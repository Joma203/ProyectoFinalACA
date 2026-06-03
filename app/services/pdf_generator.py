
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def calculate_risk(summary):
    if summary["critical"] > 0:
        return "HIGH"

    if summary["high"] > 3:
        return "HIGH"

    if summary["medium"] > 0:
        return "MEDIUM"

    return "LOW"


def get_severity_color(severity):
    severity = severity.lower()

    if severity == "critical":
        return colors.red

    if severity == "high":
        return colors.orange

    if severity == "medium":
        return colors.yellow

    if severity == "low":
        return colors.lightgreen

    return colors.lightgrey


def generate_pdf(report, output_path):
    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    elements = []

    summary = report["summary"]
    vulnerabilities = report["vulnerabilities"]

    # ==================================================
    # COVER PAGE
    # ==================================================

    total = (
        summary["critical"]
        + summary["high"]
        + summary["medium"]
        + summary["low"]
    )

    overall_risk = calculate_risk(summary)

    today = datetime.now().strftime("%Y-%m-%d")

    elements.append(
        Paragraph(
            "OpenVAS Security Assessment Report",
            styles["Title"],
        )
    )

    elements.append(Spacer(1, 80))

    elements.append(
        Paragraph(
            "Executive Vulnerability Assessment",
            styles["Heading1"],
        )
    )

    elements.append(Spacer(1, 40))

    elements.append(
        Paragraph(
            f"Overall Risk Level: {overall_risk}",
            styles["Heading2"],
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated on: {today}",
            styles["Normal"],
        )
    )

    elements.append(PageBreak())

    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================

    elements.append(
        Paragraph(
            "OpenVAS Executive Summary",
            styles["Title"],
        )
    )

    elements.append(Spacer(1, 20))

    summary_text = (
        f"The assessment identified a total of "
        f"{total} vulnerabilities across the scanned assets, "
        f"including {summary['critical']} critical, "
        f"{summary['high']} high, "
        f"{summary['medium']} medium and "
        f"{summary['low']} low severity findings. "
        "Critical and high severity vulnerabilities "
        "should be prioritized for remediation due "
        "to their potential impact on system security."
    )

    elements.append(
        Paragraph(
            summary_text,
            styles["BodyText"],
        )
    )

    elements.append(Spacer(1, 30))

    summary_table = Table(
        [
            ["Severity", "Count"],
            ["Critical", summary["critical"]],
            ["High", summary["high"]],
            ["Medium", summary["medium"]],
            ["Low", summary["low"]],
        ],
        colWidths=[150, 100],
    )

    summary_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]

    severities = ["critical", "high", "medium", "low"]

    for row, severity in enumerate(severities, start=1):
        summary_style.append(
            (
                "BACKGROUND",
                (0, row),
                (-1, row),
                get_severity_color(severity),
            )
        )

    summary_table.setStyle(TableStyle(summary_style))

    elements.append(summary_table)

    elements.append(Spacer(1, 30))

    elements.append(PageBreak())

    for vuln in vulnerabilities:
        severity_color = get_severity_color(vuln["severity"])

        elements.append(
            Paragraph(
                vuln["name"],
                styles["Heading1"],
            )
        )

        vuln_data = [
            ["Field", "Value"],
            ["Severity", vuln["severity"]],
            ["CVSS Score", str(vuln["cvss_score"])],
            [
                "CVE",
                Paragraph(
                    vuln["cve"],
                    styles["BodyText"],
                ),
            ],
            ["Host", vuln["host"]],
            ["Port", vuln["port"]],
            ["Family", vuln["family"]],
            [
                "Description",
                Paragraph(
                    vuln["description"],
                    styles["BodyText"],
                ),
            ],
            [
                "Impact",
                Paragraph(
                    vuln["impact"],
                    styles["BodyText"],
                ),
            ],
            [
                "Solution",
                Paragraph(
                    vuln["solution"],
                    styles["BodyText"],
                ),
            ],
        ]

        vuln_table = Table(
            vuln_data,
            colWidths=[150, 350],
        )

        vuln_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BACKGROUND", (0, 1), (0, -1), severity_color),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ]
            )
        )

        elements.append(vuln_table)
        elements.append(PageBreak())

    doc.build(elements)
