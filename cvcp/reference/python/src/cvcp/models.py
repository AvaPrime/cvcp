"""
CVCP Core Event Models and RFC 8785 Canonicalizer
"""
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any

def canonicalize_rfc8785(data: Any) -> str:
    """
    Recursively serializes python structures according to RFC 8785 (JCS).
    Enforces lexicographical sorting of map keys and zero whitespace spacing.
    """
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
        """
        Serializes the object, sorting keys and removing whitespace.
        The integrity block must not be passed to this function.
        """
        raw_dict = asdict(self)
        return canonicalize_rfc8785(raw_dict).encode("utf-8")
