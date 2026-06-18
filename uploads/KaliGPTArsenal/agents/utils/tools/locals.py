#!/usr/bin/env python3

# /agents/utils/tools/locals.py
# Updated: 28 Jan 2026


import ipaddress
import shlex
import requests

from bs4 import BeautifulSoup
from subprocess import Popen, PIPE, TimeoutExpired
from urllib.parse import urlparse


def get_local_server_content(url: str, timeout: int = 5) -> dict[str, bool | None | str] | dict[
    str, bool | int | str | None]:
    """
    Fetch and extract readable text content from a local server webpage.
    Returns structured status instead of raising exceptions.

    Args:
        url (str): The URL of the local server webpage to scrape.
        timeout (int): Timeout for the HTTP request in seconds. (default = 5)

    Returns:
        dict -> {  status: bool (True, False),
                    status_code: int | None,
                    error: str | None,
                    content: str | None
                    }
    """

    # Restrict to localhost/loopback targets: this helper is for local servers
    # only, and accepting arbitrary URLs would expose an SSRF path for probing
    # internal hosts or cloud metadata endpoints.
    host = urlparse(url).hostname
    if not host:
        return {"success": False, "status_code": None,
                "error": "Invalid URL", "content": None}
    try:
        is_local = host == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        is_local = host == "localhost"
    if not is_local:
        return {"success": False, "status_code": None,
                "error": "Only localhost/loopback URLs are allowed", "content": None}

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "LocalScraper/1.0"}
        )
    except requests.RequestException as exc:
        return {
            "success": False,
            "status_code": None,
            "error": str(exc),
            "content": None
        }

    if response.status_code != 200:
        return {
            "success": False,
            "status_code": response.status_code,
            "error": f"HTTP {response.status_code}",
            "content": None
        }

    soup = BeautifulSoup(response.content, "html.parser")

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    return {
        "success": True,
        "status_code": response.status_code,
        "error": None,
        "content": text
    }


def execute_generic_linux_command(command: str, use_shell: bool = False, timeout: int = 120,
                                  authorized: bool = False) -> dict:
    """
    Execute a generic Linux command using subprocess module.

   Args:
       command (str): The command to be executed, e.g., "ls -l", "mkdir dir", etc.
       use_shell (bool): Run via the shell so pipes, redirects, globs and "&&"
                         work, e.g. "cat f | grep x". (default = False)
       timeout (int): Max seconds to wait before aborting the command. (default = 120)
       authorized (bool): Must be True to run. This is an arbitrary-command
                         primitive, so it is gated like the other dual-use tools.

   Returns:
        dictionary of response -> {"output": output, "error": error}
    """
    if not authorized:
        return {
            "output": None,
            "error": "Refused: pass authorized=True to execute generic commands.",
            "authorized": False,
        }
    try:
        if use_shell:
            # Pass the command string to the shell so shell features work.
            process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        else:
            # shlex.split respects quoting (e.g. paths with spaces) unlike str.split.
            process = Popen(shlex.split(command), stdout=PIPE, stderr=PIPE)

        # Get the output and error messages (bounded by timeout)
        try:
            output, error = process.communicate(timeout=timeout)
        except TimeoutExpired:
            process.kill()
            output, error = process.communicate()
            return {"output": output.decode(errors="replace"),
                    "error": f"Command timed out after {timeout}s"}

        return {"output": output.decode(errors="replace"),
                "error": error.decode(errors="replace")}

    except Exception as e:
        return {"output": None, "error": f"Error Executing command {command} : {e}"}


if __name__ == "__main__":
    result = get_local_server_content("https://example.com")

    if result["success"]:
        print(result["content"][:500])
    else:
        print(f"Error: {result['error']} (status={result['status_code']})")

    print(execute_generic_linux_command("ls -ls", authorized=True))
