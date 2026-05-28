"""Tests para app/services/pdf_generator.py"""
from app.services.pdf_generator import generate_pdf


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
            "summary": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "vulnerabilities": [],
        }
        generate_pdf(empty, str(out))
        assert out.exists()
        assert out.read_bytes()[:5] == b"%PDF-"
