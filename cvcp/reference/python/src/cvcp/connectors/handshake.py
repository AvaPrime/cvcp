"""
Connector Handshake.
Builds on the existing RFC-0014 handshake implementation.
"""
from typing import List, Tuple
from ..handshake import (
    HandshakeParser,
    HEADER_VERSION,
    HEADER_FEATURES,
    HEADER_PROFILES,
    HEADER_EXTENSIONS
)
from ..capabilities import RuntimeCapabilities

class ConnectorHandshake:
    """
    Provides handshake operations for connectors.
    """
    @staticmethod
    def parse_headers(headers: List[Tuple[str, str]]) -> RuntimeCapabilities:
        """
        Parses and validates handshake headers.
        """
        return HandshakeParser.parse_headers(headers)

    @staticmethod
    def serialize_headers(caps: RuntimeCapabilities) -> List[Tuple[str, str]]:
        """
        Serializes capabilities into handshake headers.
        """
        return HandshakeParser.serialize_headers(caps)

__all__ = [
    "ConnectorHandshake",
    "HEADER_VERSION",
    "HEADER_FEATURES",
    "HEADER_PROFILES",
    "HEADER_EXTENSIONS"
]
