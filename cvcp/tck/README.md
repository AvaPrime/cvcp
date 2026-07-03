# CVCP Technology Compatibility Kit (TCK)

The Technology Compatibility Kit (TCK) is a protocol-level conformance framework responsible for validating that any CVCP implementation (Python, Rust, Go, TypeScript, etc.) behaves identically.

It evaluates implementations against official protocol specifications, schemas, test vectors, and capability negotiations.

## Architecture

- **vectors/**: Canonical protocol test vectors (valid, invalid, canonical, negotiation).
- **runner/**: Execution engine for discovering test vectors and running validations.
- **compliance/**: Protocol compliance evaluation logic.
- **reports/**: Deterministic compliance reports generator (JSON, Markdown, HTML).
- **schemas/**: JSON Schemas for validating TCK artifacts.
- **fixtures/**: Reusable fixtures and helper assets.
- **dashboard/**: Lightweight UI for visualizing compliance results.

The TCK is entirely implementation-agnostic and maintains byte-for-byte reproducibility.
