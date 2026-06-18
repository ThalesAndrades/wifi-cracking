#!/usr/bin/env python3

# /agents/utils/tools/web_request_framework.py
# Generic HTTP request helpers for the KaliGPT AI agent.
#
# These are "Core" (non-Kali) tools: they let the agent fetch arbitrary URLs and
# inspect the response. They return the same kind of structured dict the rest of
# the toolset uses, so the model gets parseable data instead of raw text.


import requests

# Cap how much body text we hand back to the model, to keep responses bounded.
_MAX_BODY_CHARS = 20000


def web_request_analysis(url: str, method: str = "GET", timeout: int = 15) -> dict:
    """
    Fetch a URL and return a structured analysis (status, headers, body preview).

    Args:
        url (str): The URL to request.
        method (str): HTTP method to use, e.g. "GET" or "HEAD". (default = "GET")
        timeout (int): Max seconds to wait for the response. (default = 15)

    Returns:
        dict -> {success, status_code, headers, content_type, body, error}
    """
    try:
        response = requests.request(
            method.upper(), url, timeout=timeout,
            headers={"User-Agent": "KaliGPT-WebRequest/1.0"},
        )
    except requests.RequestException as exc:
        return {"success": False, "status_code": None, "headers": None,
                "content_type": None, "body": None, "error": str(exc)}

    body = response.text or ""
    return {
        "success": response.ok,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content_type": response.headers.get("Content-Type"),
        "body": body[:_MAX_BODY_CHARS],
        "error": None,
    }


def get_raw_response(url: str, timeout: int = 15) -> dict:
    """
    Fetch a URL and return the raw, unprocessed response body and status.

    Args:
        url (str): The URL to request.
        timeout (int): Max seconds to wait for the response. (default = 15)

    Returns:
        dict -> {success, status_code, body, error}
    """
    try:
        response = requests.get(
            url, timeout=timeout,
            headers={"User-Agent": "KaliGPT-WebRequest/1.0"},
        )
    except requests.RequestException as exc:
        return {"success": False, "status_code": None, "body": None, "error": str(exc)}

    return {
        "success": response.ok,
        "status_code": response.status_code,
        "body": response.text,
        "error": None,
    }
