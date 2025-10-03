"""
LLM-powered website generator using SmolAgents.

This module uses SmolAgents with a local HuggingFace model to autonomously
discover content, process Markdown files, and generate complete HTML pages.
"""

import logging
from typing import Optional
import os
from pathlib import Path

from .config import (
    DEFAULT_MODEL_NAME,
    OLLAMA_MODEL_ID, 
    DEFAULT_CONTENT_ROOT,
    SYSTEM_PROMPT,
    PAGE_GENERATION_PROMPT_TEMPLATE,
    REQUIRED_HTML_TAGS,
    MARKDOWN_FILE_EXTENSIONS,
    HTML_CONFIG
)

logger = logging.getLogger(__name__)


class LLMSiteGenerator:
    """Fully LLM-driven website generator that handles content discovery and HTML generation."""
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, content_root: str = DEFAULT_CONTENT_ROOT):
        """
        Initialize the LLM site generator.
        
        Args:
            model_name: HuggingFace model name for HTML generation
            content_root: Root directory for site content
        """
        self.model_name = model_name
        self.content_root = Path(content_root)
        self._agent = None
        
        logger.info(f"LLM Site Generator initialized with content root: {self.content_root}")
    
    def _get_agent(self):
        """Get or create the SmolAgents instance."""
        if self._agent is None:
            try:
                # Import here to avoid errors if smolagents not installed
                from smolagents import CodeAgent, LiteLLMModel
                
                model = LiteLLMModel(model_id=OLLAMA_MODEL_ID)  # Using Ollama as fallback
                
                self._agent = CodeAgent(
                    model=model,
                    tools=[],
                    system_prompt=SYSTEM_PROMPT
                )
                
                logger.info(f"Initialized LLM site generator with model: {self.model_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize LLM agent: {e}")
                self._agent = None
                
        return self._agent
    
    def generate_page(self, url_path: str) -> Optional[str]:
        """
        Generate complete HTML page for the given URL path using LLM.
        
        The LLM will autonomously:
        1. Discover the appropriate content file(s)
        2. Process Markdown and frontmatter
        3. Apply layout specifications
        4. Generate complete HTML
        
        Args:
            url_path: URL path (e.g., "/about/", "/products/item1/")
            
        Returns:
            Complete HTML string or None if generation failed
        """
        try:
            # Pure LLM-based autonomous generation
            html = self._generate_with_llm(url_path)
            
            if html and self.validate_html(html):
                logger.info(f"Successfully generated HTML with LLM for: {url_path}")
                return html
            
            logger.error(f"LLM generation failed for {url_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating HTML for {url_path}: {e}")
            return None
    
    def _generate_with_llm(self, url_path: str) -> Optional[str]:
        """Generate HTML using LLM autonomous processing."""
        try:
            agent = self._get_agent()
            if not agent:
                logger.error("LLM agent not available - cannot generate page")
                return None
            
            # Get file structure for the LLM to work with
            file_structure = self._get_file_structure()
            
            # Create comprehensive prompt for autonomous generation using template
            prompt = PAGE_GENERATION_PROMPT_TEMPLATE.format(
                url_path=url_path,
                file_structure=file_structure,
                content_root=self.content_root
            )
            
            # Get HTML from the agent
            result = agent.run(prompt)
            
            # Extract HTML from the result
            if isinstance(result, str):
                return self._clean_html_response(result)
            
            return None
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None
    

    

    
    def _get_file_structure(self) -> str:
        """Get a text representation of the content file structure."""
        try:
            structure = []
            
            if self.content_root.exists():
                for root, dirs, files in os.walk(self.content_root):
                    level = root.replace(str(self.content_root), '').count(os.sep)
                    indent = '  ' * level
                    structure.append(f"{indent}{os.path.basename(root)}/")
                    
                    sub_indent = '  ' * (level + 1)
                    for file in files:
                        if any(file.endswith(ext) for ext in MARKDOWN_FILE_EXTENSIONS):
                            structure.append(f"{sub_indent}{file}")
            
            return '\n'.join(structure)
        except Exception as e:
            logger.error(f"Error getting file structure: {e}")
            return "Error reading file structure"
    

    
    def _clean_html_response(self, response: str) -> str:
        """Clean and validate LLM HTML response."""
        if not HTML_CONFIG["clean_response"]:
            return response.strip()
            
        # Remove any markdown code blocks if present
        if HTML_CONFIG["remove_code_blocks"]:
            if "```html" in response:
                response = response.split("```html")[1].split("```")[0].strip()
            elif "```" in response:
                parts = response.split("```")
                if len(parts) >= 3:
                    response = parts[1].strip()
        
        # Ensure it starts with DOCTYPE
        if HTML_CONFIG["require_doctype"] and not response.strip().startswith("<!DOCTYPE"):
            logger.warning("LLM response missing DOCTYPE, may be incomplete")
        
        return response.strip()
    
    def validate_html(self, html: str) -> bool:
        """
        Basic HTML validation.
        
        Args:
            html: HTML string to validate
            
        Returns:
            True if HTML appears valid, False otherwise
        """
        try:
            if not HTML_CONFIG["validate_structure"]:
                return True
                
            # Basic checks for valid HTML structure
            return all(tag in html.lower() for tag in REQUIRED_HTML_TAGS)
        except Exception as e:
            logger.error(f"HTML validation error: {e}")
            return False
    



# Global LLM site generator instance
site_generator = LLMSiteGenerator()