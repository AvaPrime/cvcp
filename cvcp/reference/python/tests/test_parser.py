"""
CVCP Milestone 1 Test Harness
"""
import os
import json
import pytest

from cvcp.errors import CVCPProtocolError
from cvcp.parser import CVCPEventParser

VECTORS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../specs/test-vectors")
)

def load_vector(filename: str) -> str:
    path = os.path.join(VECTORS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_stage_valid_vector():
    """Validates execution against a mathematically correct canonical payload."""
    wire_data = load_vector("event-valid-001.json")
    envelope = CVCPEventParser.parse_and_verify(wire_data)
    assert envelope.event_id == "evt_0197b80c-f7b8-7b31-b913-99a21b4f881a"
    assert envelope.payload["new_status"] == "PROMOTED"

def test_stage_missing_id_vector():
    """Asserts that schemas missing key values trigger parsing exceptions."""
    wire_data = load_vector("event-invalid-missing-id.json")
    with pytest.raises(CVCPProtocolError) as err:
        CVCPEventParser.parse_and_verify(wire_data)
    assert err.value.error_code == "CVCP_ERR_EVENT_SCHEMA"

def test_stage_invalid_checksum_vector():
    """Asserts that modified or mismatched hashes reject execution cycles."""
    wire_data = load_vector("event-invalid-checksum.json")
    with pytest.raises(CVCPProtocolError) as err:
        CVCPEventParser.parse_and_verify(wire_data)
    assert err.value.error_code == "CVCP_ERR_EVENT_CHECKSUM"
