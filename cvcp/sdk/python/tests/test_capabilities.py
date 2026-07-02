"""
Test Suite for RuntimeCapabilities
"""
import pytest
from cvcp.capabilities import RuntimeCapabilities
from cvcp.errors import CVCPProtocolError

def test_normalization():
    caps1 = RuntimeCapabilities(
        version="1.1.0",
        features=("RFC0013", "RFC0001", " RFC0013 ")
    )
    assert caps1.features == ("RFC0001", "RFC0013")
    
    caps2 = RuntimeCapabilities(
        version="1.1.0",
        features=("RFC0001", "RFC0013")
    )
    assert caps1 == caps2

def test_malformed_version():
    with pytest.raises(CVCPProtocolError) as exc:
        RuntimeCapabilities(version="1.1", features=(), profiles=(), extensions=())
    assert exc.value.error_code == "CVCP_ERR_PROTOCOL_VERSION"

def test_reject_empty_string():
    with pytest.raises(CVCPProtocolError) as exc:
        RuntimeCapabilities(version="1.1.0", features=("",), profiles=(), extensions=())
    assert exc.value.error_code == "CVCP_ERR_EVENT_SCHEMA"

def test_malformed_identifiers():
    with pytest.raises(CVCPProtocolError) as exc:
        RuntimeCapabilities(version="1.1.0", features=("INVALID FEATURE",), profiles=(), extensions=())
    assert exc.value.error_code == "CVCP_ERR_EVENT_SCHEMA"
    
    with pytest.raises(CVCPProtocolError) as exc:
        RuntimeCapabilities(version="1.1.0", features=(), profiles=("profile!",), extensions=())
    assert exc.value.error_code == "CVCP_ERR_EVENT_SCHEMA"
    
    with pytest.raises(CVCPProtocolError) as exc:
        RuntimeCapabilities(version="1.1.0", features=(), profiles=(), extensions=("ext.1",))
    assert exc.value.error_code == "CVCP_ERR_EVENT_SCHEMA"

def test_reject_none():
    with pytest.raises(CVCPProtocolError) as exc:
        RuntimeCapabilities(version="1.1.0", features=(None,), profiles=(), extensions=())
    assert exc.value.error_code == "CVCP_ERR_EVENT_SCHEMA"

def test_serialization():
    caps = RuntimeCapabilities.create(
        "1.1.0", 
        ["RFC0001", "RFC0013"], 
        ["Reader"], 
        ["ext1"]
    )
    d = caps.to_dict()
    assert d == {
        "version": "1.1.0",
        "features": ["RFC0001", "RFC0013"],
        "profiles": ["Reader"],
        "extensions": ["ext1"]
    }
    
    j = caps.to_json()
    caps2 = RuntimeCapabilities.from_json(j)
    assert caps == caps2

def test_helpers():
    caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], ["ext1"])
    assert caps.supports_feature(" RFC0001 ")
    assert not caps.supports_feature("RFC0013")
    assert caps.supports_profile("Reader")
    assert caps.supports_extension("ext1")
