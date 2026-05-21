from app.parser.parser_adapter import process_xml
from app.storage.memory_store import save_report

def create_report(xml_content):

    parsed_data = process_xml(xml_content)

    report_id = save_report(parsed_data)

    return report_id

