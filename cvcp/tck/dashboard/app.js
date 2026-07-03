document.addEventListener("DOMContentLoaded", () => {
  // Placeholder mock data until we fetch real reports
  const mockReport = {
    sdk: "CVCP Python SDK",
    protocol_version: "1.1.0",
    timestamp: new Date().toISOString(),
    summary: {
      total: 4,
      passed: 3,
      failed: 1,
      skipped: 0
    },
    results: [
      { id: "test-valid-1", compliant: true },
      { id: "test-canonical-1", compliant: true },
      { id: "test-negotiation-1", compliant: true },
      { id: "test-invalid-1", compliant: false, error: "Missing CVCP_ERR_PROTOCOL_VERSION" }
    ]
  };

  function renderReport(report) {
    document.getElementById("sdk-name").textContent = report.sdk;
    document.getElementById("protocol-version").textContent = report.protocol_version;
    
    const { total, passed, failed, skipped } = report.summary;
    const score = total > 0 ? Math.round((passed / total) * 100) : 0;
    
    const scoreEl = document.getElementById("compliance-score");
    scoreEl.textContent = `${score}%`;
    if (score < 100) {
      scoreEl.style.color = "var(--failed-color)";
    }

    document.getElementById("stat-passed").textContent = passed;
    document.getElementById("stat-failed").textContent = failed;
    document.getElementById("stat-skipped").textContent = skipped;
    document.getElementById("stat-total").textContent = total;

    const failedList = document.getElementById("failed-list");
    failedList.innerHTML = "";
    
    const failedTests = report.results.filter(r => !r.compliant);
    if (failedTests.length === 0) {
      failedList.innerHTML = "<li><p>No failed tests.</p></li>";
    } else {
      failedTests.forEach(test => {
        const li = document.createElement("li");
        li.className = "failed-item";
        li.innerHTML = `<strong>${test.id}</strong><br>Reason: ${test.error || 'Unknown error'}`;
        failedList.appendChild(li);
      });
    }
  }

  // Init
  renderReport(mockReport);
});
