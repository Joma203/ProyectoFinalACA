from app.parser.models import Vulnerability


class OpenVASParser:

    def __init__(self, root):

        self.root = root

    def parse_vulnerabilities(self):

        vulnerabilities = []

        results = self.root.findall(".//{*}result")

        print("RESULTS FOUND:", len(results))

        for result in results:

            vulnerability = self._parse_result(result)

            if vulnerability:

                vulnerabilities.append(vulnerability)

        return vulnerabilities

    def _parse_result(self, result):

        host = result.findtext(
            ".//{*}host",
            default="unknown"
        ).strip()

        port = result.findtext(
            ".//{*}port",
            default="unknown"
        ).strip()

        severity_score = result.findtext(
            ".//{*}severity",
            default="0"
        ).strip()

        cve = result.findtext(
            ".//{*}cve",
            default="N/A"
        ).strip()

        name = result.findtext(
            ".//{*}nvt/{*}name",
            default="Unknown Vulnerability"
        ).strip()

        family = result.findtext(
            ".//{*}nvt/{*}family",
            default="Unknown"
        ).strip()

        cvss_score = result.findtext(
            ".//{*}nvt/{*}cvss_base",
            default="0"
        ).strip()

        tags_text = result.findtext(
            ".//{*}tags",
            default=""
        )

        parsed_tags = self._parse_tags(tags_text)

        description = parsed_tags.get(
            "summary",
            "No description available."
        )

        impact = parsed_tags.get(
            "impact",
            "No impact information."
        )

        solution = parsed_tags.get(
            "solution",
            "No solution available."
        )

        severity = self._map_severity(
            severity_score
        )

        cve = self._normalize_cve(cve)

        try:
            cvss_score = float(cvss_score)

        except ValueError:
            cvss_score = 0.0

        return Vulnerability(

            severity=severity,

            cvss_score=cvss_score,

            cve=cve,

            host=host,

            port=port,

            name=name,

            family=family,

            description=description,

            impact=impact,

            solution=solution
        )

    def _parse_tags(self, tags_text):

        parsed = {}

        if not tags_text:
            return parsed

        items = tags_text.split("|")

        for item in items:

            if "=" in item:

                key, value = item.split("=", 1)

                parsed[key.strip()] = value.strip()

        return parsed

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