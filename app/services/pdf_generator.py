from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(report, output_path):

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    elements = []

    summary = report["summary"]

    elements.append(
        Paragraph(
            "OpenVAS Executive Summary",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"Critical: {summary['critical']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"High: {summary['high']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Medium: {summary['medium']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Low: {summary['low']}",
            styles["Normal"]
        )
    )

    doc.build(elements)