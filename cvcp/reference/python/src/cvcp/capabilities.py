"""
CVCP Capability Model

Implements the RuntimeCapabilities model for the CVCP Python SDK as defined by
RFC-0014: Capability Discovery & Feature Negotiation.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Tuple

from .errors import CVCPProtocolError

_VERSION_REGEX = re.compile(r"^\d+\.\d+\.\d+$")
_IDENTIFIER_REGEX = re.compile(r"^[A-Za-z0-9_-]+$")


def _normalize_collection(name: str, items: Iterable[Any]) -> Tuple[str, ...]:
    """
    Normalizes a collection of capability identifiers.
    Removes duplicates, trims whitespace, and sorts lexicographically.
    Rejects None, empty strings, non-string types, and malformed identifiers.
    """
    if items is None:
        raise CVCPProtocolError(
            "CVCP_ERR_EVENT_SCHEMA",
            f"Collection '{name}' cannot be None."
        )

    normalized_items = set()
    for item in items:
        if item is None:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Collection '{name}' contains None."
            )
        if not isinstance(item, str):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Collection '{name}' contains non-string value: {type(item).__name__}"
            )
        
        stripped = item.strip()
        if not stripped:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Collection '{name}' contains an empty string."
            )
        if not _IDENTIFIER_REGEX.match(stripped):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Collection '{name}' contains malformed identifier: {stripped}"
            )
            
        normalized_items.add(stripped)
        
    return tuple(sorted(normalized_items))


@dataclass(frozen=True, slots=True)
class RuntimeCapabilities:
    """
    Immutable representation of a runtime's advertised protocol capabilities.
    """
    version: str
    features: Tuple[str, ...] = ()
    profiles: Tuple[str, ...] = ()
    extensions: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """
        Validates the version format and normalizes collections after initialization.
        """
        if not self.version or not isinstance(self.version, str):
            raise CVCPProtocolError(
                "CVCP_ERR_PROTOCOL_VERSION",
                "Version must be a non-empty string."
            )
            
        if not _VERSION_REGEX.match(self.version):
            raise CVCPProtocolError(
                "CVCP_ERR_PROTOCOL_VERSION",
                f"Malformed protocol version: {self.version}"
            )

        object.__setattr__(self, "features", _normalize_collection("features", self.features))
        object.__setattr__(self, "profiles", _normalize_collection("profiles", self.profiles))
        object.__setattr__(self, "extensions", _normalize_collection("extensions", self.extensions))

    @classmethod
    def create(
        cls,
        version: str,
        features: Iterable[str],
        profiles: Iterable[str],
        extensions: Iterable[str]
    ) -> 'RuntimeCapabilities':
        """
        Constructs a RuntimeCapabilities object from iterables.
        """
        return cls(
            version=version,
            features=tuple(features),
            profiles=tuple(profiles),
            extensions=tuple(extensions)
        )

    def supports_feature(self, name: str) -> bool:
        """Checks if a feature is supported."""
        return name.strip() in self.features

    def supports_profile(self, name: str) -> bool:
        """Checks if a profile is supported."""
        return name.strip() in self.profiles

    def supports_extension(self, name: str) -> bool:
        """Checks if an extension is supported."""
        return name.strip() in self.extensions

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes capabilities to a deterministic dictionary representation.
        """
        return {
            "version": self.version,
            "features": list(self.features),
            "profiles": list(self.profiles),
            "extensions": list(self.extensions)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuntimeCapabilities':
        """
        Deserializes capabilities from a dictionary.
        """
        if not isinstance(data, dict):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                "Input data must be a dictionary."
            )
            
        return cls.create(
            version=data.get("version"),  # type: ignore
            features=data.get("features", []),
            profiles=data.get("profiles", []),
            extensions=data.get("extensions", [])
        )

    def to_json(self) -> str:
        """
        Serializes capabilities to a deterministic JSON string.
        """
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'RuntimeCapabilities':
        """
        Deserializes capabilities from a JSON string.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as err:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Malformed JSON: {str(err)}"
            )
        return cls.from_dict(data)
