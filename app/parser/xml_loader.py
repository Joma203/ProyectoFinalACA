import xml.etree.ElementTree as ET

from app.parser.exceptions import InvalidXMLException


def load_xml(file_path: str):

    try:
        tree = ET.parse(file_path)
        return tree.getroot()

    except ET.ParseError as e:
        raise InvalidXMLException(
            f"Malformed XML: {str(e)}"
        )
