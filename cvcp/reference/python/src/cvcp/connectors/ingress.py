"""
Ingress Connector Framework.

Exposes a transport-neutral interface for capability negotiation.
"""
from typing import List, Tuple
from ..capabilities import RuntimeCapabilities
from ..negotiation import negotiate, NegotiationResult
from .handshake import ConnectorHandshake

class IngressConnector:
    """
    Ingress connector primitive for receiving remote capabilities and
    negotiating protocol compatibility.
    """
    def __init__(self, local_capabilities: RuntimeCapabilities):
        """
        Initializes the IngressConnector with the local runtime capabilities.
        """
        self.local_capabilities = local_capabilities

    def negotiate(self, remote_capabilities: RuntimeCapabilities) -> NegotiationResult:
        """
        Negotiates capabilities with a remote participant.
        """
        return negotiate(self.local_capabilities, remote_capabilities)

    def negotiate_from_headers(self, headers: List[Tuple[str, str]]) -> NegotiationResult:
        """
        Parses handshake headers and negotiates capabilities.
        """
        remote_caps = ConnectorHandshake.parse_headers(headers)
        return self.negotiate(remote_caps)

__all__ = ["IngressConnector"]
