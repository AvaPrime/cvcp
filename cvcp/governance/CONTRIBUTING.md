# Contributing to CVCP

The Cross-Vendor Communication Protocol (CVCP) is an open, standards-grade protocol. This repository serves as the official registry, specification, and Technology Compatibility Kit (TCK) for CVCP.

We welcome contributions to the protocol standard, as well as submissions of new reference implementations!

## 1. Governance & RFCs

Changes to the CVCP protocol are managed via Request for Comments (RFC). We operate under an **Artifact-First** governance model. Every specification change MUST produce machine-readable artifacts (JSON Schemas, canonical vectors, and TCK compliance tests).

### How to Propose a Protocol Change

1. **Draft an RFC**: Create a new Markdown file in the `specs/normative/` directory for protocol-defining specifications or `specs/informative/` for explanatory content. Number it sequentially (e.g., `RFC-0015-FeatureName.md`).
2. **Detail the Specification**: Clearly outline the motivation, technical details, schema changes, and backward-compatibility implications.
3. **Artifact-First Execution**: You MUST update or create the corresponding JSON Schemas, canonical test vectors, and TCK references. A PR cannot merge without these artifacts.
4. **Submit a PR**: Open a Pull Request targeting the `main` branch. 
5. **Working Group Review**: The `CVCP-WG` will review the proposal. Merged normative RFCs become part of the official standard.

## 2. Technology Compatibility Kit (TCK)

The TCK located in the `tck/` directory is the "Judge". It defines what it means to be "CVCP Compliant".
If you are modifying the protocol (via an RFC), you **must** also submit matching test vectors and schema updates to the TCK.

### Contributing to the TCK

- **Vectors**: Add valid, invalid, and canonical edge-case examples in `tck/vectors/`.
- **Schemas**: Update JSON schemas in `tck/schemas/` to reflect any new payload definitions.
- **Runner**: Improvements to the reference runner or compliance evaluation engine.

## 3. Submitting an Implementation for Certification

Any vendor or developer can implement CVCP. To have your implementation officially certified:

1. **Pass the TCK**: Ensure your implementation passes the entire CVCP Technology Compatibility Kit. It must produce byte-for-byte deterministic canonical output where required and correctly negotiate capabilities.
2. **Provide a Runner**: Implement a wrapper script or GitHub Actions workflow that executes the TCK against your library.
3. **Submit for Certification**: Open a Pull Request adding your implementation details to `cvcp.yaml` and providing the workflow under `.github/workflows/`.
4. **Automated Verification**: Our `.github/workflows/certify.yml` will automatically verify your implementation. If it passes, a cryptographically signed `CVCP-CERTIFIED.json` will be generated and published to the registry.

## 4. Reference Implementations

The `reference/` directory contains standard implementations (e.g., Python, TypeScript). These serve as educational references. Pull requests fixing bugs or improving these SDKs are always welcome.

*Thank you for helping us build a robust, vendor-neutral standard for cross-agent communication!*
