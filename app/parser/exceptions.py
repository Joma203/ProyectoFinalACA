class InvalidXMLException(Exception):
    """Raised when XML format is invalid."""
    pass


class OpenVASFormatException(Exception):
    """Raised when XML is not a valid OpenVAS report."""
    pass