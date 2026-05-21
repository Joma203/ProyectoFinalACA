import uuid

REPORTS = {}

def save_report(data):

    report_id = str(uuid.uuid4())

    REPORTS[report_id] = data

    return report_id

def get_report(report_id):

    return REPORTS.get(report_id)