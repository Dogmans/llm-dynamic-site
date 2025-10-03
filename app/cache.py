"""
Redis integration for HTML page caching with in-memory fallback.

This module provides a simple interface for caching generated HTML pages
using Redis with a default TTL of 1 hour. Falls back to in-memory cache
if Redis is unavailable.
"""

import logging
import time
import json
from typing import Optional

from .config import DEFAULT_CACHE_TTL, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages HTML caching using Redis with in-memory fallback."""
    
    def __init__(self, host: str = REDIS_HOST, port: int = REDIS_PORT, db: int = REDIS_DB, 
                 password: Optional[str] = REDIS_PASSWORD, default_ttl: int = DEFAULT_CACHE_TTL):
        """
        Initialize the cache manager.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            default_ttl: Default time-to-live for cached items in seconds (default: 1 hour)
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.default_ttl = default_ttl
        self._redis_client = None
        self._use_redis = False
        self._memory_cache = {}  # Fallback in-memory cache: {key: (value, expiry_time)}
        
        # Try to initialize Redis connection
        self._initialize_redis()
        
    def _initialize_redis(self):
        """Initialize Redis connection, fallback to in-memory if Redis unavailable."""
        try:
            import redis
            self._redis_client = redis.Redis(
                host=self.host, 
                port=self.port, 
                db=self.db, 
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self._redis_client.ping()
            self._use_redis = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}), using in-memory cache fallback")
            self._use_redis = False
    
    def _normalize_key(self, key: str) -> str:
        """
        Normalize cache key to ensure consistency.
        
        Args:
            key: Raw key (usually URL path)
            
        Returns:
            Normalized cache key
        """
        # Remove leading/trailing slashes and replace remaining slashes with underscores
        normalized = key.strip('/').replace('/', '_')
        return f"llm_site:{normalized}" if normalized else "llm_site:home"
    
    def _cleanup_memory_cache(self):
        """Remove expired entries from in-memory cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (value, expiry) in self._memory_cache.items()
            if current_time >= expiry
        ]
        for key in expired_keys:
            del self._memory_cache[key]
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve cached HTML content by URL path.
        
        Args:
            key: URL path to retrieve cached content for
            
        Returns:
            Cached HTML content or None if not found/expired
        """
        normalized_key = self._normalize_key(key)
        
        if self._use_redis:
            try:
                content = self._redis_client.get(normalized_key)
                if content:
                    logger.debug(f"Redis cache hit for key: {normalized_key}")
                    return content
                else:
                    logger.debug(f"Redis cache miss for key: {normalized_key}")
                    return None
            except Exception as e:
                logger.error(f"Redis get error for key {normalized_key}: {e}")
                # Fall back to memory cache on Redis error
                self._use_redis = False
        
        # Use in-memory cache (fallback or primary if Redis unavailable)
        self._cleanup_memory_cache()
        if normalized_key in self._memory_cache:
            content, expiry = self._memory_cache[normalized_key]
            if time.time() < expiry:
                logger.debug(f"Memory cache hit for key: {normalized_key}")
                return content
            else:
                # Expired
                del self._memory_cache[normalized_key]
        
        logger.debug(f"Memory cache miss for key: {normalized_key}")
        return None
    
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Store HTML content in cache with TTL.
        
        Args:
            key: URL path to cache content for
            value: HTML content to cache
            ttl: Time-to-live in seconds (defaults to default_ttl)
            
        Returns:
            True if successfully cached, False otherwise
        """
        normalized_key = self._normalize_key(key)
        cache_ttl = ttl if ttl is not None else self.default_ttl
        
        if self._use_redis:
            try:
                result = self._redis_client.setex(normalized_key, cache_ttl, value)
                if result:
                    logger.debug(f"Redis cache set for key: {normalized_key} (TTL: {cache_ttl}s)")
                    return True
            except Exception as e:
                logger.error(f"Redis set error for key {normalized_key}: {e}")
                # Fall back to memory cache on Redis error
                self._use_redis = False
        
        # Use in-memory cache (fallback or primary if Redis unavailable)
        expiry_time = time.time() + cache_ttl
        self._memory_cache[normalized_key] = (value, expiry_time)
        logger.debug(f"Memory cache set for key: {normalized_key} (TTL: {cache_ttl}s)")
        
        # Periodic cleanup of memory cache
        if len(self._memory_cache) % 10 == 0:  # Cleanup every 10 insertions
            self._cleanup_memory_cache()
        
        return True
    
    def delete(self, key: str) -> bool:
        """
        Remove cached content for a specific URL path.
        
        Args:
            key: URL path to remove from cache
            
        Returns:
            True if successfully deleted, False otherwise
        """
        normalized_key = self._normalize_key(key)
        success = False
        
        if self._use_redis:
            try:
                deleted = self._redis_client.delete(normalized_key)
                if deleted:
                    logger.debug(f"Redis cache deleted for key: {normalized_key}")
                success = True
            except Exception as e:
                logger.error(f"Redis delete error for key {normalized_key}: {e}")
                # Fall back to memory cache on Redis error
                self._use_redis = False
        
        # Also remove from memory cache
        if normalized_key in self._memory_cache:
            del self._memory_cache[normalized_key]
            logger.debug(f"Memory cache deleted for key: {normalized_key}")
            success = True
        
        return success
    
    def clear(self) -> bool:
        """
        Clear all cached content.
        
        Returns:
            True if successfully cleared, False otherwise
        """
        success = False
        
        if self._use_redis:
            try:
                # Delete all keys with our prefix
                keys = self._redis_client.keys("llm_site:*")
                if keys:
                    deleted = self._redis_client.delete(*keys)
                    logger.info(f"Redis cache cleared: {deleted} keys deleted")
                success = True
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
                # Fall back to memory cache on Redis error
                self._use_redis = False
        
        # Also clear memory cache
        cleared_count = len(self._memory_cache)
        self._memory_cache.clear()
        logger.info(f"Memory cache cleared: {cleared_count} keys deleted")
        success = True
        
        return success
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            "backend": "redis" if self._use_redis else "memory",
            "redis_connected": self._use_redis,
            "memory_cache_size": len(self._memory_cache),
        }
        
        if self._use_redis:
            try:
                info = self._redis_client.info()
                stats.update({
                    "redis_memory_used": info.get("used_memory_human", "unknown"),
                    "redis_connected_clients": info.get("connected_clients", 0),
                    "redis_total_commands": info.get("total_commands_processed", 0)
                })
            except Exception as e:
                logger.error(f"Redis stats error: {e}")
                stats["redis_stats_error"] = str(e)
        
        return stats


# Global cache manager instance
cache_manager = CacheManager()