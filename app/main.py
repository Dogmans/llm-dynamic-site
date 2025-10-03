"""
Main FastAPI application for the LLM Dynamic Site.

This module implements the cache-first architecture with directory-aware
URL mapping and LLM-powered HTML generation.
"""

import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .cache import cache_manager
from .renderer import site_generator
from .config import API_CONFIG, CORS_CONFIG, LOG_FORMAT, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app using config
app = FastAPI(**API_CONFIG)

# Add CORS middleware using config
app.add_middleware(
    CORSMiddleware,
    **CORS_CONFIG
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting LLM Dynamic Site...")
    
    # Test cache connection and log backend being used
    try:
        stats = cache_manager.get_stats()
        backend = stats.get('backend', 'unknown')
        logger.info(f"Cache initialized using {backend} backend")
    except Exception as e:
        logger.warning(f"Cache initialization issue: {e}")
    
    logger.info("LLM Dynamic Site startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down LLM Dynamic Site...")
    # No explicit cleanup needed for Redis/memory cache


@app.get("/", response_class=HTMLResponse)
@app.get("/{path:path}/", response_class=HTMLResponse)
async def serve_page(path: str = ""):
    """
    Serve HTML pages with cache-first architecture.
    
    This endpoint handles all page requests using directory-aware URL mapping:
    - /about/ -> about.md
    - /products/ -> products/index.md  
    - /products/item1/ -> products/item1.md
    """
    try:
        # Normalize path
        url_path = f"/{path.strip('/')}/" if path else "/"
        
        logger.info(f"Serving page request: {url_path}")
        
        # 1. Check cache first
        cached_html = cache_manager.get(url_path)
        if cached_html:
            logger.info(f"Cache hit for {url_path}")
            return HTMLResponse(content=cached_html)
        
        # 2. Cache miss - generate HTML with LLM
        logger.info(f"Cache miss for {url_path} - generating HTML with LLM")
        
        # Generate HTML using autonomous LLM
        html = site_generator.generate_page(url_path)
        if not html:
            raise HTTPException(
                status_code=503, 
                detail=f"LLM service unavailable - cannot generate page: {url_path}"
            )
        
        # 3. Store in cache
        cache_success = cache_manager.set(url_path, html)
        if cache_success:
            logger.info(f"Cached HTML for {url_path}")
        else:
            logger.warning(f"Failed to cache HTML for {url_path}")
        
        return HTMLResponse(content=html)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving page {path}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/rebuild")
async def rebuild_page(url: str = Query(..., description="URL path to rebuild")):
    """
    Explicitly rebuild and cache a specific page.
    
    This endpoint forces regeneration of HTML for a given URL,
    invalidating any existing cache entry.
    """
    try:
        logger.info(f"Rebuild requested for: {url}")
        
        # Normalize URL
        url_path = f"/{url.strip('/')}/" if url.strip('/') else "/"
        
        # 1. Invalidate existing cache
        cache_manager.delete(url_path)
        logger.info(f"Invalidated cache for {url_path}")
        
        # 2. Generate new HTML with LLM
        html = site_generator.generate_page(url_path)
        if not html:
            raise HTTPException(
                status_code=503, 
                detail=f"LLM service unavailable - cannot generate page: {url_path}"
            )
        
        # 4. Cache the new HTML
        cache_success = cache_manager.set(url_path, html)
        
        return {
            "status": "success",
            "url": url_path,
            "cached": cache_success,
            "timestamp": datetime.now().isoformat(),
            "message": f"Successfully rebuilt page: {url_path}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebuilding page {url}: {e}")
        raise HTTPException(status_code=500, detail="Rebuild failed")


@app.get("/api/pages")
async def list_pages():
    """List all available pages."""
    try:
        # Get available pages by scanning the content directory
        pages = {}
        content_root = Path("site-content/pages")
        
        if content_root.exists():
            for md_file in content_root.rglob("*.md"):
                rel_path = md_file.relative_to(content_root)
                
                # Convert to URL path
                if rel_path.name == "index.md":
                    if len(rel_path.parts) == 1:
                        url_path = "/"
                    else:
                        url_path = "/" + "/".join(rel_path.parts[:-1]) + "/"
                else:
                    url_path = "/" + str(rel_path.with_suffix('')) + "/"
                
                pages[url_path] = str(md_file)
        
        return {
            "pages": pages,
            "count": len(pages),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing pages: {e}")
        raise HTTPException(status_code=500, detail="Failed to list pages")


@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    try:
        stats = cache_manager.get_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")


@app.post("/api/cache/flush")
async def flush_cache():
    """Flush all cached content."""
    try:
        success = cache_manager.flush_all()
        return {
            "status": "success" if success else "failed",
            "message": "Cache flushed" if success else "Failed to flush cache",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error flushing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to flush cache")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test cache connection
        cache_healthy = cache_manager.get_stats() is not None
        
        # Test content availability
        content_root = Path("site-content/pages")
        content_healthy = content_root.exists() and any(content_root.glob("*.md"))
        
        healthy = cache_healthy and content_healthy
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "cache": "ok" if cache_healthy else "error",
            "content": "ok" if content_healthy else "error",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics and backend information."""
    try:
        stats = cache_manager.get_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


def main():
    """Entry point for the application."""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)