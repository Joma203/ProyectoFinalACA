from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(report, output_path):

    doc = SimpleDocTemplate(output_path)

    styles = getSampleStyleSheet()

    elements = []

    summary = report["summary"]

    vulnerabilities = report["vulnerabilities"]

    elements.append(
        Paragraph(
            "OpenVAS Executive Summary",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    summary_data = [

        ["Severity", "Count"],

        ["Critical", summary["critical"]],

        ["High", summary["high"]],

        ["Medium", summary["medium"]],

        ["Low", summary["low"]]
    ]

    summary_table = Table(summary_data)

    summary_table.setStyle(

        TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ])
    )
    elements.append(summary_table)

    elements.append(Spacer(1, 30))

    elements.append(PageBreak())

    for vuln in vulnerabilities:
        elements.append(
            Paragraph(
                vuln["name"],
                styles["Heading1"]
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
                    styles["BodyText"]
                )
            ],

            ["Host", vuln["host"]],

            ["Port", vuln["port"]],

            ["Family", vuln["family"]],

            [
                "Description",
                Paragraph(
                    vuln["description"],
                    styles["BodyText"]
                )
            ],
            [
                "Impact",

                Paragraph(
                    vuln["impact"],
                    styles["BodyText"]
                )
            ],
            [
                "Solution",

                Paragraph(
                    vuln["solution"],
                    styles["BodyText"]
                )
            ]

        ]

        vuln_table = Table(
            vuln_data,
            colWidths=[150, 350]
        )

        vuln_table.setStyle(

            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

                ("GRID", (0, 0), (-1, -1), 1, colors.black),

                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

                ("VALIGN", (0, 0), (-1, -1), "TOP"),

                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ])
        )

        elements.append(vuln_table)
        elements.append(PageBreak())

    doc.build(elements)
