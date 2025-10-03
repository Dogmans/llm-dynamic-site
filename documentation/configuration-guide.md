# Configuration Guide

The LLM Dynamic Site uses a centralized configuration system in `app/config.py` that allows you to easily customize prompts, model settings, and behavior without modifying the core code.

## Key Configuration Areas

### 1. LLM Model Configuration
```python
DEFAULT_MODEL_NAME = "microsoft/DialoGPT-medium"
OLLAMA_MODEL_ID = "ollama/llama3.2"
```

### 2. System Prompts
The main system prompt that defines how the LLM behaves:
```python
SYSTEM_PROMPT = """You are an autonomous website generator AI..."""
```

**Alternative prompts available:**
- `SYSTEM_PROMPT_MINIMAL` - For clean, fast-loading pages
- `SYSTEM_PROMPT_CREATIVE` - For visually stunning, modern designs  
- `SYSTEM_PROMPT_ACCESSIBILITY_FOCUSED` - For WCAG 2.1 AA compliance

To use an alternative prompt, modify `app/renderer.py`:
```python
# Replace SYSTEM_PROMPT with desired alternative
from .config import SYSTEM_PROMPT_CREATIVE as SYSTEM_PROMPT
```

### 3. Page Generation Prompts
Controls how individual pages are generated:
```python
PAGE_GENERATION_PROMPT_TEMPLATE = """Generate a complete HTML page for..."""
```

**Alternatives:**
- `PAGE_GENERATION_PROMPT_FAST` - Minimal, performance-focused
- `PAGE_GENERATION_PROMPT_DETAILED` - Feature-rich, elaborate pages

### 4. Cache Configuration
```python
DEFAULT_CACHE_TTL = 3600  # 1 hour
MEMCACHED_HOST = "localhost"
MEMCACHED_PORT = 11211
```

### 5. HTML Processing Configuration
```python
HTML_CONFIG = {
    "require_doctype": True,
    "validate_structure": True,
    "clean_response": True,
    "remove_code_blocks": True,
}
```

### 6. Performance Settings
```python
PERFORMANCE_CONFIG = {
    "enable_background_cache_refresh": False,
    "cache_warmup_urls": ["/", "/about/", "/products/", "/contact/"],
    "max_file_size_mb": 10,
}
```

## Common Customizations

### Change LLM Behavior Style
Edit `SYSTEM_PROMPT` in `config.py` to change how the LLM generates content:

```python
# For minimalist sites
SYSTEM_PROMPT = SYSTEM_PROMPT_MINIMAL

# For creative, visual sites  
SYSTEM_PROMPT = SYSTEM_PROMPT_CREATIVE

# For accessibility-focused sites
SYSTEM_PROMPT = SYSTEM_PROMPT_ACCESSIBILITY_FOCUSED
```

### Adjust Cache TTL
Modify `DEFAULT_CACHE_TTL` to change how long pages are cached:

```python
DEFAULT_CACHE_TTL = 7200  # 2 hours
DEFAULT_CACHE_TTL = 300   # 5 minutes for development
```

### Customize HTML Validation
Turn off strict validation for more experimental LLM output:

```python
HTML_CONFIG = {
    "require_doctype": False,
    "validate_structure": False,
    "clean_response": True,
    "remove_code_blocks": True,
}
```

### Add Custom Prompt Variables
You can add your own configuration variables:

```python
# Custom site branding
SITE_CONFIG = {
    "site_name": "My AI Website",
    "theme_color": "#2563eb",
    "brand_voice": "professional and friendly",
}
```

Then modify the prompt template to use them:

```python
PAGE_GENERATION_PROMPT_TEMPLATE = """Generate a {brand_voice} HTML page for {site_name}...
URL: {url_path}
Theme color: {theme_color}
..."""
```

## Environment-Specific Configurations

For different environments, you can create separate config files:

- `config_dev.py` - Development settings with faster, less strict validation
- `config_prod.py` - Production settings with full validation and longer cache times
- `config_creative.py` - Creative/design-focused prompts and settings

Then modify your import in the main files:

```python
# Development
from .config_dev import *

# Production  
from .config_prod import *

# Creative mode
from .config_creative import *
```

This approach makes the LLM behavior highly configurable while keeping the core logic unchanged!