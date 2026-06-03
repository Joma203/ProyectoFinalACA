
"""Tests para app/services/pdf_generator.py"""

from reportlab.lib import colors

from app.services.pdf_generator import (
    calculate_risk,
    generate_pdf,
    get_severity_color,
)


def make_report():
    return {
        "summary": {"critical": 1, "high": 2, "medium": 0, "low": 1},
        "vulnerabilities": [
            {
                "severity": "Critical",
                "cvss_score": 9.8,
                "cve": "CVE-2024-1234",
                "host": "192.168.1.10",
                "port": "443/tcp",
                "name": "Test Vuln",
                "family": "SSL",
                "description": "desc",
                "impact": "impact",
                "solution": "solution",
            }
        ],
    }


class TestPdfGenerator:

    def test_generates_pdf_file(self, tmp_path):
        out = tmp_path / "test.pdf"
        generate_pdf(make_report(), str(out))

        assert out.exists()
        assert out.stat().st_size > 0

    def test_pdf_has_valid_signature(self, tmp_path):
        out = tmp_path / "test.pdf"

        generate_pdf(make_report(), str(out))

        assert out.read_bytes()[:5] == b"%PDF-"

    def test_generates_with_empty_vulnerabilities(self, tmp_path):
        out = tmp_path / "empty.pdf"

        empty = {
            "summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "vulnerabilities": [],
        }

        generate_pdf(empty, str(out))

        assert out.exists()
        assert out.read_bytes()[:5] == b"%PDF-"


class TestCalculateRisk:

    def test_returns_high_when_critical_exists(self):
        summary = {
            "critical": 1,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        assert calculate_risk(summary) == "HIGH"

    def test_returns_high_when_more_than_three_high(self):
        summary = {
            "critical": 0,
            "high": 4,
            "medium": 0,
            "low": 0,
        }

        assert calculate_risk(summary) == "HIGH"

    def test_returns_medium_when_medium_exists(self):
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 1,
            "low": 0,
        }

        assert calculate_risk(summary) == "MEDIUM"

    def test_returns_low_when_no_findings(self):
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        assert calculate_risk(summary) == "LOW"


class TestSeverityColor:

    def test_critical_color(self):
        assert get_severity_color("critical") == colors.red

    def test_high_color(self):
        assert get_severity_color("high") == colors.orange

    def test_medium_color(self):
        assert get_severity_color("medium") == colors.yellow

    def test_low_color(self):
        assert get_severity_color("low") == colors.lightgreen

    def test_unknown_color_returns_lightgrey(self):
        assert get_severity_color("unknown") == colors.lightgrey
