#!/usr/bin/env python3

# /agents/utils/tools/kali_recon.py
# Reconnaissance / OSINT tool wrappers for the KaliGPT AI agent.
# Each function runs an external Kali tool with safe defaults and returns a
# structured dictionary the model can reason about.


import json
import logging

# nmap output is untrusted (it can be influenced by attacker-controlled targets),
# so prefer defusedxml to guard against XXE / entity-expansion (billion laughs).
# Fall back to the stdlib parser if defusedxml is not installed.
try:
    from defusedxml import ElementTree as ET
    from defusedxml.common import DefusedXmlException
except ImportError:  # pragma: no cover - fallback when defusedxml is unavailable
    import xml.etree.ElementTree as ET
    DefusedXmlException = ET.ParseError

from ._runner import run_command, tool_available, validate_arg, invalid_arg, missing_dependency

logger = logging.getLogger("kaligpt.tools")


# Allowlist of supported nmap scan profiles -> safe flag sets. Callers pick a
# profile name instead of passing raw flags, so NSE scripts and output-altering
# options (which would break the wrapper's fixed "-oX - target" XML parsing)
# cannot be injected through the scan_type argument.
NMAP_PROFILES = {
    "quick": ["-T4", "-F"],            # fast scan of the most common ports
    "service": ["-sV"],               # service/version detection (default)
    "full": ["-sV", "-p-"],           # version detection across all ports
    "syn": ["-sS"],                   # TCP SYN scan (needs root)
    "connect": ["-sT"],               # TCP connect scan
    "ping": ["-sn"],                  # host discovery only, no port scan
    "udp": ["-sU"],                   # UDP scan (needs root)
    "os": ["-O", "-sV"],              # OS + service detection (needs root)
}


