#!/usr/bin/env python3
"""
Automated bootstrap tool for Milestone 1 workspace setup.
Computes and populates test-vectors with mathematically valid hashes.
"""
import os
import json
import hashlib

# 1. Directory Structure Setup
DIRS = [
    "cvcp/specs/schemas",
    "cvcp/specs/test-vectors",
    "cvcp/sdk/python/src/cvcp",
    "cvcp/sdk/python/tests"
]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

# Helper serialization function for seed canonicalization
def compute_jcs_hash(data: dict) -> str:
    from cvcp.models import canonicalize_rfc8785
    # Remove integrity key if present
    payload_copy = data.copy()
    if "integrity" in payload_copy:
        payload_copy.pop("integrity")
    jcs_str = canonicalize_rfc8785(payload_copy)
    return hashlib.sha256(jcs_str.encode("utf-8")).hexdigest()

# Define raw payloads
raw_payload_base = {
    "protocol": {"spec": "CVCP", "version": "1.1.0"},
    "event_id": "evt_0197b80c-f7b8-7b31-b913-99a21b4f881a",
    "aggregate_id": "opp_0197b80d-01f2-7a22-bc11-88f21b4a992b",
    "aggregate_type": "OPPORTUNITY",
    "event_version": 1,
    "graph_version": 142,
    "timestamp": "2026-07-02T14:32:00.000Z",
    "causation_id": "evt_0197b80a-e211-7f12-aa34-11b22c3d4e5f",
    "correlation_id": "corr_0197b80a-e211-7f12-aa34-00a11b22c3d4",
    "payload_type": "OpportunityStatusChanged",
    "payload_schema": "cvcp://schemas/opportunity-status-changed/1.0.0",
    "payload": {"new_status": "PROMOTED"},
    "metadata": {"origin_node": "connector_github_main"}
}

# 2. Write Python Source Files
with open("cvcp/sdk/python/src/cvcp/__init__.py", "w") as f:
    f.write('__version__ = "1.1.0"\n')

with open("cvcp/sdk/python/src/cvcp/errors.py", "w") as f:
    f.write('class CVCPProtocolError(Exception):\n    def __init__(self, error_code: str, message: str):\n        self.error_code = error_code\n        self.message = message\n        super().__init__(f"[{error_code}] {message}")\n')

with open("cvcp/sdk/python/src/cvcp/models.py", "w") as f:
    f.write('''import json
from dataclasses import dataclass, asdict
from typing import Dict, Any

def canonicalize_rfc8785(data: Any) -> str:
    if isinstance(data, dict):
        items = []
        for k in sorted(data.keys()):
            v = data[k]
            items.append(f"{json.dumps(k, ensure_ascii=False)}:{canonicalize_rfc8785(v)}")
        return "{" + ",".join(items) + "}"
    elif isinstance(data, list):
        return "[" + ",".join(canonicalize_rfc8785(x) for x in data) + "]"
    elif isinstance(data, bool):
        return "true" if data else "false"
    elif data is None:
        return "null"
    elif isinstance(data, (int, float)):
        if isinstance(data, float) and data.is_integer():
            return str(int(data))
        return str(data)
    elif isinstance(data, str):
        return json.dumps(data, ensure_ascii=False)
    else:
        raise ValueError(f"Type {type(data)} is not supported under RFC 8785")

@dataclass(frozen=True)
class EventEnvelope:
    protocol: Dict[str, str]
    event_id: str
    aggregate_id: str
    aggregate_type: str
    event_version: int
    graph_version: int
    timestamp: str
    causation_id: str
    correlation_id: str
    payload_type: str
    payload_schema: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_jcs_bytes(self) -> bytes:
        raw_dict = asdict(self)
        return canonicalize_rfc8785(raw_dict).encode("utf-8")
''')

