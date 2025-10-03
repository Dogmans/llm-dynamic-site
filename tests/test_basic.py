"""
Basic tests for the LLM Dynamic Site.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Test cache manager
def test_cache_manager_initialization():
    """Test cache manager can be initialized."""
    from app.cache import CacheManager
    
    cache = CacheManager()
    assert cache.host == "localhost"
    assert cache.port == 11211
    assert cache.default_ttl == 3600


def test_cache_key_normalization():
    """Test cache key normalization."""
    from app.cache import CacheManager
    
    cache = CacheManager()
    
    # Test normal key
    normalized = cache._normalize_key("/about/")
    assert normalized == "llm_site:/about/"
    
    # Test key with spaces
    normalized = cache._normalize_key("/about page/")
    assert normalized == "llm_site:/about_page/"
    
    # Test very long key
    long_key = "/" + "a" * 300
    normalized = cache._normalize_key(long_key)
    assert len(normalized) <= 250
    assert normalized.startswith("llm_site:long_key_")


# Test content parser
def test_content_parser_initialization():
    """Test content parser initialization."""
    from app.parser import ContentParser
    
    parser = ContentParser()
    assert parser.content_root == Path("site-content")
    assert parser.pages_dir == Path("site-content/pages")
    assert parser.layouts_dir == Path("site-content/layouts")


def test_url_to_file_mapping():
    """Test URL to file path mapping."""
    from app.parser import ContentParser
    
    parser = ContentParser()
    
    # Test cases (these would need actual files to work fully)
    test_cases = [
        ("about", "about.md"),
        ("products", "products/index.md"), 
        ("products/item1", "products/item1.md")
    ]
    
    for url_path, expected_suffix in test_cases:
        file_path = parser.url_to_file_path(url_path)
        # Just test the method doesn't crash for now
        # In a real test, we'd create mock files
        assert file_path is None or expected_suffix in str(file_path)


# Test HTML renderer
def test_html_renderer_initialization():
    """Test HTML renderer initialization."""
    from app.renderer import HTMLRenderer
    
    renderer = HTMLRenderer()
    assert renderer.model_name == "microsoft/DialoGPT-medium"


def test_html_validation():
    """Test HTML validation."""
    from app.renderer import HTMLRenderer
    
    renderer = HTMLRenderer()
    
    # Valid HTML
    valid_html = """<!DOCTYPE html>
<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"""
    assert renderer.validate_html(valid_html) == True
    
    # Invalid HTML
    invalid_html = "<p>Just a paragraph</p>"
    assert renderer.validate_html(invalid_html) == False


def test_template_fallback_rendering():
    """Test template fallback rendering."""
    from app.renderer import HTMLRenderer
    
    renderer = HTMLRenderer()
    
    page_content = {
        'frontmatter': {
            'title': 'Test Page',
            'description': 'A test page',
            'layout': 'default'
        },
        'content': '# Hello World\\n\\nThis is a test.',
        'html_preview': '<h1>Hello World</h1>\\n<p>This is a test.</p>'
    }
    
    layout_content = {
        'frontmatter': {'name': 'default'},
        'content': 'Default layout instructions'
    }
    
    html = renderer._render_with_template(page_content, layout_content)
    
    assert '<!DOCTYPE html>' in html
    assert 'Test Page' in html
    assert 'Hello World' in html


# Integration tests would go here
@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    # This would require setting up a test FastAPI client
    # For now, just a placeholder
    pass


if __name__ == "__main__":
    pytest.main([__file__])