def nmap_scan(target: str, scan_type: str = "service", ports: str | None = None,
              timeout: int = 300) -> dict:
    """
    Run an nmap scan against a target and return parsed host/port/service data.

    Args:
        target (str): Host or IP to scan (single argument, no spaces).
        scan_type (str): A profile name from NMAP_PROFILES, e.g. "quick",
            "service", "full", "syn", "connect", "ping", "udp", "os". (default = "service")
        ports (str | None): Optional port spec, e.g. "1-1000" or "80,443".
        timeout (int): Max seconds to wait. (default = 300)

    Returns:
        dict with parsed 'hosts' (each with open ports/services) plus runner data.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)

    if scan_type not in NMAP_PROFILES:
        return invalid_arg(
            "scan_type",
            f"{scan_type!r}; allowed profiles: {', '.join(sorted(NMAP_PROFILES))}",
        )

    args = ["nmap", *NMAP_PROFILES[scan_type]]
    if ports:
        if not validate_arg(ports):
            return invalid_arg("ports", ports)
        args += ["-p", ports]
    args += ["-oX", "-", target]  # XML to stdout for parsing

    result = run_command(args, timeout=timeout)

    hosts = []
    if result.get("output"):
        try:
            root = ET.fromstring(result["output"])
            for host in root.findall("host"):
                addr_el = host.find("address")
                address = addr_el.get("addr") if addr_el is not None else None
                ports_data = []
                for port in host.findall("./ports/port"):
                    state_el = port.find("state")
                    service_el = port.find("service")
                    ports_data.append({
                        "port": port.get("portid"),
                        "protocol": port.get("protocol"),
                        "state": state_el.get("state") if state_el is not None else None,
                        "service": service_el.get("name") if service_el is not None else None,
                        "product": service_el.get("product") if service_el is not None else None,
                        "version": service_el.get("version") if service_el is not None else None,
                    })
                hosts.append({"address": address, "ports": ports_data})
        except (ET.ParseError, DefusedXmlException) as exc:
            logger.debug("nmap XML parse failed: %s", exc)

    result["hosts"] = hosts
    return result


def dns_recon(domain: str, record_types: list[str] | None = None, timeout: int = 30) -> dict:
    """
    Resolve common DNS records (A, AAAA, MX, NS, TXT, CNAME) for a domain via dig.

    Args:
        domain (str): Domain to query.
        record_types (list[str] | None): Record types to fetch.
            (default = A, AAAA, MX, NS, TXT)
        timeout (int): Max seconds per lookup. (default = 30)

    Returns:
        dict -> {"domain": ..., "records": {TYPE: [values]}, "errors": [...]}
    """
    if not validate_arg(domain):
        return invalid_arg("domain", domain)

    if not tool_available("dig"):
        return missing_dependency("dig")

    record_types = record_types or ["A", "AAAA", "MX", "NS", "TXT"]
    records, errors = {}, []
    any_success = False

    for rtype in record_types:
        if not validate_arg(rtype):
            errors.append(f"Invalid record type: {rtype!r}")
            continue
        res = run_command(["dig", "+short", domain, rtype], timeout=timeout)
        if res.get("success") and res.get("output"):
            values = [line for line in res["output"].splitlines() if line.strip()]
            records[rtype] = values
            any_success = True
        elif res.get("error"):
            errors.append(f"{rtype}: {res['error']}")

    return {"success": any_success, "installed": True, "domain": domain,
            "records": records, "errors": errors}


def subdomain_enum(domain: str, timeout: int = 180) -> dict:
    """
    Enumerate subdomains of a domain passively using subfinder.

    Args:
        domain (str): Root domain to enumerate.
        timeout (int): Max seconds to wait. (default = 180)

    Returns:
        dict with a 'subdomains' list plus runner data.
    """
    if not validate_arg(domain):
        return invalid_arg("domain", domain)

    result = run_command(["subfinder", "-silent", "-d", domain], timeout=timeout)
    subs = []
    if result.get("output"):
        subs = [line.strip() for line in result["output"].splitlines() if line.strip()]
    result["subdomains"] = subs
    result["count"] = len(subs)
    return result


def dnsx_resolve(domain: str, record_type: str = "a", timeout: int = 60) -> dict:
    """
    Bulk-resolve a domain (or wildcard) with dnsx and return resolved records.

    Args:
        domain (str): Domain or host to resolve.
        record_type (str): Record type: "a", "aaaa", "cname", "ns", "mx", "txt".
            (default = "a")
        timeout (int): Max seconds to wait. (default = 60)

    Returns:
        dict with a parsed 'records' list plus runner data.
    """
    if not validate_arg(domain):
        return invalid_arg("domain", domain)

    rtype = record_type.lower()
    if rtype not in ("a", "aaaa", "cname", "ns", "mx", "txt"):
        return invalid_arg("record_type", record_type)

    result = run_command(["dnsx", "-silent", "-json", f"-{rtype}", "-d", domain],
                         timeout=timeout)
    records = []
    if result.get("output"):
        for line in result["output"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                records.append({
                    "host": entry.get("host"),
                    "type": rtype,
                    "values": entry.get(rtype) or entry.get("a") or [],
                })
            except json.JSONDecodeError:
                continue
    result["records"] = records
    return result


def whois_lookup(target: str, timeout: int = 30) -> dict:
    """
    Look up WHOIS registration information for a domain or IP address.

    Args:
        target (str): Domain or IP to query.
        timeout (int): Max seconds to wait. (default = 30)

    Returns:
        dict with the raw WHOIS text in 'output' plus runner status.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)
    return run_command(["whois", target], timeout=timeout)


def searchsploit_lookup(term: str, timeout: int = 30) -> dict:
    """
    Search the local Exploit-DB (searchsploit) for known exploits matching a term.

    Args:
        term (str): Software/keyword to search, e.g. "apache 2.4".
        timeout (int): Max seconds to wait. (default = 30)

    Returns:
        dict with a parsed 'exploits' list (title, path/url) plus runner data.
    """
    if not term or not isinstance(term, str):
        return invalid_arg("term", term)

    # searchsploit accepts multiple terms as separate args; split on whitespace.
    terms = [t for t in term.split() if validate_arg(t)]
    if not terms:
        return invalid_arg("term", term)

    result = run_command(["searchsploit", "--json", *terms], timeout=timeout)
    exploits = []
    if result.get("output"):
        try:
            data = json.loads(result["output"])
            for item in data.get("RESULTS_EXPLOIT", []):
                exploits.append({
                    "title": item.get("Title"),
                    "path": item.get("Path"),
                    "edb_id": item.get("EDB-ID"),
                    "date": item.get("Date_Published"),
                })
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.debug("searchsploit JSON parse failed: %s", exc)
    result["exploits"] = exploits
    return result


if __name__ == "__main__":
    print(dns_recon("example.com"))
    print(whois_lookup("example.com"))
