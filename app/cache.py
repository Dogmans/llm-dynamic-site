"""
Memcached integration for HTML page caching.

This module provides a simple interface for caching generated HTML pages
using Memcached with a default TTL of 1 hour.
"""

import logging
from typing import Optional

from pymemcache.client.base import Client
from pymemcache.exceptions import MemcacheError

from .config import DEFAULT_CACHE_TTL

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages HTML caching using Memcached."""
    
    def __init__(self, host: str = "localhost", port: int = 11211, default_ttl: int = DEFAULT_CACHE_TTL):
        """
        Initialize the cache manager.
        
        Args:
            host: Memcached server host
            port: Memcached server port  
            default_ttl: Default time-to-live for cached items in seconds (default: 1 hour)
        """
        self.host = host
        self.port = port
        self.default_ttl = default_ttl
        self._client: Optional[Client] = None
        
    def _get_client(self) -> Client:
        """Get or create Memcached client connection."""
        if self._client is None:
            try:
                self._client = Client((self.host, self.port))
                # Test connection
                self._client.version()
                logger.info(f"Connected to Memcached at {self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to connect to Memcached: {e}")
                raise
        return self._client
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve cached HTML content by URL path.
        
        Args:
            key: URL path (e.g., "/about/", "/products/index/")
            
        Returns:
            Cached HTML content if found, None otherwise
        """
        try:
            client = self._get_client()
            cached_content = client.get(self._normalize_key(key))
            
            if cached_content:
                logger.info(f"Cache hit for key: {key}")
                return cached_content.decode('utf-8')
            else:
                logger.info(f"Cache miss for key: {key}")
                return None
                
        except MemcacheError as e:
            logger.error(f"Memcache error getting key {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting key {key}: {e}")
            return None
    
    def set(self, key: str, content: str, ttl: Optional[int] = None) -> bool:
        """
        Store HTML content in cache.
        
        Args:
            key: URL path (e.g., "/about/", "/products/index/")
            content: HTML content to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = self._get_client()
            cache_ttl = ttl or self.default_ttl
            
            success = client.set(
                self._normalize_key(key),
                content.encode('utf-8'),
                expire=cache_ttl
            )
            
            if success:
                logger.info(f"Cached content for key: {key} (TTL: {cache_ttl}s)")
            else:
                logger.warning(f"Failed to cache content for key: {key}")
                
            return success
            
        except MemcacheError as e:
            logger.error(f"Memcache error setting key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Remove item from cache.
        
        Args:
            key: URL path to remove from cache
            
        Returns:
            True if item was deleted, False otherwise
        """
        try:
            client = self._get_client()
            success = client.delete(self._normalize_key(key))
            
            if success:
                logger.info(f"Deleted cache entry for key: {key}")
            else:
                logger.info(f"No cache entry found for key: {key}")
                
            return success
            
        except MemcacheError as e:
            logger.error(f"Memcache error deleting key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting key {key}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all cached content.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            client = self._get_client()
            success = client.flush_all()
            
            if success:
                logger.info("Flushed all cache entries")
            else:
                logger.warning("Failed to flush cache")
                
            return success
            
        except MemcacheError as e:
            logger.error(f"Memcache error flushing cache: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error flushing cache: {e}")
            return False
    
    def _normalize_key(self, key: str) -> str:
        """
        Normalize cache key to ensure compatibility with Memcached.
        
        Args:
            key: Original key
            
        Returns:
            Normalized key safe for Memcached
        """
        # Ensure key starts and ends with appropriate characters
        normalized = key.strip()
        
        # Replace any problematic characters for Memcached keys
        normalized = normalized.replace(' ', '_')
        normalized = normalized.replace('\n', '_')
        normalized = normalized.replace('\r', '_')
        normalized = normalized.replace('\t', '_')
        
        # Prefix to avoid conflicts with other applications
        normalized = f"llm_site:{normalized}"
        
        # Memcached keys must be <= 250 characters
        if len(normalized) > 250:
            # Use a hash for very long keys
            import hashlib
            hash_suffix = hashlib.md5(normalized.encode()).hexdigest()[:16]
            normalized = f"llm_site:long_key_{hash_suffix}"
        
        return normalized
    
    def get_stats(self) -> Optional[dict]:
        """
        Get Memcached server statistics.
        
        Returns:
            Dictionary of server stats if successful, None otherwise
        """
        try:
            client = self._get_client()
            stats = client.stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return None
    
    def close(self):
        """Close the Memcached connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Closed Memcached connection")
            except Exception as e:
                logger.error(f"Error closing Memcached connection: {e}")
            finally:
                self._client = None


# Global cache manager instance
cache_manager = CacheManager()