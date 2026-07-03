import pytest
import json
import os
from pathlib import Path
from cvcp.tck.harness.runner import TCKRunner, TestVector, ComplianceReport, TestResult
from cvcp.tck.harness.errors import CVCPProtocolError

@pytest.fixture
def temp_vector_dir(tmp_path):
    vec_dir = tmp_path / "vectors"
    vec_dir.mkdir()
    
    valid_dir = vec_dir / "valid"
    valid_dir.mkdir()
    
    invalid_dir = vec_dir / "invalid"
    invalid_dir.mkdir()

    valid_json = {
        "id": "v1",
        "name": "Valid Test",
        "category": "core",
        "protocol_version": "1.1.0",
        "input": {"x": 1},
        "expected_output": {"x": 1}
    }
    
    invalid_json = {
        "id": "v2",
        "name": "Invalid Test",
        "input": {"x": -1},
        "expected_error": "CVCP_ERR_TEST"
    }

    with open(valid_dir / "1.json", "w") as f:
        json.dump(valid_json, f)
        
    with open(invalid_dir / "2.json", "w") as f:
        json.dump(invalid_json, f)
        
    return vec_dir

class DummyImplementation:
    def execute(self, vector: TestVector):
        if vector.input.get("x") == 1:
            return vector.input
        else:
            raise CVCPProtocolError("CVCP_ERR_TEST", "Test error")

class BadImplementation:
    def __call__(self, vector: TestVector):
        raise ValueError("Generic error")

def test_load_vectors(temp_vector_dir):
    runner = TCKRunner()
    vectors = runner.load_vectors(str(temp_vector_dir))
    
    assert len(vectors) == 2
    # Lexical order ensures 1.json comes before 2.json
    assert vectors[0].id == "v2"
    assert vectors[1].id == "v1"

def test_load_vectors_missing():
    runner = TCKRunner()
    with pytest.raises(CVCPProtocolError) as exc:
        runner.load_vectors("non_existent_dir")
    assert exc.value.error_code == "CVCP_ERR_TCK_VECTOR"

def test_load_vectors_malformed(tmp_path):
    vec_dir = tmp_path / "bad_vectors"
    vec_dir.mkdir()
    with open(vec_dir / "bad.json", "w") as f:
        f.write("{bad json")
    
    runner = TCKRunner()
    with pytest.raises(CVCPProtocolError) as exc:
        runner.load_vectors(str(vec_dir))
    assert exc.value.error_code == "CVCP_ERR_TCK_SCHEMA"

def test_run_vector_pass():
    runner = TCKRunner()
    vector = TestVector("v1", "v1", "cat", "1.1.0", "", {"x": 1}, {"x": 1}, None, {})
    result = runner.run_vector(DummyImplementation(), vector)
    
    assert result.status == "PASS"
    assert result.error_code is None
    assert result.actual == {"x": 1}

def test_run_vector_expected_error_pass():
    runner = TCKRunner()
    vector = TestVector("v2", "v2", "cat", "1.1.0", "", {"x": -1}, None, "CVCP_ERR_TEST", {})
    result = runner.run_vector(DummyImplementation(), vector)
    
    assert result.status == "PASS"
    assert result.error_code == "CVCP_ERR_TEST"

def test_run_vector_fail_unexpected_error():
    runner = TCKRunner()
    vector = TestVector("v1", "v1", "cat", "1.1.0", "", {"x": -1}, {"x": 1}, None, {})
    result = runner.run_vector(DummyImplementation(), vector)
    
    assert result.status == "ERROR"
    assert result.error_code == "CVCP_ERR_TEST"

def test_run_vector_generic_error():
    runner = TCKRunner()
    vector = TestVector("v1", "v1", "cat", "1.1.0", "", {"x": 1}, {"x": 1}, None, {})
    result = runner.run_vector(BadImplementation(), vector)
    
    assert result.status == "ERROR"
    assert result.error_code == "CVCP_ERR_TCK_EXECUTION"

def test_run_all_and_report():
    runner = TCKRunner()
    v1 = TestVector("v1", "v1", "cat", "1.1.0", "", {"x": 1}, {"x": 1}, None, {})
    v2 = TestVector("v2", "v2", "cat", "1.1.0", "", {"x": -1}, None, "CVCP_ERR_TEST", {})
    
    report = runner.run(DummyImplementation(), [v1, v2], impl_name="test-impl", timestamp="2026-07-02T00:00:00Z")
    
    assert report.total_vectors == 2
    assert report.passed == 2
    assert report.failed == 0
    assert report.skipped == 0
    assert report.compliance_percentage == 100.0
    assert report.status == "PASS"
    assert report.execution_timestamp == "2026-07-02T00:00:00Z"

def test_write_report(tmp_path):
    runner = TCKRunner()
    report = ComplianceReport(
        protocol="CVCP",
        implementation="test",
        implementation_version="1.0",
        execution_timestamp="2026-07-02T00:00:00Z",
        total_vectors=0,
        passed=0,
        failed=0,
        skipped=0,
        compliance_percentage=100.0,
        status="PASS",
        results=[]
    )
    out_file = tmp_path / "report.json"
    runner.write_report(report, str(out_file))
    
    with open(out_file, "r") as f:
        data = json.load(f)
        
    assert data["protocol"] == "CVCP"
    assert data["status"] == "PASS"

def test_deterministic_serialization(tmp_path):
    runner = TCKRunner()
    report = ComplianceReport(
        protocol="CVCP",
        implementation="test",
        implementation_version="1.0",
        execution_timestamp="2026-07-02T00:00:00Z",
        total_vectors=0,
        passed=0,
        failed=0,
        skipped=0,
        compliance_percentage=100.0,
        status="PASS",
        results=[]
    )
    out_file = tmp_path / "report.json"
    runner.write_report(report, str(out_file))
    
    with open(out_file, "r") as f:
        content = f.read()
    
    assert " " not in content # separators=(',', ':')
    assert '"protocol":"CVCP"' in content

def test_empty_vector_dir(tmp_path):
    vec_dir = tmp_path / "empty"
    vec_dir.mkdir()
    
    runner = TCKRunner()
    vectors = runner.load_vectors(str(vec_dir))
    assert len(vectors) == 0
    
    report = runner.run(DummyImplementation(), vectors)
    assert report.total_vectors == 0
    assert report.compliance_percentage == 100.0