with open("cvcp/sdk/python/src/cvcp/parser.py", "w") as f:
    f.write('''import hashlib
import json
import re
from typing import Dict, Any

from .errors import CVCPProtocolError
from .models import EventEnvelope

class CVCPEventParser:
    ISO_8601_Z_REGEX = re.compile(r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(\\.\\d{3})?Z$")
    UUIDV7_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")

    @classmethod
    def parse_and_verify(cls, raw_wire_data: str) -> EventEnvelope:
        try:
            parsed_json = json.loads(raw_wire_data)
        except json.JSONDecodeError as err:
            raise CVCPProtocolError("CVCP_ERR_EVENT_SYNTAX", f"Malformed JSON wire input: {str(err)}")

        if not isinstance(parsed_json, dict):
            raise CVCPProtocolError("CVCP_ERR_EVENT_SCHEMA", "Ingress payload must be a JSON object")

        required_root_keys = {
            "protocol", "event_id", "aggregate_id", "aggregate_type", "event_version",
            "graph_version", "timestamp", "causation_id", "correlation_id",
            "payload_type", "payload_schema", "payload", "metadata", "integrity"
        }

        missing_keys = required_root_keys - parsed_json.keys()
        if missing_keys:
            raise CVCPProtocolError("CVCP_ERR_EVENT_SCHEMA", f"Missing structural root fields: {sorted(list(missing_keys))}")

        extra_keys = parsed_json.keys() - required_root_keys
        if extra_keys:
            raise CVCPProtocolError("CVCP_ERR_EVENT_SCHEMA", f"Payload contains unrecognized properties: {sorted(list(extra_keys))}")

        for dict_key in ("protocol", "payload", "metadata", "integrity"):
            if not isinstance(parsed_json[dict_key], dict):
                raise CVCPProtocolError("CVCP_ERR_EVENT_SCHEMA", f"Root field '{dict_key}' must be a JSON object")

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
            raise CVCPProtocolError("CVCP_ERR_EVENT_SCHEMA", f"Root field type mismatch: {str(err)}")

        if integrity_block.get("canonicalization") != "RFC8785":
            raise CVCPProtocolError("CVCP_ERR_EVENT_CANONICALIZATION", "Unsupported canonicalization layout. RFC8785 expected.")
        if integrity_block.get("algorithm") != "SHA-256":
            raise CVCPProtocolError("CVCP_ERR_EVENT_CANONICALIZATION", "Unsupported cryptographic algorithm. SHA-256 expected.")

        computed_checksum = hashlib.sha256(envelope.to_jcs_bytes()).hexdigest()
        if integrity_block.get("checksum") != computed_checksum:
            raise CVCPProtocolError("CVCP_ERR_EVENT_CHECKSUM", f"Payload integrity hash validation failed. Expected: {computed_checksum}")

        cls._validate_semantics(envelope)
        return envelope

    @classmethod
    def _validate_semantics(cls, env: EventEnvelope) -> None:
        spec = env.protocol.get("spec")
        version = env.protocol.get("version")

        if spec != "CVCP":
            raise CVCPProtocolError("CVCP_ERR_EVENT_PROTOCOL_VERSION", f"Unsupported protocol spec: {spec}")
        if not version or not re.match(r"^1\\.1\\.\\d+$", version):
            raise CVCPProtocolError("CVCP_ERR_EVENT_PROTOCOL_VERSION", f"Unsupported protocol version configuration: {version}")

        if not env.event_id.startswith("evt_") or not cls.UUIDV7_REGEX.match(env.event_id[4:]):
            raise CVCPProtocolError("CVCP_ERR_EVENT_SEMANTICS", f"event_id '{env.event_id}' must be a valid 'evt_' prefixed UUIDv7.")
        if not env.correlation_id.startswith("corr_") or not cls.UUIDV7_REGEX.match(env.correlation_id[5:]):
            raise CVCPProtocolError("CVCP_ERR_EVENT_SEMANTICS", f"correlation_id '{env.correlation_id}' must be a valid 'corr_' prefixed UUIDv7.")

        if not cls.ISO_8601_Z_REGEX.match(env.timestamp):
            raise CVCPProtocolError("CVCP_ERR_EVENT_SEMANTICS", f"Timestamp '{env.timestamp}' breaks strict millisecond UTC Z compliance rules.")
        if env.event_version < 1:
            raise CVCPProtocolError("CVCP_ERR_EVENT_SEMANTICS", "event_version metric must be >= 1.")
        if env.graph_version < 0:
            raise CVCPProtocolError("CVCP_ERR_EVENT_SEMANTICS", "graph_version metric must be >= 0.")
''')

with open("cvcp/sdk/python/tests/test_parser.py", "w") as f:
    f.write('''import os
import json
import pytest

from cvcp.errors import CVCPProtocolError
from cvcp.parser import CVCPEventParser

VECTORS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../specs/test-vectors"))

def load_vector(filename: str) -> str:
    path = os.path.join(VECTORS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_stage_valid_vector():
    wire_data = load_vector("event-valid-001.json")
    envelope = CVCPEventParser.parse_and_verify(wire_data)
    assert envelope.event_id == "evt_0197b80c-f7b8-7b31-b913-99a21b4f881a"
    assert envelope.payload["new_status"] == "PROMOTED"

def test_stage_missing_id_vector():
    wire_data = load_vector("event-invalid-missing-id.json")
    with pytest.raises(CVCPProtocolError) as err:
        CVCPEventParser.parse_and_verify(wire_data)
    assert err.value.error_code == "CVCP_ERR_EVENT_SCHEMA"

def test_stage_invalid_checksum_vector():
    wire_data = load_vector("event-invalid-checksum.json")
    with pytest.raises(CVCPProtocolError) as err:
        CVCPEventParser.parse_and_verify(wire_data)
    assert err.value.error_code == "CVCP_ERR_EVENT_CHECKSUM"
''')

# Inject source logic programmatically in this bootstrap script
import sys
sys.path.insert(0, os.path.abspath("cvcp/sdk/python/src"))
from cvcp.models import canonicalize_rfc8785

# Compute static valid checksum based on standard JCS serialization
valid_checksum = compute_jcs_hash(raw_payload_base)

# Build out complete schemas and test vectors
valid_vector = raw_payload_base.copy()
valid_vector["integrity"] = {
    "algorithm": "SHA-256",
    "canonicalization": "RFC8785",
    "checksum": valid_checksum
}

invalid_missing_id = raw_payload_base.copy()
invalid_missing_id.pop("event_id")
invalid_missing_id["integrity"] = {
    "algorithm": "SHA-256",
    "canonicalization": "RFC8785",
    "checksum": "0000000000000000000000000000000000000000000000000000000000000000"
}

invalid_checksum = raw_payload_base.copy()
invalid_checksum["integrity"] = {
    "algorithm": "SHA-256",
    "canonicalization": "RFC8785",
    "checksum": "deadbeefdecafbad000000000000000000000000000000000000000000000000"
}

# Write test vector targets
with open("cvcp/specs/test-vectors/event-valid-001.json", "w") as f:
    json.dump(valid_vector, f)

with open("cvcp/specs/test-vectors/event-invalid-missing-id.json", "w") as f:
    json.dump(invalid_missing_id, f)

with open("cvcp/specs/test-vectors/event-invalid-checksum.json", "w") as f:
    json.dump(invalid_checksum, f)

print("✔ Milestone 1 directory layout and test vectors written successfully.")
