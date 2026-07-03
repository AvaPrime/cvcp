import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from .errors import CVCPProtocolError

@dataclass(frozen=True, slots=True)
class TestVector:
    id: str
    name: str
    category: str
    protocol_version: str
    description: str
    input: Any
    expected_output: Any
    expected_error: Optional[str]
    metadata: Dict[str, Any]

@dataclass(frozen=True, slots=True)
class TestResult:
    vector_id: str
    status: str
    expected: Any
    actual: Any
    execution_time_ms: float
    error_code: Optional[str]
    message: Optional[str]

@dataclass(frozen=True, slots=True)
class ComplianceReport:
    protocol: str
    implementation: str
    implementation_version: str
    execution_timestamp: str
    total_vectors: int
    passed: int
    failed: int
    skipped: int
    compliance_percentage: float
    status: str
    results: List[TestResult]

class TCKRunner:
    """
    Execution harness serving as the canonical protocol conformance engine for CVCP.
    """

    def load_vectors(self, path: str) -> List[TestVector]:
        """
        Recursively discovers and loads protocol test vectors in deterministic lexical order.
        """
        base_path = Path(path)
        if not base_path.exists():
            raise CVCPProtocolError("CVCP_ERR_TCK_VECTOR", f"Directory or file not found: {path}")

        if base_path.is_file():
            files = [base_path]
        else:
            files = sorted(base_path.rglob("*.json"))

        vectors = []
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                if not isinstance(data, dict):
                    raise ValueError("Root must be an object")
                if "id" not in data or "name" not in data:
                    raise ValueError("Missing required fields 'id' or 'name'")

                vector = TestVector(
                    id=data["id"],
                    name=data["name"],
                    category=data.get("category", "unknown"),
                    protocol_version=data.get("protocol_version", "1.1.0"),
                    description=data.get("description", ""),
                    input=data.get("input"),
                    expected_output=data.get("expected_output"),
                    expected_error=data.get("expected_error"),
                    metadata=data.get("metadata", {})
                )
                vectors.append(vector)
            except Exception as e:
                raise CVCPProtocolError("CVCP_ERR_TCK_SCHEMA", f"Failed to load vector {file_path}: {e}")

        return vectors

    def run_vector(self, implementation: Any, vector: TestVector) -> TestResult:
        """
        Executes a single vector against the implementation.
        """
        start_time = time.perf_counter()
        actual = None
        error_code = None
        message = None
        status = "FAIL"

        try:
            if callable(implementation):
                result_output = implementation(vector)
            elif hasattr(implementation, "execute"):
                result_output = implementation.execute(vector)
            elif hasattr(implementation, "run"):
                result_output = implementation.run(vector)
            else:
                raise ValueError("Implementation is not callable and missing execute() or run()")

            actual = result_output
            if vector.expected_error:
                status = "FAIL"
                message = f"Expected error {vector.expected_error} but got success"
            else:
                if vector.expected_output is not None:
                    if actual == vector.expected_output:
                        status = "PASS"
                    else:
                        status = "FAIL"
                        message = "Actual output did not match expected"
                else:
                    status = "PASS"
                
        except Exception as e:
            if hasattr(e, "error_code"):
                err_code = getattr(e, "error_code")
                msg = getattr(e, "message", str(e))
            else:
                err_code = "CVCP_ERR_TCK_EXECUTION"
                msg = str(e)
                
            actual = None
            error_code = err_code
            message = msg

            if vector.expected_error == err_code:
                status = "PASS"
            elif vector.expected_error:
                status = "FAIL"
                message = f"Expected {vector.expected_error} but got {err_code}: {msg}"
            else:
                status = "ERROR"

        execution_time_ms = (time.perf_counter() - start_time) * 1000

        return TestResult(
            vector_id=vector.id,
            status=status,
            expected=vector.expected_output if vector.expected_output is not None else vector.expected_error,
            actual=actual if status != "ERROR" else None,
            execution_time_ms=execution_time_ms,
            error_code=error_code,
            message=message
        )

    def run(self, implementation: Any, vectors: List[TestVector], impl_name: str = "unknown", impl_version: str = "unknown", timestamp: Optional[str] = None) -> ComplianceReport:
        """
        Executes a list of vectors against the implementation and produces a compliance report.
        """
        try:
            results = []
            for vector in vectors:
                results.append(self.run_vector(implementation, vector))
            return self.generate_report(results, impl_name=impl_name, impl_version=impl_version, timestamp=timestamp)
        except Exception as e:
            if not isinstance(e, CVCPProtocolError):
                raise CVCPProtocolError("CVCP_ERR_TCK_EXECUTION", f"Execution failed: {e}")
            raise

    def generate_report(self, results: List[TestResult], impl_name: str = "unknown", impl_version: str = "unknown", timestamp: Optional[str] = None) -> ComplianceReport:
        """
        Calculates metrics and returns a structured ComplianceReport.
        """
        try:
            passed = sum(1 for r in results if r.status == "PASS")
            failed = sum(1 for r in results if r.status in ("FAIL", "ERROR"))
            skipped = sum(1 for r in results if r.status == "SKIPPED")
            
            total = len(results)
            executable = total - skipped
            if executable > 0:
                percentage = round((passed / executable) * 100, 2)
            else:
                percentage = 100.0 if total == 0 else 0.0

            status = "PASS" if (failed == 0 and passed == executable) else "FAIL"
            
            if timestamp is None:
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
            return ComplianceReport(
                protocol="CVCP",
                implementation=impl_name,
                implementation_version=impl_version,
                execution_timestamp=timestamp,
                total_vectors=total,
                passed=passed,
                failed=failed,
                skipped=skipped,
                compliance_percentage=percentage,
                status=status,
                results=results
            )
        except Exception as e:
            raise CVCPProtocolError("CVCP_ERR_TCK_COMPLIANCE", f"Failed to generate compliance report: {e}")

    def write_report(self, report: ComplianceReport, path: str) -> None:
        """
        Writes the deterministic JSON report to the given path.
        """
        try:
            data = asdict(report)
            json_str = json.dumps(
                data,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
        except Exception as e:
            raise CVCPProtocolError("CVCP_ERR_TCK_REPORT", f"Failed to write report to {path}: {e}")

