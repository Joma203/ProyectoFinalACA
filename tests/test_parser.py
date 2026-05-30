"""
Tests para el parser de reportes OpenVAS.
Cubre: parseo de vulnerabilidades, mapeo de severidad, normalización de CVE,
parseo de tags, y manejo de XML inválido.
"""
import xml.etree.ElementTree as ET

import pytest

from app.parser.exceptions import InvalidXMLException
from app.parser.models import Vulnerability
from app.parser.openvas_parser import OpenVASParser
from app.parser.parser_adapter import process_xml
from app.parser.xml_loader import load_xml


# ---------- xml_loader ----------

class TestXmlLoader:

    def test_load_valid_xml_returns_root(self, sample_xml_path):
        root = load_xml(str(sample_xml_path))
        assert root is not None
        assert root.tag == "report"

    def test_load_malformed_xml_raises(self, tmp_path):
        bad = tmp_path / "bad.xml"
        bad.write_text("<root><unclosed>")
        with pytest.raises(InvalidXMLException):
            load_xml(str(bad))

    def test_load_nonexistent_file_raises(self):
        # ET.parse lanza FileNotFoundError, no InvalidXMLException.
        # Documentamos el comportamiento actual.
        with pytest.raises(FileNotFoundError):
            load_xml("/ruta/que/no/existe.xml")


# ---------- OpenVASParser._map_severity ----------

class TestMapSeverity:

    @pytest.fixture
    def parser(self):
        return OpenVASParser(root=None)

    def test_critical_threshold(self, parser):
        assert parser._map_severity("9.0") == "Critical"
        assert parser._map_severity("10.0") == "Critical"

    def test_high_threshold(self, parser):
        assert parser._map_severity("7.0") == "High"
        assert parser._map_severity("8.9") == "High"

    def test_medium_threshold(self, parser):
        assert parser._map_severity("4.0") == "Medium"
        assert parser._map_severity("6.9") == "Medium"

    def test_low_threshold(self, parser):
        assert parser._map_severity("0.0") == "Low"
        assert parser._map_severity("3.9") == "Low"

    def test_invalid_severity_returns_unknown(self, parser):
        assert parser._map_severity("abc") == "Unknown"
        assert parser._map_severity("") == "Unknown"


# ---------- OpenVASParser._normalize_cve ----------

class TestNormalizeCve:

    @pytest.fixture
    def parser(self):
        return OpenVASParser(root=None)

    def test_valid_cve_preserved(self, parser):
        assert parser._normalize_cve("CVE-2024-1234") == "CVE-2024-1234"

    def test_nocve_normalized_to_na(self, parser):
        assert parser._normalize_cve("NOCVE") == "N/A"
        assert parser._normalize_cve("nocve") == "N/A"
        assert parser._normalize_cve("NoCVE") == "N/A"

    def test_empty_string_returns_na(self, parser):
        # Una cadena vacía es "falsy" en Python, así que el parser
        # entra en la rama temprana y devuelve "N/A".
        assert parser._normalize_cve("") == "N/A"

    def test_whitespace_stripped(self, parser):
        assert parser._normalize_cve("  CVE-2024-1234  ") == "CVE-2024-1234"


# ---------- OpenVASParser._parse_tags ----------

class TestParseTags:

    @pytest.fixture
    def parser(self):
        return OpenVASParser(root=None)

    def test_parse_full_tags(self, parser):
        text = "summary=A description|impact=An impact|solution=A fix"
        parsed = parser._parse_tags(text)
        assert parsed["summary"] == "A description"
        assert parsed["impact"] == "An impact"
        assert parsed["solution"] == "A fix"

    def test_empty_tags_returns_empty_dict(self, parser):
        assert parser._parse_tags("") == {}
        assert parser._parse_tags(None) == {}

    def test_malformed_tags_are_skipped(self, parser):
        # "noequals" no tiene `=`, debe ignorarse y los demás se conservan.
        text = "summary=ok|noequals|solution=also ok"
        parsed = parser._parse_tags(text)
        assert parsed == {"summary": "ok", "solution": "also ok"}

    def test_value_with_equals_sign(self, parser):
        # split("=", 1) preserva el `=` en el valor.
        text = "summary=x=y=z"
        assert parser._parse_tags(text)["summary"] == "x=y=z"


