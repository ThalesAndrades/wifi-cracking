[//]: # ( /docs/ARSENAL.md )
[//]: # ( KaliGPT agent tool arsenal — architecture & reference )
[//]: # ( Updated: 12 June 2026 )

# KaliGPT Agent Arsenal

The **arsenal** is the set of tools the KaliGPT AI agent can call during a
session. It turns natural-language intent ("scan this host", "what CMS is this
site running") into safe, structured tool invocations the model can reason over.

> See also: the `kali-arsenal` skill in `.claude/skills/` for the conventions to
> follow when adding or changing a tool.

## Design principles

1. **Structured over raw.** Wrappers parse tool output into dictionaries instead
   of dumping text, so the model gets `{"port": "443", "service": "https"}`
   rather than 80 lines of console output.
2. **One uniform schema.** Every wrapper returns at least `success`, `installed`,
   `command`, `returncode`, `output`, `error` — plus tool-specific keys.
3. **No shell.** Commands run as argument lists through a shared runner with a
   timeout. User input is validated; shell metacharacters are rejected.
4. **Graceful when a tool is missing.** If a binary isn't installed, the wrapper
   returns a clear "install it with…" message instead of crashing.
5. **Deliberate for dual-use.** Offensive tools require an explicit
   `authorized=True` flag, consistent with the project DISCLAIMER.
6. **Single source of truth.** `TOOL_CATEGORIES` drives the flat tool list, the
   metadata, and the `/list tools` display.

## Layout

```
agents/utils/tools/
├── _runner.py          # shared: validation, run_command, result schema, logging
├── __init__.py         # TOOL_CATEGORIES (source of truth) + registry accessors
├── locals.py           # execute_generic_linux_command, local server scraping
├── opensearchapi.py    # live web search (keyword_search, search_as_RAG)
├── web_request_framework.py  # HTTP request/response security analysis
├── kali_recon.py       # nmap, dns, dnsx, subdomains, whois, searchsploit
├── kali_web.py         # whatweb, httpx, katana, ffuf, nuclei, nikto, wpscan
├── kali_network.py     # sslscan (tls_audit), masscan, naabu
├── kali_secrets.py     # trufflehog, gitleaks
└── kali_offensive.py   # hash_identify + gated sqlmap/hydra/hashcat
```

## Tool catalogue (29 tools)

### Core
`check_search_connection`, `keyword_search`, `search_as_RAG`,
`get_local_server_content`, `execute_generic_linux_command`,
`web_request_analysis`, `get_raw_response`

### Recon / OSINT
| Tool | Binary | Output |
|------|--------|--------|
| `nmap_scan` | nmap | parsed hosts/ports/services (XML) |
| `dns_recon` | dig | records by type |
| `dnsx_resolve` | dnsx | bulk DNS resolution (JSON) |
| `subdomain_enum` | subfinder | subdomain list |
| `whois_lookup` | whois | raw registration text |
| `searchsploit_lookup` | searchsploit | exploit list (JSON) |

`nmap_scan` accepts a **profile name** (`quick`, `service`, `full`, `syn`,
`connect`, `ping`, `udp`, `os`) — not raw flags — so output parsing stays
consistent and NSE/output flags can't be injected.

### Web
| Tool | Binary | Output |
|------|--------|--------|
| `http_fingerprint` | whatweb | tech stack + status (JSON) |
| `httpx_probe` | httpx | status/title/tech/TLS (JSON) |
| `katana_crawl` | katana | discovered endpoints/URLs |
| `dir_bruteforce` | ffuf | discovered paths (JSON) |
| `nuclei_scan` | nuclei | findings by severity (JSONL) |
| `nikto_scan` | nikto | raw server-scan report |
| `wpscan` | wpscan | WordPress version/plugins (JSON) |

### Network / TLS
| Tool | Binary | Output |
|------|--------|--------|
| `tls_audit` | sslscan | protocols/ciphers/cert |
| `masscan_sweep` | masscan | open ports (JSON) |
| `naabu_scan` | naabu | open ports (JSON) |

### Secret detection
| Tool | Binary | Output |
|------|--------|--------|
| `trufflehog_scan` | trufflehog | verified/unverified secret findings |
| `gitleaks_scan` | gitleaks | hardcoded-secret findings (JSON) |

### Offensive (dual-use — require `authorized=True`)
| Tool | Binary | Notes |
|------|--------|-------|
| `hash_identify` | hashid | identification only — **not** gated |
| `sqlmap_test` | sqlmap | SQL injection testing |
| `hydra_spray` | hydra | online credential brute-force |
| `hashcat_crack` | hashcat | offline hash cracking |

## Result schema

```python
{
  "success": bool,        # binary ran AND returncode == 0
  "installed": bool,      # binary found on PATH
  "command": str,         # the executed command line
  "returncode": int|None,
  "output": str|None,     # raw stdout
  "error": str|None,      # stderr or a runner-level message
  # ...plus tool-specific keys, e.g. "hosts", "findings", "open_ports"
}
```

## Extending the arsenal

Follow the `kali-arsenal` skill. In short: add the function to the right
`kali_*` module, register it in `TOOL_CATEGORIES`, document it here and in
`requirements/globals.md`, and add tests under `tests/`.

## Testing

```bash
pip install -r requirements/dev-requirements.txt
pytest -q
```

The dispatch workflow (`.github/workflows/desktop_tools_dispatch.yml`) runs the
same suite and emits a downloadable tool manifest on every manual trigger.
