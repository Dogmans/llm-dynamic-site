# LLM Dynamic Site

A FastAPI-based, cache-first, dynamic website architecture using LLMs to render content from Markdown files.

## Features

- Cache-first architecture with Memcached
- LLM-powered HTML generation from Markdown
- Directory-aware URL mapping
- Frontmatter support for page metadata
- Markdown-based layout system
- Explicit rebuild API

## Setup

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -e .
```

3. Start Memcached (required):
```bash
# Install and start memcached on your system
# Windows: Download from https://memcached.org/downloads
# Linux: sudo apt-get install memcached && systemctl start memcached
# Mac: brew install memcached && brew services start memcached
```

4. Run the application:
```bash
fastapi dev app/main.py
```

## Usage

- Visit `http://localhost:8000/about/` for sample pages
- Use `POST /rebuild?url=/about/` to regenerate specific pages
- Pages are cached for 1 hour by default

## Project Structure

```
app/                    # FastAPI application
site-content/
  pages/               # Markdown source files
    products/          # Nested page structure
    blog/
  layouts/             # Markdown-based layout templates
documentation/         # Project documentation
tests/                 # Unit tests
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black .
isort .
```