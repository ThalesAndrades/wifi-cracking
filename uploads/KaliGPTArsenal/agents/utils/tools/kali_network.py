#!/usr/bin/env python3

# /agents/utils/tools/kali_network.py
# Network and TLS analysis tool wrappers for the KaliGPT AI agent.


import json
import logging

from ._runner import run_command, validate_arg, invalid_arg

logger = logging.getLogger("kaligpt.tools")


def tls_audit(target: str, port: str = "443", timeout: int = 120) -> dict:
    """
    Audit a host's TLS/SSL configuration (protocols, ciphers, certificate) using sslscan.

    Args:
        target (str): Host or IP to audit.
        port (str): TLS port. (default = "443")
        timeout (int): Max seconds to wait. (default = 120)

    Returns:
        dict with the raw sslscan report in 'output' plus runner status.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)
    if not validate_arg(port):
        return invalid_arg("port", port)
    return run_command(["sslscan", f"{target}:{port}"], timeout=timeout)


def masscan_sweep(target: str, ports: str = "1-1000", rate: str = "1000", timeout: int = 300) -> dict:
    """
    Perform a fast port sweep over a target or range using masscan.

    Args:
        target (str): Host, IP or CIDR range to scan.
        ports (str): Port spec, e.g. "1-1000" or "80,443". (default = "1-1000")
        rate (str): Packets per second. (default = "1000")
        timeout (int): Max seconds to wait. (default = 300)

    Note:
        masscan typically requires root privileges (raw sockets).

    Returns:
        dict with a parsed 'open_ports' list plus runner data.
    """
    for name, val in (("target", target), ("ports", ports), ("rate", rate)):
        if not validate_arg(val):
            return invalid_arg(name, val)

    result = run_command(
        ["masscan", target, "-p", ports, "--rate", rate, "-oJ", "/dev/stdout"],
        timeout=timeout,
    )
    open_ports = []
    if result.get("output"):
        # masscan -oJ emits a JSON array (sometimes with blank/trailing lines).
        text = result["output"].strip()
        data = []
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Fall back to parsing line-delimited JSON records.
            for line in text.splitlines():
                line = line.strip().rstrip(",")
                if not line or line in ("[", "]"):
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        for entry in data if isinstance(data, list) else []:
            for p in entry.get("ports", []):
                open_ports.append({
                    "ip": entry.get("ip"),
                    "port": p.get("port"),
                    "proto": p.get("proto"),
                    "status": p.get("status"),
                })
    result["open_ports"] = open_ports
    return result


def naabu_scan(target: str, ports: str | None = None, top_ports: str = "100",
               timeout: int = 300) -> dict:
    """
    Fast SYN/CONNECT port scan of a host using naabu (ProjectDiscovery).

    Args:
        target (str): Host or IP to scan.
        ports (str | None): Explicit port spec, e.g. "80,443" or "1-1000".
            When omitted, naabu scans the top N ports.
        top_ports (str): Number of top ports to scan when 'ports' is omitted. (default = "100")
        timeout (int): Max seconds to wait. (default = 300)

    Returns:
        dict with a parsed 'open_ports' list (host, port) plus runner data.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)

    args = ["naabu", "-host", target, "-json", "-silent"]
    if ports:
        if not validate_arg(ports):
            return invalid_arg("ports", ports)
        args += ["-p", ports]
    else:
        if not top_ports.isdigit():
            return invalid_arg("top_ports", f"{top_ports!r} (must be numeric)")
        args += ["-top-ports", top_ports]

    result = run_command(args, timeout=timeout)
    open_ports = []
    if result.get("output"):
        for line in result["output"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                open_ports.append({
                    "host": entry.get("host") or entry.get("ip"),
                    "port": entry.get("port"),
                })
            except json.JSONDecodeError:
                continue
    result["open_ports"] = open_ports
    result["count"] = len(open_ports)
    return result


if __name__ == "__main__":
    print(tls_audit("example.com"))
