"""Tests for the dual-use authorization gate and input validation."""

from agents.utils.tools import kali_offensive


def test_sqlmap_refused_without_authorization():
    result = kali_offensive.sqlmap_test("http://example.com/?id=1")
    assert result["success"] is False
    assert result["authorized"] is False
    assert "authorized=True" in result["error"]


def test_hydra_refused_without_authorization():
    result = kali_offensive.hydra_spray("10.0.0.1", "ssh", username="root",
                                        passlist="/tmp/p.txt")
    assert result["success"] is False
    assert result["authorized"] is False


def test_hashcat_refused_without_authorization():
    result = kali_offensive.hashcat_crack("/tmp/h.txt", "/tmp/w.txt", "0")
    assert result["success"] is False
    assert result["authorized"] is False


def test_authorized_call_validates_input_before_running():
    # Authorized but with an invalid (space/metachar) target -> validation error,
    # not a refusal. This proves the gate is passed and validation still applies.
    result = kali_offensive.sqlmap_test("bad url with spaces", authorized=True)
    assert result["success"] is False
    assert "Invalid" in result["error"]


def test_hashcat_rejects_non_numeric_mode():
    result = kali_offensive.hashcat_crack("/tmp/h.txt", "/tmp/w.txt", "abc",
                                          authorized=True)
    assert result["success"] is False
    assert "hash_mode" in result["error"]


def test_hash_identify_requires_no_authorization():
    # hash_identify is identification only; it should not be gated. With the
    # binary likely absent in CI it returns a missing-dependency result, but it
    # must never return the authorization refusal.
    result = kali_offensive.hash_identify("5f4dcc3b5aa765d61d8327deb882cf99")
    assert "authorized=True" not in (result.get("error") or "")
