"""Tests for the tool registry and its category metadata."""

from agents.utils import tools


def test_registry_exposes_all_tools():
    info = tools.get_tools_info()
    # 7 core + 6 recon + 7 web + 3 network + 2 secrets + 4 offensive = 29
    assert len(info) == 29
    # No duplicate tool names.
    names = [t.__name__ for t in info]
    assert len(names) == len(set(names))


def test_available_tools_data_has_descriptions():
    data = tools.get_available_tools_data()
    assert len(data) == 29
    assert all(isinstance(desc, str) and desc for desc in data.values())


def test_metadata_categories_and_dual_use_flags():
    meta = tools.get_tools_metadata()
    assert meta["nmap_scan"]["category"] == "Recon / OSINT"
    assert meta["nmap_scan"]["dual_use"] is False
    for name in ("sqlmap_test", "hydra_spray", "hashcat_crack"):
        assert meta[name]["dual_use"] is True
    # hash_identify is identification-only and must not be gated.
    assert meta["hash_identify"]["dual_use"] is False


def test_categories_cover_every_tool():
    from itertools import chain
    categorized = list(chain.from_iterable(tools.TOOL_CATEGORIES.values()))
    assert set(t.__name__ for t in categorized) == set(
        t.__name__ for t in tools.get_tools_info()
    )
