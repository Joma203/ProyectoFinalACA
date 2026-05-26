from dataclasses import dataclass


@dataclass
class Vulnerability:

    severity: str

    cvss_score: float

    cve: str

    host: str

    port: str

    name: str

    family: str

    description: str

    impact: str

    solution: str