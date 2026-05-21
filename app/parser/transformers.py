def build_summary(vulnerabilities):

    summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for vuln in vulnerabilities:

        severity = vuln.severity.lower()

        if severity in summary:
            summary[severity] += 1

    return summary


def vulnerabilities_to_json(vulnerabilities):

    return [
        {
            "severity": vuln.severity,
            "cve": vuln.cve,
            "host": vuln.host
        }
        for vuln in vulnerabilities
    ]


def build_response(vulnerabilities):

    return {
        "summary": build_summary(vulnerabilities),
        "vulnerabilities": vulnerabilities_to_json(
            vulnerabilities
        )
    }