"""
Test Suite for RFC-0014 Negotiation Engine
"""
import pytest
from cvcp.capabilities import RuntimeCapabilities
from cvcp.handshake import HandshakeParser
from cvcp.negotiation import (
    negotiate, 
    CompatibilityStatus, 
    NegotiationReason
)
from cvcp.errors import CVCPProtocolError

def test_identical_runtimes():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader"], ["github-v1"])
    remote = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader"], ["github-v1"])
    
    res = negotiate(local, remote)
    assert res.compatible
    assert res.compatibility_status == CompatibilityStatus.COMPATIBLE
    assert res.reason_code == NegotiationReason.NEGOTIATION_SUCCESS
    assert res.negotiated_version == "1.1.0"
    assert res.negotiated_features == ("RFC0001", "SHA256")
    assert res.negotiated_profiles == ("Reader",)
    assert res.negotiated_extensions == ("github-v1",)

def test_higher_remote_version():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote = RuntimeCapabilities.create("1.2.0", ["RFC0001"], ["Reader"], [])
    
    res = negotiate(local, remote)
    assert res.compatible
    assert res.compatibility_status == CompatibilityStatus.DOWNGRADED
    assert res.reason_code == NegotiationReason.VERSION_DOWNGRADED
    assert res.negotiated_version == "1.1.0"

def test_lower_remote_version():
    local = RuntimeCapabilities.create("1.2.0", ["RFC0001"], ["Reader"], [])
    remote = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    
    res = negotiate(local, remote)
    assert res.compatible
    assert res.compatibility_status == CompatibilityStatus.DOWNGRADED
    assert res.reason_code == NegotiationReason.VERSION_DOWNGRADED
    assert res.negotiated_version == "1.1.0"

def test_major_version_mismatch():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote = RuntimeCapabilities.create("2.0.0", ["RFC0001"], ["Reader"], [])
    
    res = negotiate(local, remote)
    assert not res.compatible
    assert res.compatibility_status == CompatibilityStatus.INCOMPATIBLE
    assert res.reason_code == NegotiationReason.VERSION_MISMATCH
    assert res.negotiated_version is None

def test_missing_rfc0001():
    local = RuntimeCapabilities.create("1.1.0", ["SHA256"], ["Reader"], [])
    remote = RuntimeCapabilities.create("1.1.0", ["SHA256"], ["Reader"], [])
    
    res = negotiate(local, remote)
    assert not res.compatible
    assert res.reason_code == NegotiationReason.MISSING_CORE_PROTOCOL

def test_incompatible_profiles():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Writer"], [])
    
    res = negotiate(local, remote)
    assert not res.compatible
    assert res.reason_code == NegotiationReason.PROFILE_MISMATCH

def test_optional_extensions_ignored():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], ["ext1"])
    remote = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], ["ext2"])
    
    res = negotiate(local, remote)
    assert res.compatible
    assert res.negotiated_extensions == ()

def test_duplicate_headers():
    headers = [
        ("CVCP-Version", "1.1.0"),
        ("CVCP-Features", "RFC0001"),
        ("cvcp-features", "SHA256")
    ]
    with pytest.raises(CVCPProtocolError) as exc:
        HandshakeParser.parse_headers(headers)
    assert exc.value.error_code == "CVCP_ERR_NEGOTIATION"

def test_malformed_headers():
    headers = [
        ("CVCP-Version", "1.1")
    ]
    with pytest.raises(CVCPProtocolError) as exc:
        HandshakeParser.parse_headers(headers)
    assert exc.value.error_code == "CVCP_ERR_PROTOCOL_VERSION"

def test_empty_feature_lists():
    headers = [
        ("CVCP-Version", "1.1.0"),
        ("CVCP-Features", "  ,,  ")
    ]
    caps = HandshakeParser.parse_headers(headers)
    assert caps.features == ()

def test_deterministic_ordering():
    caps = RuntimeCapabilities.create(
        "1.1.0",
        ["Z_FEAT", "A_FEAT", "RFC0001"],
        ["Writer", "Reader"],
        ["slack-v1", "github-v1"]
    )
    assert caps.features == ("A_FEAT", "RFC0001", "Z_FEAT")
    assert caps.profiles == ("Reader", "Writer")
    assert caps.extensions == ("github-v1", "slack-v1")

def test_serialization_round_trip():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader"], ["github-v1"])
    headers = HandshakeParser.serialize_headers(local)
    parsed = HandshakeParser.parse_headers(headers)
    assert local == parsed

def test_equality_despite_reordered_inputs():
    local1 = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader", "Writer"], ["github-v1"])
    remote1 = RuntimeCapabilities.create("1.1.0", ["SHA256", "RFC0001"], ["Writer", "Reader"], ["github-v1"])
    
    local2 = RuntimeCapabilities.create("1.1.0", ["SHA256", "RFC0001"], ["Writer", "Reader"], ["github-v1"])
    remote2 = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader", "Writer"], ["github-v1"])
    
    res1 = negotiate(local1, remote1)
    res2 = negotiate(local2, remote2)
    
    assert res1 == res2
    assert res1.negotiated_features == ("RFC0001", "SHA256")
    assert res1.negotiated_profiles == ("Reader", "Writer")

def test_raise_for_status():
    local = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Writer"], [])
    
    res = negotiate(local, remote)
    assert not res.compatible
    with pytest.raises(CVCPProtocolError) as exc:
        res.raise_for_status()
    assert exc.value.error_code == "CVCP_ERR_PROFILE_UNSUPPORTED"
