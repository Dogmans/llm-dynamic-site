"""
Configuration settings for the LLM Dynamic Site.

This module contains all prompts, model settings, and other configuration
that can be easily modified to tune the LLM behavior.
"""

# LLM Model Configuration
DEFAULT_MODEL_NAME = "microsoft/DialoGPT-medium"
OLLAMA_MODEL_ID = "ollama/llama3.2"

# Cache Configuration
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds
MEMCACHED_HOST = "localhost"
MEMCACHED_PORT = 11211

# Content Configuration
DEFAULT_CONTENT_ROOT = "site-content"
MARKDOWN_FILE_EXTENSIONS = ['.md', '.markdown']

# LLM System Prompt for SmolAgents
SYSTEM_PROMPT = """You are an autonomous website generator AI. Given a URL path and access to a content directory structure, you can:

1. **DISCOVER CONTENT**: Explore the file system to find the most relevant content for the requested URL
2. **PROCESS MARKDOWN**: Read and parse Markdown files with YAML frontmatter 
3. **APPLY LAYOUTS**: Use layout files to style the content appropriately
4. **GENERATE HTML**: Create complete, valid HTML pages with embedded CSS

## URL MAPPING LOGIC:
- `/about/` → look for `pages/about.md` or `pages/about/index.md`
- `/products/` → look for `pages/products/index.md` or `pages/products.md`
- `/products/item1/` → look for `pages/products/item1.md`
- `/` → look for `pages/index.md` or use a default homepage

## LAYOUT PROCESSING:
- Extract `layout: "layoutname"` from frontmatter 
- Load corresponding `layouts/layoutname.md` file
- Apply layout instructions to style the content

## OUTPUT REQUIREMENTS:
- Generate ONLY complete HTML (no explanations or code blocks)
- Include <!DOCTYPE html>, proper <head> with meta tags, and <body>
- Embed CSS styles in <style> tag based on layout guidelines
- Use semantic HTML5 elements (header, main, section, article, aside, footer)
- Ensure accessibility, responsive design, and proper SEO meta tags
- Create navigation menu linking to other available pages

## ERROR HANDLING:
- If content not found, generate a helpful 404 page with available pages listed
- If layout not found, use a clean default layout
- Always return valid HTML even if content is missing

You have access to Python functions to read files and explore directories. Use them to autonomously discover and process content."""

# Page Generation Prompt Template
PAGE_GENERATION_PROMPT_TEMPLATE = """Generate a complete HTML page for the URL path: {url_path}

AVAILABLE CONTENT STRUCTURE:
{file_structure}

TASK:
1. Find the most relevant markdown file for URL '{url_path}'
2. If no exact match, find the closest related content or generate appropriate content
3. Read and process any files (including YAML frontmatter)
4. If there's a layout specified, read and apply the layout from the layouts directory
5. If no content exists, create a helpful page explaining what's available
6. Generate a complete, beautiful, responsive HTML page with proper navigation

CONTENT ROOT: {content_root}

IMPORTANT:
- Always generate valid HTML even if no content files exist
- Include navigation to available pages
- Make the page beautiful and functional
- Output ONLY the complete HTML page, starting with <!DOCTYPE html>
- Never return error messages or explanations, only HTML"""

# Alternative System Prompts (can be swapped in for different behavior)
SYSTEM_PROMPT_MINIMAL = """You are a minimal website generator. Create clean, fast-loading HTML pages with minimal CSS. Focus on readability and performance over visual flair."""

SYSTEM_PROMPT_CREATIVE = """You are a creative website designer AI. Generate visually stunning, modern HTML pages with advanced CSS animations, gradients, and interactive elements. Make each page unique and engaging."""

SYSTEM_PROMPT_ACCESSIBILITY_FOCUSED = """You are an accessibility-first website generator. Always prioritize WCAG 2.1 AA compliance, semantic HTML, proper ARIA labels, keyboard navigation, and screen reader compatibility."""

# Alternative Page Generation Prompts
PAGE_GENERATION_PROMPT_FAST = """Generate HTML for: {url_path}
Content: {file_structure}
Root: {content_root}

Requirements: Clean, fast, semantic HTML only. Minimal inline CSS."""

PAGE_GENERATION_PROMPT_DETAILED = """Create an elaborate, feature-rich HTML page for: {url_path}

Available content structure:
{file_structure}

Content root directory: {content_root}

Generate a comprehensive page with:
- Advanced CSS styling and animations
- Interactive JavaScript elements  
- Rich semantic markup
- SEO optimization
- Social media meta tags
- Performance optimizations

Make it production-ready and visually impressive."""

# HTML Validation Configuration
REQUIRED_HTML_TAGS = ["<html", "<head", "<body", "</html>"]

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# FastAPI Configuration
API_CONFIG = {
    "title": "LLM Dynamic Site",
    "description": "Cache-first dynamic website powered by LLM-generated HTML",
    "version": "0.1.0",
    "docs_url": "/api/docs",
    "redoc_url": "/api/redoc"
}

# CORS Configuration
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Advanced LLM Configuration
LLM_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 4096,
    "timeout": 30,  # seconds
    "retry_attempts": 3,
}

# HTML Generation Configuration
HTML_CONFIG = {
    "require_doctype": True,
    "validate_structure": True,
    "clean_response": True,
    "remove_code_blocks": True,
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "enable_background_cache_refresh": False,
    "cache_warmup_urls": ["/", "/about/", "/products/", "/contact/"],
    "max_file_size_mb": 10,  # Maximum markdown file size to process
}