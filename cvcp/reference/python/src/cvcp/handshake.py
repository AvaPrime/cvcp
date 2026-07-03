"""
CVCP Protocol Handshake Headers
"""
from typing import List, Tuple, Dict
from .capabilities import RuntimeCapabilities
from .errors import CVCPProtocolError
import re

HEADER_VERSION = "CVCP-Version"
HEADER_FEATURES = "CVCP-Features"
HEADER_PROFILES = "CVCP-Profiles"
HEADER_EXTENSIONS = "CVCP-Extensions"

class HandshakeParser:
    @staticmethod
    def parse_headers(headers: List[Tuple[str, str]]) -> RuntimeCapabilities:
        """
        Parses and validates handshake headers.
        """
        seen_keys = set()
        parsed: Dict[str, str] = {}
        
        for key, value in headers:
            norm_key = key.strip().upper()
            if norm_key in seen_keys:
                raise CVCPProtocolError("CVCP_ERR_NEGOTIATION", f"Duplicate header: {key}")
            seen_keys.add(norm_key)
            parsed[norm_key] = value

        version = parsed.get(HEADER_VERSION.upper())
        if not version:
            raise CVCPProtocolError("CVCP_ERR_PROTOCOL_VERSION", f"Missing {HEADER_VERSION} header")
            
        version = version.strip()
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            raise CVCPProtocolError("CVCP_ERR_PROTOCOL_VERSION", f"Malformed {HEADER_VERSION}: {version}")

        def _split_and_clean(val: str) -> List[str]:
            return [v.strip() for v in val.split(",") if v.strip()]

        features = _split_and_clean(parsed.get(HEADER_FEATURES.upper(), ""))
        profiles = _split_and_clean(parsed.get(HEADER_PROFILES.upper(), ""))
        extensions = _split_and_clean(parsed.get(HEADER_EXTENSIONS.upper(), ""))

        return RuntimeCapabilities.create(
            version=version,
            features=features,
            profiles=profiles,
            extensions=extensions
        )

    @staticmethod
    def serialize_headers(caps: RuntimeCapabilities) -> List[Tuple[str, str]]:
        """
        Serializes capabilities into handshake headers.
        """
        headers = [(HEADER_VERSION, caps.version)]
        if caps.features:
            headers.append((HEADER_FEATURES, ",".join(caps.features)))
        if caps.profiles:
            headers.append((HEADER_PROFILES, ",".join(caps.profiles)))
        if caps.extensions:
            headers.append((HEADER_EXTENSIONS, ",".join(caps.extensions)))
        return headers
