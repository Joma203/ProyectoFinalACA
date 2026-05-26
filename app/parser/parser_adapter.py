import tempfile

from app.parser.xml_loader import load_xml
from app.parser.openvas_parser import OpenVASParser
from app.parser.response_builder import build_response


def process_xml(xml_content):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".xml"
    ) as temp_file:

        temp_file.write(xml_content)

        temp_path = temp_file.name

    root = load_xml(temp_path)

    parser = OpenVASParser(root)

    vulnerabilities = parser.parse_vulnerabilities()

    response = build_response(vulnerabilities)

    return response