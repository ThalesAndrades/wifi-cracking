"""Tests for the shared subprocess runner and argument validation."""

from agents.utils.tools import _runner


def test_validate_arg_accepts_simple_values():
    assert _runner.validate_arg("example.com")
    assert _runner.validate_arg("http://example.com/?id=1")
    assert _runner.validate_arg("1-1000")


def test_validate_arg_rejects_shell_metachars_and_spaces():
    assert not _runner.validate_arg("a b")           # space
    assert not _runner.validate_arg("a;rm -rf /")    # semicolon
    assert not _runner.validate_arg("a|b")           # pipe
    assert not _runner.validate_arg("a`b`")          # backtick
    assert not _runner.validate_arg("")              # empty
    assert not _runner.validate_arg(None)            # wrong type


def test_invalid_arg_has_base_schema():
    result = _runner.invalid_arg("target", "a b")
    for key in _runner.BASE_RESULT_KEYS:
        assert key in result
    assert result["success"] is False
    assert "target" in result["error"]


def test_missing_dependency_reports_not_installed():
    result = _runner.missing_dependency("definitely-not-a-real-binary")
    assert result["success"] is False
    assert result["installed"] is False
    assert "not installed" in result["error"]


def test_run_command_missing_binary():
    result = _runner.run_command(["definitely-not-a-real-binary-xyz", "--help"])
    assert result["success"] is False
    assert result["installed"] is False


def test_run_command_success_with_real_binary():
    # `true` exists on any POSIX system and exits 0.
    result = _runner.run_command(["true"])
    assert result["installed"] is True
    assert result["success"] is True
    assert result["returncode"] == 0


def test_run_command_nonzero_returncode():
    result = _runner.run_command(["false"])
    assert result["installed"] is True
    assert result["success"] is False
    assert result["returncode"] != 0


def test_run_command_empty_args():
    result = _runner.run_command([])
    assert result["success"] is False
    assert "No command" in result["error"]
