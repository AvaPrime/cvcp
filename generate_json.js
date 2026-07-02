import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const dirs = [
    "cvcp/specs/schemas",
    "cvcp/specs/test-vectors",
    "cvcp/sdk/python/src/cvcp",
    "cvcp/sdk/python/tests"
];
dirs.forEach(d => fs.mkdirSync(d, { recursive: true }));

function canonicalize(data) {
    if (Array.isArray(data)) {
        return "[" + data.map(canonicalize).join(",") + "]";
    } else if (data !== null && typeof data === 'object') {
        const keys = Object.keys(data).sort();
        const items = keys.map(k => `${JSON.stringify(k)}:${canonicalize(data[k])}`);
        return "{" + items.join(",") + "}";
    } else if (typeof data === 'boolean') {
        return data ? "true" : "false";
    } else if (data === null) {
        return "null";
    } else if (typeof data === 'number') {
        return data.toString();
    } else if (typeof data === 'string') {
        return JSON.stringify(data);
    }
}

const raw_payload_base = {
    "protocol": {"spec": "CVCP", "version": "1.1.0"},
    "event_id": "evt_0197b80c-f7b8-7b31-b913-99a21b4f881a",
    "aggregate_id": "opp_0197b80d-01f2-7a22-bc11-88f21b4a992b",
    "aggregate_type": "OPPORTUNITY",
    "event_version": 1,
    "graph_version": 142,
    "timestamp": "2026-07-02T14:32:00.000Z",
    "causation_id": "evt_0197b80a-e211-7f12-aa34-11b22c3d4e5f",
    "correlation_id": "corr_0197b80a-e211-7f12-aa34-00a11b22c3d4",
    "payload_type": "OpportunityStatusChanged",
    "payload_schema": "cvcp://schemas/opportunity-status-changed/1.0.0",
    "payload": {"new_status": "PROMOTED"},
    "metadata": {"origin_node": "connector_github_main"}
};

const jcs_str = canonicalize(raw_payload_base);
const valid_checksum = crypto.createHash('sha256').update(jcs_str, 'utf8').digest('hex');

const valid_vector = { ...raw_payload_base, integrity: { algorithm: "SHA-256", canonicalization: "RFC8785", checksum: valid_checksum } };
const invalid_missing_id = { ...raw_payload_base, integrity: { algorithm: "SHA-256", canonicalization: "RFC8785", checksum: "0000000000000000000000000000000000000000000000000000000000000000" } };
delete invalid_missing_id.event_id;
const invalid_checksum = { ...raw_payload_base, integrity: { algorithm: "SHA-256", canonicalization: "RFC8785", checksum: "deadbeefdecafbad000000000000000000000000000000000000000000000000" } };

fs.writeFileSync("cvcp/specs/test-vectors/event-valid-001.json", JSON.stringify(valid_vector, null, 2));
fs.writeFileSync("cvcp/specs/test-vectors/event-invalid-missing-id.json", JSON.stringify(invalid_missing_id, null, 2));
fs.writeFileSync("cvcp/specs/test-vectors/event-invalid-checksum.json", JSON.stringify(invalid_checksum, null, 2));

fs.writeFileSync("cvcp/sdk/python/src/cvcp/__init__.py", '__version__ = "1.1.0"\\n');
fs.writeFileSync("cvcp/sdk/python/tests/__init__.py", "");

console.log("JSON generated");
