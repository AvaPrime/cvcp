"""
CVCP v1.1.0 Multi-Stage Parser Validation Engine
"""
import hashlib
import json
import re
from typing import Dict, Any

from .errors import CVCPProtocolError
from .models import EventEnvelope

class CVCPEventParser:
    ISO_8601_Z_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$")
    UUIDV7_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")

    @classmethod
    def parse_and_verify(cls, raw_wire_data: str) -> EventEnvelope:
        # Phase 1: Wire Parse
        try:
            parsed_json = json.loads(raw_wire_data)
        except json.JSONDecodeError as err:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SYNTAX",
                f"Malformed JSON wire input: {str(err)}"
            )

        # Phase 2: Schema Match (Root fields and structure)
        if not isinstance(parsed_json, dict):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                "Ingress payload must be a JSON object"
            )

        required_root_keys = {
            "protocol", "event_id", "aggregate_id", "aggregate_type", "event_version",
            "graph_version", "timestamp", "causation_id", "correlation_id",
            "payload_type", "payload_schema", "payload", "metadata", "integrity"
        }

        missing_keys = required_root_keys - parsed_json.keys()
        if missing_keys:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Missing structural root fields: {sorted(list(missing_keys))}"
            )

        extra_keys = parsed_json.keys() - required_root_keys
        if extra_keys:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Payload contains unrecognized properties: {sorted(list(extra_keys))}"
            )

        # Validate types of structured sub-dictionaries
        for dict_key in ("protocol", "payload", "metadata", "integrity"):
            if not isinstance(parsed_json[dict_key], dict):
                raise CVCPProtocolError(
                    "CVCP_ERR_EVENT_SCHEMA",
                    f"Root field '{dict_key}' must be a JSON object"
                )

        try:
            envelope = EventEnvelope(
                protocol=parsed_json["protocol"],
                event_id=parsed_json["event_id"],
                aggregate_id=parsed_json["aggregate_id"],
                aggregate_type=parsed_json["aggregate_type"],
                event_version=int(parsed_json["event_version"]),
                graph_version=int(parsed_json["graph_version"]),
                timestamp=parsed_json["timestamp"],
                causation_id=parsed_json["causation_id"],
                correlation_id=parsed_json["correlation_id"],
                payload_type=parsed_json["payload_type"],
                payload_schema=parsed_json["payload_schema"],
                payload=parsed_json["payload"],
                metadata=parsed_json["metadata"]
            )
            integrity_block = parsed_json["integrity"]
        except (ValueError, TypeError) as err:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SCHEMA",
                f"Root field type mismatch: {str(err)}"
            )

        # Phase 3 & 4: Canonicalization & Cryptographic Integrity Check
        if integrity_block.get("canonicalization") != "RFC8785":
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_CANONICALIZATION",
                "Unsupported canonicalization layout. RFC8785 expected."
            )
        if integrity_block.get("algorithm") != "SHA-256":
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_CANONICALIZATION",
                "Unsupported cryptographic algorithm. SHA-256 expected."
            )

        computed_checksum = hashlib.sha256(envelope.to_jcs_bytes()).hexdigest()
        if integrity_block.get("checksum") != computed_checksum:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_CHECKSUM",
                f"Payload integrity hash validation failed. Expected: {computed_checksum}"
            )

        # Phase 5: Semantic Verification
        cls._validate_semantics(envelope)

        return envelope

    @classmethod
    def _validate_semantics(cls, env: EventEnvelope) -> None:
        """Enforces version bounds, UUID shapes, and strict timeline format constraints."""
        spec = env.protocol.get("spec")
        version = env.protocol.get("version")

        if spec != "CVCP":
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_PROTOCOL_VERSION",
                f"Unsupported protocol spec: {spec}"
            )
        if not version or not re.match(r"^1\.1\.\d+$", version):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_PROTOCOL_VERSION",
                f"Unsupported protocol version configuration: {version}"
            )

        if not env.event_id.startswith("evt_") or not cls.UUIDV7_REGEX.match(env.event_id[4:]):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SEMANTICS",
                f"event_id '{env.event_id}' must be a valid 'evt_' prefixed UUIDv7."
            )
        if not env.correlation_id.startswith("corr_") or not cls.UUIDV7_REGEX.match(env.correlation_id[5:]):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SEMANTICS",
                f"correlation_id '{env.correlation_id}' must be a valid 'corr_' prefixed UUIDv7."
            )

        if not cls.ISO_8601_Z_REGEX.match(env.timestamp):
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SEMANTICS",
                f"Timestamp '{env.timestamp}' breaks strict millisecond UTC Z compliance rules."
            )
        if env.event_version < 1:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SEMANTICS",
                "event_version metric must be >= 1."
            )
        if env.graph_version < 0:
            raise CVCPProtocolError(
                "CVCP_ERR_EVENT_SEMANTICS",
                "graph_version metric must be >= 0."
            )
