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

            "cvss_score": vuln.cvss_score,

            "cve": vuln.cve,

            "host": vuln.host,

            "port": vuln.port,

            "name": vuln.name,

            "family": vuln.family,

            "description": vuln.description,

            "impact": vuln.impact,

            "solution": vuln.solution
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