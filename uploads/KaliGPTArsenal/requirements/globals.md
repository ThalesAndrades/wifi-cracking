[//]: # ( /requirements/global.md )
[//]: # ( SudoHopeX: https://hope.is-a.dev, github.com/SudoHopeX )
[//]: # ( Updated: 21 March 2026 )

# KaliGPT Requirements
This document lists all the requirements/dependencies for KaliGPT, categorized by their source.

## Index
- [GitHub Packages](#github-packages)
- [PyPI (python pip) Packages](#pypi-python-pip-packages)
- [System Packages](#system-packages)
- [Tools](#tools)
- [Love 🩵](#love)


## GitHub Packages
| Package                     | Description                               |
|-----------------------------|-------------------------------------------|
| SudoHopeX/**OpenSearchAPI** | for performing search queries freely.     |
| SudoHopeX/**KaliGPT** 😉    | for using the KaliGPT itself              |


## PyPI (python pip) Packages
| Package                                                                        | Description                          |
|--------------------------------------------------------------------------------|--------------------------------------|
| `openai`                                                                       | accessing openai & OpenRouter models |
| `google-genai`                                                                 | accessing google gemini models       |
| `ollama`                                                                       | using ollama models                  |
| `rich`                                                                         | for rich text output                 |
| `requests`                                                                     | making HTTP requests                 |
| `newspaper3k`,`lxml_html_clean`                                                | cleaning & parsing HTML              |
| `beautifulsoup4`, `flask`, `ddgs`, `curl_cffi`, `nodriver`, `pyvirtualdisplay` | OpenSearchAPI dependency             |
| `prompt_toolkit`                                                               | Interactive CLI Selector             | 


## System Packages
| Package                                                                  | Description                                                                   | 
|--------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `curl`                                                                   | Downloading KaliGPT installer scripts                                         |
| `python3`                                                                | Running Python scripts                                                        |
| `python3-venv`                                                           | Managing & using virtual environments                                         | 
| `python3-pip`                                                            | Installing Python dependencies                                                | 
| `git`                                                                    | Cloning GitHub repositories                                                   |
| `bash`                                                                   | Installing KaliGPT, creating & using KaliGPT launcher                         |
| `lixxml2`, `libxslt`                                                     | for building `lxml_html_clean`                                                |
| `libjpeg-turbo`, `libpng`, `freetype`, `littlecms`,`openjpeg`, `libtiff` | for building `Pillow`                                                         | 
| `make`, `pkg-config`, `clang`                                            | building packages like `Pillow`, `lxml`, `lxml_html_clean`, and `newspaper3k` |
| `rust`                                                                   | for building `newspaper3k` dependencies                                       | 
| `chromium`, `xvfb`                                                       | OpenSearchAPI dependency                                                      |

## Tools

### Core (always available)

| Name                                                         | Description                                                               |
|--------------------------------------------------------------|---------------------------------------------------------------------------|
| `keyword_search`, `check_search_connection`, `search_as_RAG` | for online search & real-time info. connectivity                          |
| `get_local_server_content`                                   | extracting content accessible via local server (e.g. localhost etc.)      |
| `execute_generic_linux_command`                              | executing linux tools & commands (supports `use_shell` + `timeout`)       |
| `web_request_analysis`, `get_raw_response`                   | HTTP/HTTPS request & response security analysis                           |

### Kali security wrappers
These call external Kali tools and return **structured output**. Each tool degrades
gracefully when its binary is not installed (`sudo apt install <tool>`).

| Name                | Underlying Kali tool      | Description                                                |
|---------------------|---------------------------|------------------------------------------------------------|
| `nmap_scan`         | `nmap`                    | port/service/version scan, parsed from nmap XML            |
| `dns_recon`         | `dig` (dnsutils)          | resolves A/AAAA/MX/NS/TXT/CNAME records                    |
| `dnsx_resolve`      | `dnsx`                    | bulk DNS resolution, parsed from JSON                      |
| `subdomain_enum`    | `subfinder`               | passive subdomain enumeration                              |
| `whois_lookup`      | `whois`                   | domain/IP registration lookup                              |
| `searchsploit_lookup` | `searchsploit` (exploitdb) | local Exploit-DB search, parsed from JSON               |
| `http_fingerprint`  | `whatweb`                 | web tech-stack & header fingerprinting                     |
| `httpx_probe`       | `httpx`                   | HTTP probing: status/title/tech/TLS, parsed from JSON      |
| `katana_crawl`      | `katana`                  | web crawler — maps endpoints/attack surface                |
| `dir_bruteforce`    | `ffuf`                    | directory/file content discovery via wordlist             |
| `nuclei_scan`       | `nuclei`                  | template-based vulnerability scanning, parsed from JSONL   |
| `nikto_scan`        | `nikto`                   | web server vulnerability scan                              |
| `wpscan`            | `wpscan`                  | WordPress version/plugin/theme audit                       |
| `tls_audit`         | `sslscan`                 | TLS/SSL protocol, cipher & certificate audit              |
| `masscan_sweep`     | `masscan`                 | fast large-range port sweep (needs root)                  |
| `naabu_scan`        | `naabu`                   | fast port scan, parsed from JSON                           |

### Secret detection
| Name              | Underlying tool | Description                                              |
|-------------------|-----------------|---------------------------------------------------------|
| `trufflehog_scan` | `trufflehog`    | find (and verify) leaked secrets in paths/git repos     |
| `gitleaks_scan`   | `gitleaks`      | detect hardcoded secrets in a git repo/directory        |

### Offensive / dual-use ( require `authorized=True` )
For **authorized** engagements only (owned systems, pentests, CTFs, research),
per the project [DISCLAIMER](../DISCLAIMER.md).

| Name             | Underlying Kali tool | Description                                          |
|------------------|----------------------|------------------------------------------------------|
| `hash_identify`  | `hashid`             | identify hash type (identification only, no gating)  |
| `sqlmap_test`    | `sqlmap`             | SQL injection testing                                |
| `hydra_spray`    | `hydra`              | online credential brute-force/spray                  |
| `hashcat_crack`  | `hashcat`            | offline hash cracking with a wordlist                |


## Love
Lots of ❤️, Care and ⭐ from the community!
