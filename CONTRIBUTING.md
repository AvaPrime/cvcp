# Contributing to CVCP

Thank you for your interest in contributing to the Cross-Vendor Communication Protocol!

## Overview

CVCP is an open protocol standard maintained by the CVCP Working Group. This document outlines how to propose changes, contribute code, and maintain compliance.

## Architecture

```
cvcp/
├── specs/                    # Protocol specifications (RFC documents)
├── registry/                 # Canonical source of truth for implementations
├── tck/                      # Technology Compatibility Kit (test framework)
└── reference/                # Reference SDK implementations
```

## How to Contribute

### 1. Propose Protocol Changes (RFC Process)

Protocol-level changes require an RFC (Request for Comments):

1. **Draft your RFC**
   - Create a file: `cvcp/specs/rfc/RFC-XXXX-short-name.md`
   - Use the RFC template below
   - Include motivation, specification, and test vectors

2. **Open a Pull Request**
   - Tag with labels: `rfc`, `type:proposal`
   - Link related issues
   - Provide implementation examples

3. **Community Discussion**
   - Minimum 5 business days for feedback
   - Address concerns in the PR
   - Update RFC based on feedback

4. **Approval**
   - Approved by 2+ CVCP-WG maintainers
   - No unresolved blocking concerns
   - Test vectors pass TCK

5. **Merge**
   - RFC moves to `specs/normative/` or `specs/informative/`
   - Increment protocol version if normative
   - Update `cvcp.yaml` manifest

### RFC Template

```markdown
# RFC-XXXX: Short Title

## Status
- **Stage**: Draft | Review | Approved | Frozen
- **Version**: CVCP 1.1.0
- **Proposed by**: @github-username

## Motivation
Why is this change needed?

## Specification
Detailed technical specification.

### Example
```json
{
  "protocol": {...}
}
```

## Compliance
- Test vectors: [link to test-vectors/]
- Backward compatible: yes/no
- Breaking changes: list any

## Implementation
Reference implementations should support this RFC.
```

### 2. Submit Test Vectors

All feature additions must include test vectors:

**Required:**
- ✅ Valid case(s) - demonstrates intended behavior
- ✅ Invalid case(s) - shows error handling
- ✅ Edge case(s) - boundary conditions

**Location:**
```
cvcp/tck/vectors/
├── valid/              # Valid payloads
├── invalid/            # Invalid payloads (should fail parsing)
└── edge-cases/         # Boundary conditions
```

**Format:**
All test vectors are JSON files with meaningful names:
```
event-valid-basic-opportunity.json
event-invalid-missing-correlation-id.json
event-edge-case-max-payload-size.json
```

**Running Tests Locally:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run TCK tests
python cvcp/tck/run_tests.py

# Or with pytest directly
pytest cvcp/tck/tests -v
```

### 3. Code Contributions

#### Python SDK (`cvcp/`)

**Style Guide:**
- Format: `black` (line length: 100)
- Imports: `isort` with black profile
- Type hints: `mypy --strict` (mandatory)
- No untyped functions

**Before Submitting:**
```bash
# Auto-format
black cvcp/
isort cvcp/

# Type checking
mypy cvcp/ --strict

# Run tests
pytest cvcp/tck/tests -v --cov=cvcp
```

**Example PR:**
```python
from typing import Dict, Any
from pydantic import BaseModel, Field

class EventPayload(BaseModel):
    """Type-safe event payload."""
    
    event_type: str = Field(..., min_length=1)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    def validate_business_rules(self) -> bool:
        """Validate domain-specific rules."""
        return True
```

#### TypeScript SDK (`src/`)

**Style Guide:**
- Lint: `eslint` + `prettier`
- Type hints: `strict` mode
- Tests: Jest

**Before Submitting:**
```bash
npm run lint
npm run build
npm run test
```

### 4. Documentation

Add docstrings to all public functions:

```python
def parse_and_verify(wire_data: str) -> EventEnvelope:
    """
    Parse and validate a CVCP event envelope.
    
    Performs comprehensive validation:
    1. JSON syntax
    2. Schema compliance
    3. Semantic constraints
    4. Cryptographic integrity
    
    Args:
        wire_data: JSON string containing CVCP event
        
    Returns:
        EventEnvelope: Validated, typed event object
        
    Raises:
        CVCPProtocolError: If any validation fails
        
    Example:
        >>> wire = json.dumps({"protocol": {...}})
        >>> envelope = parse_and_verify(wire)
        >>> print(envelope.event_id)
    """
```

## Code Review Process

PRs require:
- ✅ All GitHub Actions pass
- ✅ Test coverage >90%
- ✅ 1+ maintainer approval
- ✅ Semantic review (correctness, design)
- ✅ No merge conflicts

## Certification Checklist

To submit a CVCP implementation for certification:

- [ ] RFC approved (if adding features)
- [ ] All TCK tests pass (100%)
- [ ] Coverage >90% (for Python)
- [ ] Type hints complete (Python) / strict mode (TS)
- [ ] Documentation complete
- [ ] CHANGELOG updated

Submit via:
1. Tag PR with `type:certification`
2. Reference RFC(s)
3. Link to implementation repo
4. Attach test results

## Versioning

CVCP uses Semantic Versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking protocol changes (rare)
- **MINOR**: New features, backward-compatible
- **PATCH**: Bug fixes

Update version in:
- `cvcp/cvcp.yaml` (protocol version)
- `pyproject.toml` (SDK version)
- `CHANGELOG.md` (document changes)

## Community

- **Discussions**: [GitHub Discussions](https://github.com/AvaPrime/cvcp/discussions)
- **Issues**: [GitHub Issues](https://github.com/AvaPrime/cvcp/issues)
- **Spec URI**: https://github.com/AvaPrime/cvcp/tree/main/specs

## Code of Conduct

We are committed to providing a welcoming and inspiring community. Please read our Code of Conduct.

---

**Questions?** Open an issue or ask in Discussions. Thank you for contributing! 🎉
