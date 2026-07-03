"""
CVCP Negotiation Engine

Implements the RFC-0014 Capability Discovery & Feature Negotiation Engine.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
from .capabilities import RuntimeCapabilities
from .errors import CVCPProtocolError

class CompatibilityStatus(Enum):
    COMPATIBLE = "COMPATIBLE"
    DOWNGRADED = "DOWNGRADED"
    INCOMPATIBLE = "INCOMPATIBLE"

class NegotiationReason(Enum):
    NEGOTIATION_SUCCESS = "NEGOTIATION_SUCCESS"
    VERSION_DOWNGRADED = "VERSION_DOWNGRADED"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    MISSING_CORE_PROTOCOL = "MISSING_CORE_PROTOCOL"
    FEATURE_REQUIRED = "FEATURE_REQUIRED"
    PROFILE_MISMATCH = "PROFILE_MISMATCH"
    EXTENSION_REQUIRED = "EXTENSION_REQUIRED"
    NEGOTIATION_FAILED = "NEGOTIATION_FAILED"

CORE_REQUIRED_FEATURES = ("RFC0001",)

@dataclass(frozen=True, slots=True)
class NegotiationAudit:
    local_version: str
    remote_version: str
    negotiated_version: Optional[str]
    accepted_features: Tuple[str, ...]
    rejected_features: Tuple[str, ...]
    accepted_profiles: Tuple[str, ...]
    rejected_profiles: Tuple[str, ...]
    compatibility_status: str
    reason_code: str

@dataclass(frozen=True, slots=True)
class NegotiationResult:
    negotiated_version: Optional[str]
    negotiated_features: Tuple[str, ...]
    negotiated_profiles: Tuple[str, ...]
    negotiated_extensions: Tuple[str, ...]
    compatibility_status: CompatibilityStatus
    reason_code: NegotiationReason
    audit: Optional[NegotiationAudit] = None

    @property
    def compatible(self) -> bool:
        return self.compatibility_status in (CompatibilityStatus.COMPATIBLE, CompatibilityStatus.DOWNGRADED)

    @property
    def downgraded(self) -> bool:
        return self.compatibility_status == CompatibilityStatus.DOWNGRADED

    def raise_for_status(self) -> None:
        """
        Maps negotiation failures to standard CVCP protocol errors.
        """
        if not self.compatible:
            mapping = {
                NegotiationReason.VERSION_MISMATCH: "CVCP_ERR_PROTOCOL_VERSION",
                NegotiationReason.MISSING_CORE_PROTOCOL: "CVCP_ERR_NEGOTIATION",
                NegotiationReason.PROFILE_MISMATCH: "CVCP_ERR_PROFILE_UNSUPPORTED",
                NegotiationReason.FEATURE_REQUIRED: "CVCP_ERR_FEATURE_UNSUPPORTED",
                NegotiationReason.EXTENSION_REQUIRED: "CVCP_ERR_EXTENSION_UNSUPPORTED",
                NegotiationReason.NEGOTIATION_FAILED: "CVCP_ERR_NEGOTIATION",
            }
            code = mapping.get(self.reason_code, "CVCP_ERR_NEGOTIATION")
            raise CVCPProtocolError(code, f"Negotiation failed: {self.reason_code.value}")

def _parse_version(v: str) -> tuple:
    try:
        return tuple(map(int, v.split(".")))
    except ValueError:
        return (0, 0, 0)

def negotiate(
    local: RuntimeCapabilities,
    remote: RuntimeCapabilities,
) -> NegotiationResult:
    """
    Deterministically computes the highest mutually compatible runtime configuration.
    """
    loc_v = _parse_version(local.version)
    rem_v = _parse_version(remote.version)

    # Step 1: Validate both runtime capability objects.
    # Dataclass takes care of types, but we check version.
    if loc_v == (0, 0, 0) or rem_v == (0, 0, 0):
        return NegotiationResult(
            negotiated_version=None,
            negotiated_features=(),
            negotiated_profiles=(),
            negotiated_extensions=(),
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            reason_code=NegotiationReason.VERSION_MISMATCH,
            audit=NegotiationAudit(
                local_version=local.version,
                remote_version=remote.version,
                negotiated_version=None,
                accepted_features=(),
                rejected_features=(),
                accepted_profiles=(),
                rejected_profiles=(),
                compatibility_status=CompatibilityStatus.INCOMPATIBLE.value,
                reason_code=NegotiationReason.VERSION_MISMATCH.value
            )
        )

    # Step 2: Determine highest mutually supported protocol version.
    if loc_v[0] != rem_v[0] or loc_v[0] == 0:
        return NegotiationResult(
            negotiated_version=None,
            negotiated_features=(),
            negotiated_profiles=(),
            negotiated_extensions=(),
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            reason_code=NegotiationReason.VERSION_MISMATCH,
            audit=NegotiationAudit(
                local_version=local.version,
                remote_version=remote.version,
                negotiated_version=None,
                accepted_features=(),
                rejected_features=(),
                accepted_profiles=(),
                rejected_profiles=(),
                compatibility_status=CompatibilityStatus.INCOMPATIBLE.value,
                reason_code=NegotiationReason.VERSION_MISMATCH.value
            )
        )

    neg_v = min(loc_v, rem_v)
    neg_version = f"{neg_v[0]}.{neg_v[1]}.{neg_v[2]}"

    # Step 3: Compute deterministic intersections
    shared_features = tuple(sorted(set(local.features).intersection(remote.features)))
    rejected_features = tuple(sorted(set(local.features).union(remote.features).difference(shared_features)))
    shared_profiles = tuple(sorted(set(local.profiles).intersection(remote.profiles)))
    rejected_profiles = tuple(sorted(set(local.profiles).union(remote.profiles).difference(shared_profiles)))
    shared_extensions = tuple(sorted(set(local.extensions).intersection(remote.extensions)))

    def _make_audit(status_str: str, reason_str: str, neg_ver: Optional[str]) -> NegotiationAudit:
        return NegotiationAudit(
            local_version=local.version,
            remote_version=remote.version,
            negotiated_version=neg_ver,
            accepted_features=shared_features,
            rejected_features=rejected_features,
            accepted_profiles=shared_profiles,
            rejected_profiles=rejected_profiles,
            compatibility_status=status_str,
            reason_code=reason_str
        )

    # Step 4: Verify required protocol support
    for core_feature in CORE_REQUIRED_FEATURES:
        if core_feature not in shared_features:
            return NegotiationResult(
                negotiated_version=neg_version,
                negotiated_features=shared_features,
                negotiated_profiles=shared_profiles,
                negotiated_extensions=shared_extensions,
                compatibility_status=CompatibilityStatus.INCOMPATIBLE,
                reason_code=NegotiationReason.MISSING_CORE_PROTOCOL,
                audit=_make_audit(CompatibilityStatus.INCOMPATIBLE.value, NegotiationReason.MISSING_CORE_PROTOCOL.value, neg_version)
            )

    # Step 5: Mandatory protocol features
    # Profile mismatch
    if (local.profiles or remote.profiles) and not shared_profiles:
        return NegotiationResult(
            negotiated_version=neg_version,
            negotiated_features=shared_features,
            negotiated_profiles=shared_profiles,
            negotiated_extensions=shared_extensions,
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            reason_code=NegotiationReason.PROFILE_MISMATCH,
            audit=_make_audit(CompatibilityStatus.INCOMPATIBLE.value, NegotiationReason.PROFILE_MISMATCH.value, neg_version)
        )

    # Step 6: Determine compatibility
    status = CompatibilityStatus.COMPATIBLE
    reason = NegotiationReason.NEGOTIATION_SUCCESS

    if loc_v != rem_v or len(shared_features) < len(local.features) or len(shared_profiles) < len(local.profiles):
        status = CompatibilityStatus.DOWNGRADED
        if loc_v != rem_v:
            reason = NegotiationReason.VERSION_DOWNGRADED

    return NegotiationResult(
        negotiated_version=neg_version,
        negotiated_features=shared_features,
        negotiated_profiles=shared_profiles,
        negotiated_extensions=shared_extensions,
        compatibility_status=status,
        reason_code=reason,
        audit=_make_audit(status.value, reason.value, neg_version)
    )
