import pytest
from cvcp.connectors.ingress import IngressConnector
from cvcp.connectors.registry import ConnectorRegistry, ConnectorDescriptor
from cvcp.connectors.handshake import ConnectorHandshake
from cvcp.connectors.errors import CVCPProtocolError
from cvcp.capabilities import RuntimeCapabilities

def test_successful_negotiation():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader"], [])
    remote_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001", "SHA256"], ["Reader"], ["github-v1"])
    
    connector = IngressConnector(local_caps)
    result = connector.negotiate(remote_caps)
    
    assert result.compatible is True
    assert result.negotiated_version == "1.1.0"
    assert result.negotiated_features == ("RFC0001", "SHA256")
    assert result.negotiated_profiles == ("Reader",)
    assert result.negotiated_extensions == ()

def test_version_downgrade():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote_caps = RuntimeCapabilities.create("1.2.0", ["RFC0001"], ["Reader"], [])
    
    connector = IngressConnector(local_caps)
    result = connector.negotiate(remote_caps)
    
    assert result.compatible is True
    assert result.downgraded is True
    assert result.negotiated_version == "1.1.0"

def test_incompatible_protocol_versions():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote_caps = RuntimeCapabilities.create("2.0.0", ["RFC0001"], ["Reader"], [])
    
    connector = IngressConnector(local_caps)
    result = connector.negotiate(remote_caps)
    
    assert result.compatible is False

def test_malformed_handshake_headers():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    connector = IngressConnector(local_caps)
    
    with pytest.raises(CVCPProtocolError) as exc:
        connector.negotiate_from_headers([("CVCP-Version", "invalid.version")])
    assert exc.value.error_code == "CVCP_ERR_PROTOCOL_VERSION"

def test_duplicate_headers():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    connector = IngressConnector(local_caps)
    
    with pytest.raises(CVCPProtocolError) as exc:
        connector.negotiate_from_headers([
            ("CVCP-Version", "1.1.0"),
            ("CVCP-Version", "1.1.0")
        ])
    assert exc.value.error_code == "CVCP_ERR_NEGOTIATION"

def test_malformed_capability_identifiers():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    connector = IngressConnector(local_caps)
    
    with pytest.raises(CVCPProtocolError) as exc:
        connector.negotiate_from_headers([
            ("CVCP-Version", "1.1.0"),
            ("CVCP-Features", "bad id!")
        ])
    assert exc.value.error_code == "CVCP_ERR_EVENT_SCHEMA"

def test_unsupported_mandatory_features():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote_caps = RuntimeCapabilities.create("1.1.0", ["SHA256"], ["Reader"], [])
    
    connector = IngressConnector(local_caps)
    result = connector.negotiate(remote_caps)
    
    assert result.compatible is False
    with pytest.raises(CVCPProtocolError) as exc:
        result.raise_for_status()
    assert exc.value.error_code == "CVCP_ERR_NEGOTIATION"

def test_unsupported_profiles():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Writer"], [])
    
    connector = IngressConnector(local_caps)
    result = connector.negotiate(remote_caps)
    
    assert result.compatible is False
    with pytest.raises(CVCPProtocolError) as exc:
        result.raise_for_status()
    assert exc.value.error_code == "CVCP_ERR_PROFILE_UNSUPPORTED"

def test_optional_extensions():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], ["ext1"])
    remote_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], ["ext2"])
    
    connector = IngressConnector(local_caps)
    result = connector.negotiate(remote_caps)
    
    assert result.compatible is True
    assert result.negotiated_extensions == ()

def test_deterministic_serialization():
    caps = RuntimeCapabilities.create("1.1.0", ["RFC0001", "B", "A"], ["Reader"], ["ext1"])
    headers = ConnectorHandshake.serialize_headers(caps)
    
    assert headers == [
        ("CVCP-Version", "1.1.0"),
        ("CVCP-Features", "A,B,RFC0001"),
        ("CVCP-Profiles", "Reader"),
        ("CVCP-Extensions", "ext1")
    ]

def test_connector_registration():
    ConnectorRegistry.clear()
    
    decl = ConnectorDescriptor(
        name="http-connector",
        implementation_id="codessa-http-v1",
        transport="http",
        supported_versions=("1.1.0", "1.2.0"),
        supported_profiles=("Reader",),
        supported_features=("RFC0001",),
        supported_extensions=()
    )
    
    ConnectorRegistry.register(decl)
    assert ConnectorRegistry.exists("http-connector") is True
    fetched = ConnectorRegistry.get("http-connector")
    
    assert fetched is not None
    assert fetched.name == "http-connector"
    
    caps = fetched.to_capabilities("1.1.0")
    assert caps.version == "1.1.0"
    
    with pytest.raises(CVCPProtocolError):
        fetched.to_capabilities("2.0.0")
        
    connectors = ConnectorRegistry.list()
    assert len(connectors) == 1
    assert connectors[0].name == "http-connector"
    
    ConnectorRegistry.unregister("http-connector")
    assert ConnectorRegistry.exists("http-connector") is False

def test_connector_validation():
    ConnectorRegistry.clear()
    
    # Empty name
    with pytest.raises(ValueError):
        ConnectorRegistry.register(ConnectorDescriptor(
            name="", implementation_id="id1", transport="http",
            supported_versions=("1.1.0",), supported_profiles=(), supported_features=(), supported_extensions=()
        ))
        
    # Duplicate name
    decl1 = ConnectorDescriptor(
        name="test-connector", implementation_id="id1", transport="http",
        supported_versions=("1.1.0",), supported_profiles=(), supported_features=(), supported_extensions=()
    )
    ConnectorRegistry.register(decl1)
    
    with pytest.raises(ValueError, match="already registered"):
        ConnectorRegistry.register(ConnectorDescriptor(
            name="test-connector", implementation_id="id2", transport="http",
            supported_versions=("1.1.0",), supported_profiles=(), supported_features=(), supported_extensions=()
        ))
        
    # Duplicate implementation ID
    with pytest.raises(ValueError, match="Implementation ID"):
        ConnectorRegistry.register(ConnectorDescriptor(
            name="other-connector", implementation_id="id1", transport="http",
            supported_versions=("1.1.0",), supported_profiles=(), supported_features=(), supported_extensions=()
        ))

def test_repeated_negotiations():
    local_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    remote_caps = RuntimeCapabilities.create("1.1.0", ["RFC0001"], ["Reader"], [])
    
    connector = IngressConnector(local_caps)
    result1 = connector.negotiate(remote_caps)
    result2 = connector.negotiate(remote_caps)
    
    assert result1 == result2
