#!/usr/bin/env python3

# /agents/utils/tools/kali_offensive.py
# Offensive / dual-use tool wrappers for the KaliGPT AI agent.
#
# These tools (credential brute-forcing, SQL injection testing, hash cracking)
# are intended ONLY for authorized engagements such as penetration tests, CTFs
# and security research on systems you own or have explicit written permission
# to test. Per the project DISCLAIMER, each wrapper requires an explicit
# `authorized=True` flag before it will run, acting as a deliberate guardrail.


from ._runner import run_command, validate_arg, invalid_arg, _result


_AUTH_REQUIRED = (
    "Refused: this is a dual-use offensive tool. Pass authorized=True only when "
    "you have explicit permission to test the target (owned system, pentest "
    "engagement, CTF, or security research). See the project DISCLAIMER."
)


def _refused() -> dict:
    """Uniform refusal result for an unauthorized dual-use invocation."""
    return _result(False, error=_AUTH_REQUIRED, authorized=False)


def hash_identify(hash_value: str) -> dict:
    """
    Identify the likely type/algorithm of a password hash using hashid.

    This is identification only (no cracking) and does not require authorization.

    Args:
        hash_value (str): The hash string to identify.

    Returns:
        dict with the raw hashid output plus runner status.
    """
    # NB: don't use the strict validate_arg() here — it rejects '$', which is
    # part of valid modular hash formats (bcrypt "$2a$...", sha512crypt "$6$...").
    # Run as a single argv element (no shell), so only reject empty values and
    # whitespace (which would split into multiple hashid arguments).
    if (not isinstance(hash_value, str) or not hash_value
            or any(ch in "\n\r\t " for ch in hash_value)):
        return invalid_arg("hash_value", hash_value)
    return run_command(["hashid", hash_value], timeout=15)


def sqlmap_test(url: str, authorized: bool = False, extra_args: list[str] | None = None,
                timeout: int = 600) -> dict:
    """
    Test a URL for SQL injection using sqlmap (authorized testing only).

    Args:
        url (str): Target URL, ideally including a parameter, e.g. "http://t/?id=1".
        authorized (bool): Must be True to confirm you are authorized to test the target.
        extra_args (list[str] | None): Optional extra sqlmap flags (validated individually).
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with the raw sqlmap output plus runner status, or a refusal if not authorized.
    """
    if not authorized:
        return _refused()
    if not validate_arg(url):
        return invalid_arg("url", url)

    args = ["sqlmap", "-u", url, "--batch"]
    for extra in (extra_args or []):
        if not validate_arg(extra):
            return invalid_arg("argument", extra)
        args.append(extra)
    return run_command(args, timeout=timeout)


def hydra_spray(target: str, service: str, username: str | None = None,
                userlist: str | None = None, passlist: str | None = None,
                authorized: bool = False, timeout: int = 600) -> dict:
    """
    Run an online credential brute-force/spray with hydra (authorized testing only).

    Args:
        target (str): Target host or IP.
        service (str): Service/protocol, e.g. "ssh", "ftp", "http-post-form".
        username (str | None): Single username (use this OR userlist).
        userlist (str | None): Path to a username wordlist.
        passlist (str | None): Path to a password wordlist.
        authorized (bool): Must be True to confirm authorization to test the target.
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with the raw hydra output plus runner status, or a refusal if not authorized.
    """
    if not authorized:
        return _refused()
    for name, val in (("target", target), ("service", service)):
        if not validate_arg(val):
            return invalid_arg(name, val)

    if username and userlist:
        return _result(False, error="Provide exactly one of username or userlist")

    args = ["hydra"]
    if username:
        if not validate_arg(username):
            return invalid_arg("username", username)
        args += ["-l", username]
    elif userlist:
        if not validate_arg(userlist):
            return invalid_arg("userlist", userlist)
        args += ["-L", userlist]
    else:
        return _result(False, error="Provide either username or userlist")

    if not passlist or not validate_arg(passlist):
        return invalid_arg("passlist", passlist)
    args += ["-P", passlist, target, service]

    return run_command(args, timeout=timeout)


def hashcat_crack(hashfile: str, wordlist: str, hash_mode: str, authorized: bool = False,
                  timeout: int = 600) -> dict:
    """
    Crack hashes from a file with hashcat using a wordlist (authorized testing only).

    Args:
        hashfile (str): Path to the file containing hashes.
        wordlist (str): Path to the wordlist.
        hash_mode (str): Hashcat hash mode number, e.g. "0" for MD5, "1000" for NTLM.
        authorized (bool): Must be True to confirm authorization.
        timeout (int): Max seconds to wait. (default = 600)

    Returns:
        dict with the raw hashcat output plus runner status, or a refusal if not authorized.
    """
    if not authorized:
        return _refused()
    for name, val in (("hashfile", hashfile), ("wordlist", wordlist), ("hash_mode", hash_mode)):
        if not validate_arg(val):
            return invalid_arg(name, val)
    if not hash_mode.isdigit():
        return invalid_arg("hash_mode", f"{hash_mode!r} (must be numeric)")

    args = ["hashcat", "-m", hash_mode, "-a", "0", hashfile, wordlist, "--potfile-disable"]
    return run_command(args, timeout=timeout)


if __name__ == "__main__":
    print(hash_identify("5f4dcc3b5aa765d61d8327deb882cf99"))
    print(sqlmap_test("http://example.com/?id=1"))  # refused without authorized=True
