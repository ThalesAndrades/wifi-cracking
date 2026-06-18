#!/usr/bin/env python3

# /agents/utils/tools/web_request_framework.py
# Generic HTTP request helpers for the KaliGPT AI agent.
#
# These are dual-use "Core" tools: they let the agent fetch arbitrary URLs and
# inspect the response. Because that is an SSRF primitive when exposed to a
# model, both helpers require an explicit authorized=True flag and refuse to
# target loopback / private / link-local / reserved addresses. They return the
# same kind of structured dict the rest of the toolset uses.


import ipaddress
import socket

import requests

from urllib.parse import urlparse

# Cap how much body text we hand back to the model, to keep responses bounded
# and avoid materialising huge downloads into memory.
_MAX_BODY_CHARS = 20000
_CHUNK = 8192

_AUTH_REQUIRED = (
    "Refused: pass authorized=True to make outbound web requests (this is a "
    "dual-use SSRF-capable primitive). See the project DISCLAIMER."
)


def _refused(extra: dict) -> dict:
    """Build a uniform refusal result for an unauthorized invocation."""
    result = {"success": False, "authorized": False, "error": _AUTH_REQUIRED}
    result.update(extra)
    return result


def _validate_public_url(url: str) -> str | None:
    """
    Return an error string if the URL is unsafe to fetch, else None.

    Rejects non-http(s) schemes and any host that resolves to a loopback,
    private, link-local, reserved or multicast address (SSRF guard).
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return "Only http/https URLs are allowed"
    host = parsed.hostname
    if not host:
        return "Invalid URL: missing host"
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        return f"Could not resolve host: {exc}"
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_loopback or ip.is_private or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return f"Refused: {ip} is not a public address (SSRF guard)"
    return None


def _bounded_body(response) -> str:
    """Read a streamed response body up to _MAX_BODY_CHARS without buffering it all."""
    parts, seen = [], 0
    for chunk in response.iter_content(chunk_size=_CHUNK, decode_unicode=True):
        if not chunk:
            continue
        seen += len(chunk)
        if seen >= _MAX_BODY_CHARS:
            parts.append(chunk[: max(0, _MAX_BODY_CHARS - (seen - len(chunk)))])
            break
        parts.append(chunk)
    return "".join(parts)


def web_request_analysis(url: str, method: str = "GET", timeout: int = 15,
                         authorized: bool = False) -> dict:
    """
    Fetch a URL and return a structured analysis (status, headers, body preview).

    Args:
        url (str): The URL to request (public http/https hosts only).
        method (str): HTTP method to use, e.g. "GET" or "HEAD". (default = "GET")
        timeout (int): Max seconds to wait for the response. (default = 15)
        authorized (bool): Must be True to make the outbound request.

    Returns:
        dict -> {success, status_code, headers, content_type, body, error}
    """
    base = {"status_code": None, "headers": None, "content_type": None, "body": None}
    if authorized is not True:
        return _refused(base)
    blocked = _validate_public_url(url)
    if blocked:
        return {"success": False, "error": blocked, **base}
    try:
        response = requests.request(
            method.upper(), url, timeout=timeout,
            headers={"User-Agent": "KaliGPT-WebRequest/1.0"},
            stream=True,
        )
    except requests.RequestException as exc:
        return {"success": False, "error": str(exc), **base}

    return {
        "success": response.ok,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content_type": response.headers.get("Content-Type"),
        "body": _bounded_body(response),
        "error": None,
    }


def get_raw_response(url: str, timeout: int = 15, authorized: bool = False) -> dict:
    """
    Fetch a URL and return the (bounded) raw response body and status.

    Args:
        url (str): The URL to request (public http/https hosts only).
        timeout (int): Max seconds to wait for the response. (default = 15)
        authorized (bool): Must be True to make the outbound request.

    Returns:
        dict -> {success, status_code, body, error}
    """
    base = {"status_code": None, "body": None}
    if authorized is not True:
        return _refused(base)
    blocked = _validate_public_url(url)
    if blocked:
        return {"success": False, "error": blocked, **base}
    try:
        response = requests.get(
            url, timeout=timeout,
            headers={"User-Agent": "KaliGPT-WebRequest/1.0"},
            stream=True,
        )
    except requests.RequestException as exc:
        return {"success": False, "error": str(exc), **base}

    return {
        "success": response.ok,
        "status_code": response.status_code,
        "body": _bounded_body(response),
        "error": None,
    }
