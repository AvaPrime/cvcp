# Cross-Vendor Communication Protocol (CVCP)

![CVCP Version](https://img.shields.io/badge/CVCP-v1.1.0-blue.svg)
![Status](https://img.shields.io/badge/Status-Standard-success.svg)

CVCP is an open, vendor-neutral governance protocol standard for AI systems. It is designed to enable deterministic, secure, and cross-platform communication, execution contracts, provenance, policy enforcement, and capability negotiation between AI agents, autonomous systems, and their host environments.

This repository serves as the **Official Standards Registry**, containing the normative protocol specifications, schemas, the Technology Compatibility Kit (TCK), official registries, and reference implementations.

## Repository Architecture

This repository is structured to scale as an internet-grade protocol standard:

```
cvcp/
├── cvcp.yaml                 # The Protocol Manifest (identity, version, governance, support)
├── specs/                    # Protocol specifications ("The Law")
│   ├── normative/            # Normative RFCs that define compliance (e.g., RFC-0001, RFC-0014)
│   ├── informative/          # Explanatory architecture, rationale, and examples
│   └── schemas/              # JSON Schemas defining canonical protocol payloads
├── registry/                 # Canonical source of truth
│   ├── capabilities/         # Registered capabilities
│   ├── certifications/       # Official signed certifications
│   ├── extensions/           # Registered protocol extensions
│   ├── implementations/      # Registered SDK implementations
│   └── media-types/          # Registered media types
├── tck/                      # Technology Compatibility Kit ("The Judge")
│   ├── compliance/           # Compliance evaluation logic
│   ├── reports/              # Deterministic certification report generators
│   └── vectors/              # Canonical test vectors (valid, invalid, edge-cases)
├── reference/                # Official reference implementations (Non-normative)
│   ├── python/               # CVCP Python SDK (Codessa Reference)
│   └── typescript/           # (Planned) TypeScript SDK
└── governance/               # Contribution, ADRs, and process documentation
```

## The CVCP Manifest

The root `cvcp.yaml` file defines the current protocol version, working group status, and officially recognized implementations. It acts as the machine-readable identity of this standard.

## Certification & The TCK

The **Technology Compatibility Kit (TCK)** ensures that any CVCP implementation behaves identically, regardless of the language or vendor. It evaluates runtime implementations against official protocol test vectors, verifying:
- Byte-for-byte deterministic serialization
- Capability negotiation compliance (RFC-0014)
- Schema adherence
- Canonical data handling

To claim your implementation is "CVCP Compliant", it must pass the TCK and generate a `CVCP-CERTIFIED.json` artifact via the automated certification workflow.

## Contributing & Governance

CVCP is an open protocol. We welcome proposals for new protocol features via the RFC process, additions to the TCK, and new SDK reference implementations.

Please review the [Contribution Guidelines](governance/CONTRIBUTING.md) to understand how to propose changes, update the TCK, and submit an implementation for certification.

## Getting Started

If you are looking to build applications *using* CVCP, refer to the language-specific SDKs in the `reference/` directory:

- [Python SDK Reference](reference/python/)

---

*CVCP: A shared language for governed software.*
