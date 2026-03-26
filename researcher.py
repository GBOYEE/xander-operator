#!/usr/bin/env python3
"""
Researcher Agent — Independent web search + optional deep browse.
Uses DuckDuckGo (no API key) for search, Playwright for optional page fetch.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
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

WORKSPACE = Path("/root/.openclaw/workspace")

def research(query: str, max_results: int = 5, follow_up_browse: bool = False) -> Dict[str, Any]:
    """
    Perform web research using DuckDuckGo, optionally browse first result.
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
        # Construct a simple answer from snippets
        answer = "\n\n".join([r.get("body", "") for r in results[:3]])
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
    test_q = "AI automation trends 2024"
    out = research(test_q, max_results=3, follow_up_browse=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))
