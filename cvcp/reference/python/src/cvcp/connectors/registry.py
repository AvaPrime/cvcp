"""
Connector Registry.

Lightweight registry for declaring supported protocol versions, profiles, features, and extensions
for different transport connectors.
"""
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from ..capabilities import RuntimeCapabilities
from .errors import CVCPProtocolError

@dataclass(frozen=True, slots=True)
class ConnectorDescriptor:
    """
    Declares a connector's immutable protocol capabilities and metadata.
    """
    name: str
    implementation_id: str
    transport: str
    supported_versions: Tuple[str, ...]
    supported_profiles: Tuple[str, ...]
    supported_features: Tuple[str, ...]
    supported_extensions: Tuple[str, ...]

    def to_capabilities(self, version: str) -> RuntimeCapabilities:
        """
        Creates a RuntimeCapabilities object for a specific supported version.
        """
        if version not in self.supported_versions:
            raise CVCPProtocolError("CVCP_ERR_PROTOCOL_VERSION", f"Version {version} not supported by this connector.")
        return RuntimeCapabilities.create(
            version=version,
            features=list(self.supported_features),
            profiles=list(self.supported_profiles),
            extensions=list(self.supported_extensions)
        )

class ConnectorRegistry:
    """
    Lightweight connector registry.
    """
    _registry: Dict[str, ConnectorDescriptor] = {}
    _implementations: Dict[str, str] = {}

    @classmethod
    def register(cls, descriptor: ConnectorDescriptor) -> None:
        """
        Registers a connector after validation.
        """
        if not descriptor.name:
            raise ValueError("Connector name cannot be empty.")
        if not descriptor.implementation_id:
            raise ValueError("Connector implementation_id cannot be empty.")
        if descriptor.name in cls._registry:
            raise ValueError(f"Connector '{descriptor.name}' is already registered.")
        if descriptor.implementation_id in cls._implementations:
            raise ValueError(f"Implementation ID '{descriptor.implementation_id}' is already registered by '{cls._implementations[descriptor.implementation_id]}'.")
        
        if not descriptor.supported_versions:
            raise ValueError("Connector must support at least one protocol version.")
            
        cls._registry[descriptor.name] = descriptor
        cls._implementations[descriptor.implementation_id] = descriptor.name

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregisters a connector by name.
        """
        if name in cls._registry:
            descriptor = cls._registry.pop(name)
            cls._implementations.pop(descriptor.implementation_id, None)

    @classmethod
    def get(cls, name: str) -> Optional[ConnectorDescriptor]:
        """
        Retrieves a registered connector by name.
        """
        return cls._registry.get(name)

    @classmethod
    def list(cls) -> Tuple[ConnectorDescriptor, ...]:
        """
        Returns an immutable snapshot of all registered connectors.
        """
        return tuple(cls._registry.values())
        
    @classmethod
    def exists(cls, name: str) -> bool:
        """
        Checks if a connector exists.
        """
        return name in cls._registry

    @classmethod
    def clear(cls) -> None:
        """
        Clears the registry.
        """
        cls._registry.clear()
        cls._implementations.clear()

__all__ = ["ConnectorDescriptor", "ConnectorRegistry"]
