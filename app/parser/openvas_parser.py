from app.parser.models import Vulnerability


class OpenVASParser:

    def __init__(self, root):
        self.root = root

    def parse_vulnerabilities(self):

        vulnerabilities = []

        results = self.root.findall(".//result")

        for result in results:

            vulnerability = self._parse_result(result)

            if vulnerability:
                vulnerabilities.append(vulnerability)

        return vulnerabilities

    def _parse_result(self, result):

        host = result.findtext("host", default="unknown")

        severity_score = result.findtext(
            "severity",
            default="0"
        )

        cve = result.findtext(
            ".//cve",
            default="N/A"
        )

        severity = self._map_severity(
            severity_score
        )

        cve = self._normalize_cve(cve)

        return Vulnerability(
            severity=severity,
            cve=cve,
            host=host
        )

    def _normalize_cve(self, cve):

        if not cve:
            return "N/A"

        cve = cve.strip()

        if cve.upper() == "NOCVE":
            return "N/A"

        return cve

    def _map_severity(self, severity_score):

        try:
            score = float(severity_score)

        except ValueError:
            return "Unknown"

        if score >= 9:
            return "Critical"

        elif score >= 7:
            return "High"

        elif score >= 4:
            return "Medium"

        return "Low"