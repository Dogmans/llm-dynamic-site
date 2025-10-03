# LLM-Driven Dynamic Website Prototype Specification

## Overview
This specification outlines a **purely LLM-driven**, cache-enabled dynamic website architecture where AI autonomously discovers, processes, and renders content. The system has NO fallback mechanisms - it is 100% dependent on LLM functionality. The LLM (via SmolAgents) handles everything from content discovery to layout application to HTML generation. Pages are cached in Memcached for performance, but if the LLM fails, the system returns HTTP 503 Service Unavailable rather than degrading to template-based rendering.

---

## Architecture Components

### 1. FastAPI Application
- Serves all incoming HTTP requests with minimal routing logic.
- Checks Memcached cache for requested URL.
- On cache hit: returns HTML immediately.
- On cache miss: delegates everything to LLM for autonomous content discovery and generation.
- **No fallback mechanisms**: If LLM fails, returns HTTP 503 Service Unavailable.
- No explicit URL mapping - LLM discovers appropriate content files.
- Optional: Background rebuild for stale pages.

### 2. Memcached Cache
- Stores generated HTML keyed by URL path.
- Default TTL: 1 hour for cached pages.
- Handles cache invalidation when explicit rebuild triggers occur.

### 3. LLM Agent (SmolAgents) - **PURE LLM MODE**
- **Content Discovery**: Explores file system to find relevant content for requested URL
- **File Processing**: Reads and parses Markdown files with YAML frontmatter
- **Layout Application**: Discovers and applies layout specifications autonomously
- **HTML Generation**: Outputs complete, valid HTML with embedded CSS
- **Error Handling**: Generates helpful pages when content is missing (still as HTML)
- **Self-Contained**: Requires only URL path input, handles everything else internally
- **No Fallbacks**: System fails gracefully by returning None if LLM cannot generate content

### 4. Markdown Repository
- Structure:
  ```
  /site-content
      /pages
          about.md
          contact.md
          products/
              index.md
              productA.md
              productB.md
      /layouts
          default.md
          product.md
  ```
- Each `.md` file contains:
  - YAML frontmatter:
    ```yaml
    title: "Page Title"
    layout: "default"  # optional, specifies template/layout
    expires_at: "2025-10-04T12:00:00Z"  # optional
    ```
  - Markdown content for the page.

### 5. LLM-First Generation Flow
1. User requests `/some-url/`.
2. FastAPI checks Memcached cache for `/some-url/`.
   - Hit: return cached HTML.
   - Miss: continue.
3. **LLM Autonomous Processing**:
   - LLM receives URL path and content directory structure
   - LLM explores file system to find relevant content
   - LLM reads and parses Markdown + frontmatter
   - LLM discovers and applies appropriate layout
   - LLM generates complete HTML with embedded CSS
4. Store generated HTML in Memcached with key `/some-url/` (1-hour TTL).
5. Return HTML to client.

**Key Advantage**: No explicit parsing or mapping logic needed - LLM handles everything!

### 6. Explicit Rebuild Triggers
- Possible triggers:
  - Updating frontmatter `expires_at` or content in Markdown file.
  - Administrative API endpoint (`POST /rebuild?url=/some-url/`) that forces regeneration.
- On rebuild trigger:
  1. Invalidate Memcached cache.
  2. Invoke LLM agent to regenerate HTML.
  3. Update Memcached cache.

### 7. Optional Enhancements
- Background regeneration (stale-while-revalidate) to reduce user latency.
- Logging of LLM outputs and rendering errors.
- Integration with a CDN for hot HTML pages (later phase).
- Embeddings-based search for URLs not directly mapped to Markdown.

### 8. Directory Structure
```
/site-content          # Markdown source files (LLM discovers autonomously)
    /pages             # Individual pages
    /layouts           # Layout templates
/app                   # Simplified FastAPI application
    main.py            # FastAPI routing (minimal logic)
    renderer.py        # LLM autonomous site generator
    cache.py           # Memcached handler
/tests                 # Unit/integration tests
```

**Simplified Architecture**: Removed parser.py and watcher.py - LLM handles content discovery and processing autonomously.

### 9. Technical Stack
- **FastAPI** for HTTP server and minimal routing.
- **Memcached** for caching HTML output (1-hour default TTL).
- **SmolAgents** as autonomous LLM backend with local HuggingFace Transformers model.
- **pymemcache** for Memcached client.

**Removed Dependencies** (LLM handles these internally):
- ~~Python-Markdown~~ (LLM processes Markdown)
- ~~PyYAML~~ (LLM parses frontmatter)
- ~~Content Parser~~ (LLM discovers content)

### 10. API Endpoints
- `GET /{path}`: Fetch page HTML (cache-first, generate if needed).
- `POST /rebuild?url=/{path}`: Explicitly regenerate HTML for a URL.
- Optional admin endpoints for cache management, logs, metrics.

### 11. Rendering Guidelines
- LLM outputs **full HTML** including `<!DOCTYPE html>`, `<head>`, `<body>`.
- Layouts defined in `/layouts/*.md` are Markdown files with styling instructions that guide LLM on HTML structure and CSS.
- Markdown content plus frontmatter and selected layout passed to LLM.
- Directory-aware URL mapping supports index files and nested paths.
- Ensure accessibility standards and minimal HTML errors.

### 12. Development Notes
- Modularize: keep FastAPI routes, cache logic, and LLM rendering separate.
- Implement unit tests for cache behavior, rebuild triggers, and rendering.
- Logging for debugging LLM outputs.
- Use async FastAPI where possible for high concurrency.

---

## Next Steps for Prototyping
1. Set up FastAPI skeleton with GET endpoint.
2. Connect Redis and implement cache check.
3. Implement Markdown parser with frontmatter extraction.
4. Integrate SmolAgents LLM call to generate HTML.
5. Store generated HTML in Redis.
6. Implement optional rebuild trigger endpoint.
7. Test end-to-end with sample Markdown pages.
8. Iterate with logging and background rebuild enhancements.