# ---------- OpenVASParser.parse_vulnerabilities (integración) ----------

class TestParseVulnerabilities:

    @pytest.fixture
    def parsed(self, sample_xml_path):
        root = load_xml(str(sample_xml_path))
        return OpenVASParser(root).parse_vulnerabilities()

    def test_returns_correct_count(self, parsed):
        assert len(parsed) == 4

    def test_all_items_are_vulnerability_dataclass(self, parsed):
        assert all(isinstance(v, Vulnerability) for v in parsed)

    def test_critical_vuln_fields(self, parsed):
        critical = next(v for v in parsed if v.severity == "Critical")
        assert critical.cve == "CVE-2024-1234"
        assert critical.cvss_score == 9.8
        assert critical.host == "192.168.1.10"
        assert critical.port == "443/tcp"
        assert critical.name == "Critical SSL Vulnerability"
        assert critical.family == "SSL and TLS"
        assert "TLS handshake" in critical.description
        assert "Remote code execution" in critical.impact
        assert "OpenSSL" in critical.solution

    def test_severity_distribution(self, parsed):
        severities = [v.severity for v in parsed]
        assert severities.count("Critical") == 1
        assert severities.count("High") == 1
        assert severities.count("Medium") == 1
        assert severities.count("Low") == 1

    def test_nocve_is_normalized(self, parsed):
        info_disclosure = next(
            v for v in parsed if v.name == "HTTP Server Information Disclosure"
        )
        assert info_disclosure.cve == "N/A"

    def test_cvss_score_is_float(self, parsed):
        for v in parsed:
            assert isinstance(v.cvss_score, float)


class TestParserEdgeCases:

    def test_empty_results_returns_empty_list(self):
        xml = "<report><results></results></report>"
        root = ET.fromstring(xml)
        parser = OpenVASParser(root)
        assert parser.parse_vulnerabilities() == []

    def test_invalid_cvss_defaults_to_zero(self):
        xml = """
        <report><results><result>
            <host>h</host><port>p</port><severity>5</severity>
            <nvt><name>x</name><family>f</family>
                 <cvss_base>not-a-number</cvss_base><cve>N/A</cve>
                 <tags></tags></nvt>
        </result></results></report>
        """
        root = ET.fromstring(xml)
        vulns = OpenVASParser(root).parse_vulnerabilities()
        assert vulns[0].cvss_score == 0.0

    def test_missing_optional_fields_use_defaults(self):
        xml = """
        <report><results><result>
            <severity>5</severity>
            <nvt><cvss_base>5.0</cvss_base></nvt>
        </result></results></report>
        """
        root = ET.fromstring(xml)
        vulns = OpenVASParser(root).parse_vulnerabilities()
        v = vulns[0]
        assert v.host == "unknown"
        assert v.port == "unknown"
        assert v.name == "Unknown Vulnerability"
        assert v.family == "Unknown"
        assert v.description == "No description available."
        assert v.impact == "No impact information."
        assert v.solution == "No solution available."


# ---------- parser_adapter.process_xml (end-to-end del parser) ----------

class TestProcessXml:

    def test_returns_summary_and_vulnerabilities(self, sample_xml_bytes):
        result = process_xml(sample_xml_bytes)
        assert "summary" in result
        assert "vulnerabilities" in result

    def test_summary_counts_match(self, sample_xml_bytes):
        result = process_xml(sample_xml_bytes)
        summary = result["summary"]
        assert summary["critical"] == 1
        assert summary["high"] == 1
        assert summary["medium"] == 1
        assert summary["low"] == 1

    def test_vulnerabilities_serialized_as_dicts(self, sample_xml_bytes):
        result = process_xml(sample_xml_bytes)
        assert len(result["vulnerabilities"]) == 4
        assert all(isinstance(v, dict) for v in result["vulnerabilities"])

    def test_malformed_xml_raises(self, malformed_xml_bytes):
        with pytest.raises(InvalidXMLException):
            process_xml(malformed_xml_bytes)
