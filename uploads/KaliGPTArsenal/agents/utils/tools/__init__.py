#!/usr/bin/env python3

# /agents/utils/tools/__init__.py
# Updated: 12 June 2026

from .opensearchapi import check_search_connection, search_as_RAG, keyword_search
from .locals import get_local_server_content, execute_generic_linux_command
from .web_request_framework import web_request_analysis, get_raw_response

# Kali security tool wrappers (structured output for the AI agent)
from .kali_recon import (
    nmap_scan,
    dns_recon,
    dnsx_resolve,
    subdomain_enum,
    whois_lookup,
    searchsploit_lookup,
)
from .kali_web import (
    http_fingerprint,
    httpx_probe,
    katana_crawl,
    dir_bruteforce,
    nuclei_scan,
    nikto_scan,
    wpscan,
)
from .kali_network import tls_audit, masscan_sweep, naabu_scan
from .kali_secrets import trufflehog_scan, gitleaks_scan
from .kali_offensive import (
    hash_identify,
    sqlmap_test,
    hydra_spray,
    hashcat_crack,
)


# --- SINGLE SOURCE OF TRUTH ---
# Tools grouped by category. Everything else (the flat tool list, the registry
# metadata and the /list tools display) is derived from this mapping.
TOOL_CATEGORIES = {
    "Core": [
        check_search_connection,
        keyword_search,
        search_as_RAG,
        get_local_server_content,
        execute_generic_linux_command,
        web_request_analysis,
        get_raw_response,
    ],
    "Recon / OSINT": [
        nmap_scan,
        dns_recon,
        dnsx_resolve,
        subdomain_enum,
        whois_lookup,
        searchsploit_lookup,
    ],
    "Web": [
        http_fingerprint,
        httpx_probe,
        katana_crawl,
        dir_bruteforce,
        nuclei_scan,
        nikto_scan,
        wpscan,
    ],
    "Network / TLS": [
        tls_audit,
        masscan_sweep,
        naabu_scan,
    ],
    "Secrets": [
        trufflehog_scan,
        gitleaks_scan,
    ],
    "Offensive (dual-use)": [
        hash_identify,
        sqlmap_test,
        hydra_spray,
        hashcat_crack,
    ],
}

# Dual-use tools that require an explicit authorized=True flag before they run.
DUAL_USE_TOOLS = {
    "sqlmap_test", "hydra_spray", "hashcat_crack",
    "execute_generic_linux_command",
}


def get_tools_info():
    """
    Returns a list of Python functions (tools) that the AI model can use.
    The SDK automatically converts these into FunctionDeclarations.
    """
    # The list contains the Python function objects themselves!
    return [tool for tools in TOOL_CATEGORIES.values() for tool in tools]


def _first_doc_line(tool) -> str:
    """Return the first non-empty line of a tool's docstring as its description."""
    if tool.__doc__:
        return tool.__doc__.strip().split('\n')[0]
    return "No description available."


def get_available_tools_data():
    """
    Returns a dict of tools names with brief description available for the Gemini model.
    """
    return {tool.__name__: _first_doc_line(tool) for tool in get_tools_info()}


def get_tools_metadata():
    """
    Returns richer per-tool metadata: category, dual-use flag and description.

    Returns:
        dict -> {name: {"category": str, "dual_use": bool, "description": str}}
    """
    metadata = {}
    for category, tools in TOOL_CATEGORIES.items():
        for tool in tools:
            metadata[tool.__name__] = {
                "category": category,
                "dual_use": tool.__name__ in DUAL_USE_TOOLS,
                "description": _first_doc_line(tool),
            }
    return metadata


if __name__ == "__main__":
    for category, tools in TOOL_CATEGORIES.items():
        print(f"\n{category}:")
        for tool in tools:
            flag = "  [dual-use]" if tool.__name__ in DUAL_USE_TOOLS else ""
            print(f"  ◈ {tool.__name__}{flag}: {_first_doc_line(tool)}")
