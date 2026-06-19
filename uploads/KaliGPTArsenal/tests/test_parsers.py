"""
Tests for the output parsers of the Kali tool wrappers.

Each test monkeypatches the shared `run_command` so no external tool is invoked;
we feed canned tool output and assert the wrapper parses it into structured data.
"""

import json

from agents.utils.tools import kali_recon, kali_web, kali_network, kali_secrets


def _fake_output(text, **extra):
    """Build a run_command-style result carrying canned stdout."""
    base = {"success": True, "installed": True, "command": "fake",
            "returncode": 0, "output": text, "error": None}
    base.update(extra)
    return base


def test_nmap_scan_parses_xml(monkeypatch):
    xml = """<?xml version="1.0"?>
    <nmaprun>
      <host>
        <address addr="93.184.216.34" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="80">
            <state state="open"/>
            <service name="http" product="nginx" version="1.18"/>
          </port>
          <port protocol="tcp" portid="443">
            <state state="open"/>
            <service name="https"/>
          </port>
        </ports>
      </host>
    </nmaprun>"""
    monkeypatch.setattr(kali_recon, "run_command", lambda *a, **k: _fake_output(xml))

    result = kali_recon.nmap_scan("example.com")
    assert len(result["hosts"]) == 1
    host = result["hosts"][0]
    assert host["address"] == "93.184.216.34"
    assert {p["port"] for p in host["ports"]} == {"80", "443"}
    http = next(p for p in host["ports"] if p["port"] == "80")
    assert http["service"] == "http"
    assert http["product"] == "nginx"


def test_nmap_scan_rejects_unknown_profile():
    result = kali_recon.nmap_scan("example.com", scan_type="--script=vuln")
    assert result["success"] is False
    assert "scan_type" in result["error"]


def test_nmap_scan_rejects_bad_target():
    result = kali_recon.nmap_scan("a; rm -rf /")
    assert result["success"] is False
    assert "target" in result["error"]


def test_searchsploit_parses_json(monkeypatch):
    payload = json.dumps({
        "RESULTS_EXPLOIT": [
            {"Title": "Apache 2.4 RCE", "Path": "/x/1.txt",
             "EDB-ID": "12345", "Date_Published": "2021-01-01"},
        ]
    })
    monkeypatch.setattr(kali_recon, "run_command", lambda *a, **k: _fake_output(payload))

    result = kali_recon.searchsploit_lookup("apache 2.4")
    assert len(result["exploits"]) == 1
    assert result["exploits"][0]["title"] == "Apache 2.4 RCE"
    assert result["exploits"][0]["edb_id"] == "12345"


def test_nuclei_parses_jsonl(monkeypatch):
    lines = "\n".join([
        json.dumps({"template-id": "tech-detect",
                    "info": {"name": "Tech Detect", "severity": "info"},
                    "matched-at": "http://t/"}),
        "",  # blank line should be skipped
        json.dumps({"template-id": "cve-2021-1234",
                    "info": {"name": "Some CVE", "severity": "high"},
                    "matched-at": "http://t/x"}),
    ])
    monkeypatch.setattr(kali_web, "run_command", lambda *a, **k: _fake_output(lines))

    result = kali_web.nuclei_scan("http://t/")
    assert result["count"] == 2
    sev = {f["severity"] for f in result["findings"]}
    assert sev == {"info", "high"}


def test_whatweb_parses_json_lines(monkeypatch):
    line = json.dumps({"target": "https://t/", "http_status": 200,
                       "plugins": {"nginx": {}, "PHP": {}}})
    monkeypatch.setattr(kali_web, "run_command", lambda *a, **k: _fake_output(line))

    result = kali_web.http_fingerprint("https://t/")
    assert result["findings"][0]["http_status"] == 200
    assert set(result["findings"][0]["plugins"]) == {"nginx", "PHP"}


def test_masscan_parses_json(monkeypatch):
    payload = json.dumps([
        {"ip": "10.0.0.1", "ports": [{"port": 22, "proto": "tcp", "status": "open"}]},
    ])
    monkeypatch.setattr(kali_network, "run_command", lambda *a, **k: _fake_output(payload))

    result = kali_network.masscan_sweep("10.0.0.1")
    assert result["open_ports"] == [
        {"ip": "10.0.0.1", "port": 22, "proto": "tcp", "status": "open"}
    ]


def test_httpx_parses_jsonl(monkeypatch):
    line = json.dumps({"url": "https://t/", "status_code": 200, "title": "Home",
                       "tech": ["nginx"], "webserver": "nginx"})
    monkeypatch.setattr(kali_web, "run_command", lambda *a, **k: _fake_output(line))

    result = kali_web.httpx_probe("t")
    assert result["probes"][0]["status"] == 200
    assert result["probes"][0]["tech"] == ["nginx"]


def test_katana_collects_urls(monkeypatch):
    out = "https://t/\nhttps://t/login\n\nhttps://t/api\n"
    monkeypatch.setattr(kali_web, "run_command", lambda *a, **k: _fake_output(out))

    result = kali_web.katana_crawl("https://t/")
    assert result["count"] == 3
    assert "https://t/login" in result["urls"]


def test_katana_rejects_non_numeric_depth():
    result = kali_web.katana_crawl("https://t/", depth="deep")
    assert result["success"] is False
    assert "depth" in result["error"]


def test_naabu_parses_jsonl(monkeypatch):
    lines = "\n".join([
        json.dumps({"host": "t", "ip": "10.0.0.1", "port": 80}),
        json.dumps({"host": "t", "ip": "10.0.0.1", "port": 443}),
    ])
    monkeypatch.setattr(kali_network, "run_command", lambda *a, **k: _fake_output(lines))

    result = kali_network.naabu_scan("t")
    assert result["count"] == 2
    assert {p["port"] for p in result["open_ports"]} == {80, 443}


def test_dnsx_parses_jsonl(monkeypatch):
    line = json.dumps({"host": "example.com", "a": ["93.184.216.34"]})
    monkeypatch.setattr(kali_recon, "run_command", lambda *a, **k: _fake_output(line))

    result = kali_recon.dnsx_resolve("example.com", record_type="a")
    assert result["records"][0]["values"] == ["93.184.216.34"]


def test_dnsx_rejects_bad_record_type():
    result = kali_recon.dnsx_resolve("example.com", record_type="zzz")
    assert result["success"] is False
    assert "record_type" in result["error"]


def test_trufflehog_parses_jsonl(monkeypatch):
    line = json.dumps({
        "DetectorName": "AWS", "Verified": True,
        "SourceMetadata": {"Data": {"Filesystem": {"file": "config.env"}}},
    })
    monkeypatch.setattr(kali_secrets, "run_command", lambda *a, **k: _fake_output(line))

    result = kali_secrets.trufflehog_scan(".")
    assert result["count"] == 1
    assert result["secrets"][0]["detector"] == "AWS"
    assert result["secrets"][0]["verified"] is True
    assert result["secrets"][0]["file"] == "config.env"


def test_gitleaks_parses_json(monkeypatch):
    payload = json.dumps([
        {"RuleID": "aws-key", "File": "app.py", "StartLine": 10,
         "Secret": "FAKE_TEST_SECRET_TOKEN"},
    ])
    monkeypatch.setattr(kali_secrets, "run_command", lambda *a, **k: _fake_output(payload))

    result = kali_secrets.gitleaks_scan("/repo")
    assert result["count"] == 1
    assert result["findings"][0]["rule"] == "aws-key"
    assert result["findings"][0]["secret_preview"] == "FAKE_TES…"
