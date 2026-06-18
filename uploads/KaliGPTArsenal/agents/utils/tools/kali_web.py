#!/usr/bin/env python3

# /agents/utils/tools/kali_web.py
# Web enumeration / scanning tool wrappers for the KaliGPT AI agent.


import json
import logging

from ._runner import run_command, validate_arg, invalid_arg

logger = logging.getLogger("kaligpt.tools")


def http_fingerprint(url: str, timeout: int = 60) -> dict:
    """
    Fingerprint a web target's technology stack and headers using whatweb.

    Args:
        url (str): Target URL or host.
        timeout (int): Max seconds to wait. (default = 60)

    Returns:
        dict with a parsed 'findings' summary plus runner data.
    """
    if not validate_arg(url):
        return invalid_arg("url", url)

    result = run_command(["whatweb", "--log-json=-", "--no-errors", url], timeout=timeout)
    findings = []
    if result.get("output"):
        for line in result["output"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                findings.append({
                    "target": entry.get("target"),
                    "http_status": entry.get("http_status"),
                    "plugins": list((entry.get("plugins") or {}).keys()),
                })
            except json.JSONDecodeError:
                continue
    result["findings"] = findings
    return result


def dir_bruteforce(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt",
                   extensions: str | None = None, timeout: int = 300) -> dict:
    """
    Brute-force web directories and files using ffuf and a wordlist.

    Args:
        url (str): Base URL; FUZZ keyword is appended automatically if absent.
        wordlist (str): Path to the wordlist. (default = dirb common.txt)
        extensions (str | None): Optional comma list of extensions, e.g. ".php,.txt".
        timeout (int): Max seconds to wait. (default = 300)

    Returns:
        dict with a 'results' list of discovered paths (status, length) plus runner data.
    """
    if not validate_arg(url):
        return invalid_arg("url", url)
    if not validate_arg(wordlist):
        return invalid_arg("wordlist", wordlist)

    fuzz_url = url if "FUZZ" in url else url.rstrip("/") + "/FUZZ"
    args = ["ffuf", "-u", fuzz_url, "-w", wordlist, "-of", "json", "-o", "/dev/stdout", "-s"]
    if extensions:
        if not validate_arg(extensions):
            return invalid_arg("extensions", extensions)
        args += ["-e", extensions]

    result = run_command(args, timeout=timeout)
    results = []
    if result.get("output"):
        try:
            data = json.loads(result["output"])
            for item in data.get("results", []):
                results.append({
                    "url": item.get("url"),
                    "status": item.get("status"),
                    "length": item.get("length"),
                    "words": item.get("words"),
                })
        except json.JSONDecodeError as exc:
            logger.debug("ffuf JSON parse failed: %s", exc)
    result["results"] = results
    return result


def nuclei_scan(url: str, severity: str | None = None, timeout: int = 600) -> dict:
    """
    Scan a web target for known vulnerabilities/misconfigurations using nuclei templates.

    Args:
        url (str): Target URL or host.
        severity (str | None): Optional severity filter, e.g. "critical,high".
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with a 'findings' list (template, severity, matched) plus runner data.
    """
    if not validate_arg(url):
        return invalid_arg("url", url)

    args = ["nuclei", "-u", url, "-jsonl", "-silent"]
    if severity:
        if not validate_arg(severity):
            return invalid_arg("severity", severity)
        args += ["-severity", severity]

    result = run_command(args, timeout=timeout)
    findings = []
    if result.get("output"):
        for line in result["output"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                info = entry.get("info", {})
                findings.append({
                    "template": entry.get("template-id"),
                    "name": info.get("name"),
                    "severity": info.get("severity"),
                    "matched": entry.get("matched-at"),
                })
            except json.JSONDecodeError:
                continue
    result["findings"] = findings
    result["count"] = len(findings)
    return result


def httpx_probe(target: str, timeout: int = 120) -> dict:
    """
    Probe an HTTP target with httpx for status, title, tech stack and TLS data.

    Args:
        target (str): Host or URL to probe.
        timeout (int): Max seconds to wait. (default = 120)

    Returns:
        dict with a parsed 'probes' list (url, status, title, tech) plus runner data.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)

    args = ["httpx", "-u", target, "-json", "-silent",
            "-status-code", "-title", "-tech-detect"]
    result = run_command(args, timeout=timeout)
    probes = []
    if result.get("output"):
        for line in result["output"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                probes.append({
                    "url": entry.get("url") or entry.get("input"),
                    "status": entry.get("status_code") or entry.get("status-code"),
                    "title": entry.get("title"),
                    "tech": entry.get("tech") or entry.get("technologies"),
                    "webserver": entry.get("webserver"),
                })
            except json.JSONDecodeError:
                continue
    result["probes"] = probes
    return result


def katana_crawl(url: str, depth: str = "2", timeout: int = 300) -> dict:
    """
    Crawl a web target with katana to map its attack surface (endpoints/URLs).

    Args:
        url (str): Base URL to crawl.
        depth (str): Maximum crawl depth. (default = "2")
        timeout (int): Max seconds to wait. (default = 300)

    Returns:
        dict with a discovered 'urls' list plus runner data.
    """
    if not validate_arg(url):
        return invalid_arg("url", url)
    if not depth.isdigit():
        return invalid_arg("depth", f"{depth!r} (must be numeric)")

    result = run_command(["katana", "-u", url, "-d", depth, "-silent"], timeout=timeout)
    urls = []
    if result.get("output"):
        urls = [line.strip() for line in result["output"].splitlines() if line.strip()]
    result["urls"] = urls
    result["count"] = len(urls)
    return result


def nikto_scan(target: str, timeout: int = 600) -> dict:
    """
    Run a Nikto web server vulnerability scan against a target.

    Args:
        target (str): Target host or URL.
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with the raw Nikto report in 'output' plus runner status.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)
    return run_command(["nikto", "-h", target], timeout=timeout)


def wpscan(url: str, timeout: int = 600) -> dict:
    """
    Scan a WordPress site for version, plugin and theme issues using wpscan.

    Args:
        url (str): WordPress site URL.
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with parsed 'wordpress' summary (where available) plus runner data.
    """
    if not validate_arg(url):
        return invalid_arg("url", url)

    result = run_command(["wpscan", "--url", url, "--format", "json", "--no-banner"],
                         timeout=timeout)
    if result.get("output"):
        try:
            data = json.loads(result["output"])
            result["wordpress"] = {
                "version": (data.get("version") or {}).get("number"),
                "interesting_findings": len(data.get("interesting_findings") or []),
                "plugins": list((data.get("plugins") or {}).keys()),
            }
        except json.JSONDecodeError as exc:
            logger.debug("wpscan JSON parse failed: %s", exc)
    return result


if __name__ == "__main__":
    print(http_fingerprint("https://example.com"))
