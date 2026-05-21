from dataclasses import dataclass


@dataclass
class Vulnerability:
    severity: str
    cve: str
    host: str