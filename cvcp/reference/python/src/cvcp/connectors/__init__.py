"""
CVCP Ingress Connector Framework

Provides transport-agnostic connector primitives for capability discovery and negotiation.
"""
from .ingress import IngressConnector
from .registry import ConnectorRegistry, ConnectorDescriptor
from .errors import CVCPProtocolError

__all__ = [
    "IngressConnector",
    "ConnectorRegistry",
    "ConnectorDescriptor",
    "CVCPProtocolError",
]
