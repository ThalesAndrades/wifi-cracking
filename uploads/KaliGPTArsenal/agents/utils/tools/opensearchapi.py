#!/usr/bin/env python3

# /agents/utils/tools/opensearchapi.py
# Thin client for the optional OpenSearchAPI retrieval backend.
#
# The backend (provisioned separately by the CI workflow / runtime setup) exposes
# a small HTTP API used for keyword search and RAG-style retrieval. Its base URL
# is taken from the OPENSEARCHAPI_URL environment variable. When the backend is
# not configured or not reachable, every call returns a structured "not
# available" result instead of raising, so the agent degrades gracefully.


import os

import requests

_DEFAULT_URL = "http://127.0.0.1:8080"


def _base_url() -> str:
    """Return the configured OpenSearchAPI base URL (env override, else default)."""
    return os.environ.get("OPENSEARCHAPI_URL", _DEFAULT_URL).rstrip("/")


def check_search_connection(timeout: int = 5) -> dict:
    """
    Check whether the OpenSearchAPI retrieval backend is reachable.

    Args:
        timeout (int): Max seconds to wait for the health check. (default = 5)

    Returns:
        dict -> {success, connected, url, error}
    """
    url = f"{_base_url()}/health"
    try:
        response = requests.get(url, timeout=timeout)
    except requests.RequestException as exc:
        return {"success": False, "connected": False, "url": url, "error": str(exc)}
    return {"success": response.ok, "connected": response.ok, "url": url, "error": None}


def keyword_search(query: str, top_k: int = 5, timeout: int = 15) -> dict:
    """
    Run a keyword search against the OpenSearchAPI backend.

    Args:
        query (str): The search query string.
        top_k (int): Maximum number of results to return. (default = 5)
        timeout (int): Max seconds to wait. (default = 15)

    Returns:
        dict -> {success, results, error}
    """
    return _post("/search", {"query": query, "top_k": top_k}, "results", timeout)


def search_as_RAG(query: str, top_k: int = 5, timeout: int = 30) -> dict:
    """
    Retrieve context for a query in a RAG-friendly form from OpenSearchAPI.

    Args:
        query (str): The question / query to retrieve context for.
        top_k (int): Maximum number of context passages to return. (default = 5)
        timeout (int): Max seconds to wait. (default = 30)

    Returns:
        dict -> {success, context, error}
    """
    return _post("/rag", {"query": query, "top_k": top_k}, "context", timeout)


def _post(path: str, payload: dict, key: str, timeout: int) -> dict:
    """Shared POST helper returning a uniform {success, <key>, error} dict."""
    url = f"{_base_url()}{path}"
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        return {"success": False, key: None, "error": str(exc)}
    if not response.ok:
        return {"success": False, key: None, "error": f"HTTP {response.status_code}"}
    try:
        data = response.json()
    except ValueError as exc:
        return {"success": False, key: None, "error": f"Invalid JSON: {exc}"}
    return {"success": True, key: data.get(key, data), "error": None}
