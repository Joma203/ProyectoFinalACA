"""Tests para app/parser/response_builder.py"""
from app.parser.models import Vulnerability
from app.parser.response_builder import (
    build_response,
    build_summary,
    vulnerabilities_to_json,
)


def make_vuln(severity="Low", **overrides):
    """Helper para construir vulnerabilidades de prueba."""
    defaults = dict(
        severity=severity,
        cvss_score=5.0,
        cve="CVE-2024-0001",
        host="10.0.0.1",
        port="80/tcp",
        name="Test Vuln",
        family="Test Family",
        description="desc",
        impact="impact",
        solution="solution",
    )
    defaults.update(overrides)
    return Vulnerability(**defaults)


class TestBuildSummary:

    def test_empty_list_returns_zero_counts(self):
        assert build_summary([]) == {
            "critical": 0, "high": 0, "medium": 0, "low": 0
        }

    def test_counts_each_severity(self):
        vulns = [
            make_vuln("Critical"), make_vuln("Critical"),
            make_vuln("High"),
            make_vuln("Medium"), make_vuln("Medium"), make_vuln("Medium"),
            make_vuln("Low"),
        ]
        summary = build_summary(vulns)
        assert summary == {"critical": 2, "high": 1, "medium": 3, "low": 1}

    def test_severity_is_case_insensitive(self):
        # build_summary aplica .lower() antes de buscar la clave.
        vulns = [make_vuln("CRITICAL"), make_vuln("high")]
        summary = build_summary(vulns)
        assert summary["critical"] == 1
        assert summary["high"] == 1

    def test_unknown_severity_is_ignored(self):
        vulns = [make_vuln("Unknown"), make_vuln("Critical")]
        summary = build_summary(vulns)
        assert summary["critical"] == 1
        # "unknown" no debería aparecer como clave
        assert "unknown" not in summary


class TestVulnerabilitiesToJson:

    def test_empty_input_returns_empty_list(self):
        assert vulnerabilities_to_json([]) == []

    def test_all_fields_serialized(self):
        vuln = make_vuln("High", cvss_score=7.5, cve="CVE-X")
        result = vulnerabilities_to_json([vuln])[0]
        expected_keys = {
            "severity", "cvss_score", "cve", "host", "port",
            "name", "family", "description", "impact", "solution",
        }
        assert set(result.keys()) == expected_keys
        assert result["severity"] == "High"
        assert result["cvss_score"] == 7.5
        assert result["cve"] == "CVE-X"

    def test_preserves_order(self):
        vulns = [make_vuln(name="A"), make_vuln(name="B"), make_vuln(name="C")]
        result = vulnerabilities_to_json(vulns)
        assert [v["name"] for v in result] == ["A", "B", "C"]


class TestBuildResponse:

    def test_full_response_structure(self):
        vulns = [make_vuln("Critical"), make_vuln("Low")]
        response = build_response(vulns)
        assert set(response.keys()) == {"summary", "vulnerabilities"}
        assert response["summary"]["critical"] == 1
        assert response["summary"]["low"] == 1
        assert len(response["vulnerabilities"]) == 2

    def test_empty_input(self):
        response = build_response([])
        assert response["vulnerabilities"] == []
        assert sum(response["summary"].values()) == 0
