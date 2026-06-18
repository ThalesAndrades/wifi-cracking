# KaliGPT Arsenal — Material Package

Snapshot of the agent tool arsenal work (branch: claude/desktop-tools-improvement-41gqy7, PR #1).

## Contents
- agents/utils/tools/        — the 29 tool wrappers + shared runner + registry
    - _runner.py             — validation, run_command, uniform result schema, logging
    - __init__.py            — TOOL_CATEGORIES (single source of truth) + accessors
    - locals.py              — execute_generic_linux_command (shell/timeout) + scraping
    - kali_recon.py          — nmap, dns_recon, dnsx, subdomains, whois, searchsploit
    - kali_web.py            — whatweb, httpx, katana, ffuf, nuclei, nikto, wpscan
    - kali_network.py        — sslscan (tls_audit), masscan, naabu
    - kali_secrets.py        — trufflehog, gitleaks
    - kali_offensive.py      — hash_identify + gated sqlmap/hydra/hashcat
- agents/utils/agent_management.py — grouped /list tools display
- .claude/skills/kali-arsenal/SKILL.md — conventions for extending the arsenal
- docs/ARSENAL.md            — architecture & full tool catalogue
- docs/AI_SECURITY.md        — modern offensive tech + LLM threat landscape (defensive)
- requirements/globals.md    — requirements & tool documentation
- requirements/dev-requirements.txt — pytest
- .github/workflows/desktop_tools_dispatch.yml — manual-dispatch provisioning workflow
- tests/                     — 33-test pytest suite (runner, gate, parsers, registry)

## Run the tests
    pip install -r requirements/dev-requirements.txt
    pytest -q

## Status
29 tools, 33 tests passing, CI actions SHA-pinned, dual-use tools gated.
