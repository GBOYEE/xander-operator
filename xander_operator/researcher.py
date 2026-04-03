#!/usr/bin/env python3
"""
Researcher Agent — Independent web search + optional deep browse, with LLM synthesis.
Uses DuckDuckGo (no API key) for search, Playwright for optional page fetch,
and an LLM (OpenAI/Ollama) to generate a concise answer.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Optional LLM integration
try:
    from xander_operator.llm import generate_response
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

WORKSPACE = Path("/root/.openclaw/workspace")
log = logging.getLogger(__name__)

def research(
    query: str,
    max_results: int = 5,
    follow_up_browse: bool = False,
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Perform web research using DuckDuckGo, optionally browse first result,
    and synthesize an answer using an LLM if available.

    Returns structured result.
    """
    if not SEARCH_AVAILABLE:
        return {
            "success": False,
            "query": query,
            "answer": "duckduckgo_search library not installed",
            "sources": []
        }

    # Step 1: search
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            raise ValueError("No search results")
        sources = [{"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")} for r in results]
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "answer": f"search failed: {str(e)}",
            "sources": []
        }

    # Step 2 (optional): browse first URL to get raw page text
    first_page_text = None
    if follow_up_browse and sources and PLAYWRIGHT_AVAILABLE:
        first_url = sources[0]["url"]
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(first_url, timeout=30000)
                first_page_text = page.inner_text("body")[:3000]
                browser.close()
        except Exception as e:
            first_page_text = f"browse error: {str(e)}"
            log.warning(f"Browse failed during research: {e}")

    # Step 3: LLM synthesis or fallback
    answer = ""
    if use_llm and LLM_AVAILABLE:
        # Build prompt
        prompt_parts = [f"Query: {query}\n\n"]
        for idx, src in enumerate(sources, 1):
            prompt_parts.append(f"Source {idx}: {src['title']} ({src['url']})\nSnippet: {src['snippet']}\n\n")
        if first_page_text:
            prompt_parts.append(f"Additional context from first page:\n{first_page_text[:1500]}\n\n")
        prompt_parts.append("Based on the above, provide a clear, concise answer to the query. Cite sources by number.")
        prompt = "".join(prompt_parts)
        # Use model from environment (XANDER_MODEL or OPENAI_MODEL) for routing flexibility
        llm_answer = generate_response(prompt, max_tokens=1000)
        if llm_answer:
            answer = llm_answer
        else:
            log.warning("LLM synthesis failed, falling back to snippet concatenation")
            answer = "\n\n".join([r.get("body", "") for r in results[:3]])
    else:
        # Fallback: concatenate top snippets
        answer = "\n\n".join([r.get("body", "") for r in results[:3]])

    result = {
        "success": True,
        "query": query,
        "answer": answer,
        "sources": sources,
        "first_page_text": first_page_text,
        "timestamp": datetime.now().isoformat()
    }
    return result

# Standalone test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_q = "AI automation trends 2024"
    out = research(test_q, max_results=3, follow_up_browse=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))
