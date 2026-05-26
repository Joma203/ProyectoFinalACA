from app.parser.xml_loader import load_xml
from app.parser.openvas_parser import OpenVASParser
from app.parser.transformers import build_response


def test_parse_valid_xml():

    root = load_xml(
        "tests/mock_reports/sample_report.xml"
    )

    parser = OpenVASParser(root)

    vulnerabilities = parser.parse_vulnerabilities()

    response = build_response(vulnerabilities)

    assert len(vulnerabilities) == 3

    assert response["summary"]["critical"] == 1
    assert response["summary"]["high"] == 1
    assert response["summary"]["low"] == 1