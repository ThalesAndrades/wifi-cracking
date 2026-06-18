#!/usr/bin/env python3

# /agents/utils/tools/kali_secrets.py
# Secret-detection tool wrappers for the KaliGPT AI agent.
# These scan code/filesystems/repos for leaked credentials and keys, returning
# structured findings the model can triage.


import json
import logging

from ._runner import run_command, validate_arg, invalid_arg

logger = logging.getLogger("kaligpt.tools")


def trufflehog_scan(target: str, source: str = "filesystem", only_verified: bool = False,
                    timeout: int = 600) -> dict:
    """
    Scan a filesystem path or git repo for leaked secrets using trufflehog.

    Args:
        target (str): Path to scan, or a git repo URL when source="git".
        source (str): "filesystem" (default) or "git".
        only_verified (bool): Return only secrets trufflehog could actively verify.
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with a parsed 'secrets' list (detector, verified, file) plus runner data.
    """
    if not validate_arg(target):
        return invalid_arg("target", target)
    if source not in ("filesystem", "git"):
        return invalid_arg("source", source)

    args = ["trufflehog", source, target, "--json", "--no-update"]
    if only_verified:
        args.append("--only-verified")

    result = run_command(args, timeout=timeout)
    secrets = []
    if result.get("output"):
        for line in result["output"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                metadata = entry.get("SourceMetadata", {}).get("Data", {})
                location = next(iter(metadata.values()), {}) if metadata else {}
                secrets.append({
                    "detector": entry.get("DetectorName"),
                    "verified": entry.get("Verified"),
                    "file": location.get("file") if isinstance(location, dict) else None,
                })
            except (json.JSONDecodeError, AttributeError):
                continue
    result["secrets"] = secrets
    result["count"] = len(secrets)
    return result


def gitleaks_scan(repo_path: str, timeout: int = 600) -> dict:
    """
    Detect hardcoded secrets in a git repository or directory using gitleaks.

    Args:
        repo_path (str): Path to the git repo / directory to scan.
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with a parsed 'findings' list (rule, file, secret_preview) plus runner data.
    """
    if not validate_arg(repo_path):
        return invalid_arg("repo_path", repo_path)

    # gitleaks reports findings as JSON to a file; "-" writes JSON to stdout.
    args = ["gitleaks", "detect", "--source", repo_path,
            "--report-format", "json", "--report-path", "-", "--no-banner"]
    result = run_command(args, timeout=timeout)
    findings = []
    if result.get("output"):
        try:
            data = json.loads(result["output"])
            for item in data if isinstance(data, list) else []:
                secret = item.get("Secret", "")
                findings.append({
                    "rule": item.get("RuleID"),
                    "file": item.get("File"),
                    "line": item.get("StartLine"),
                    "secret_preview": (secret[:8] + "…") if secret else None,
                })
        except json.JSONDecodeError as exc:
            logger.debug("gitleaks JSON parse failed: %s", exc)
    result["findings"] = findings
    result["count"] = len(findings)
    return result


if __name__ == "__main__":
    print(trufflehog_scan("."))
