import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getAudit,
  getPdfUrl,
} from "../services/api";
import StatusBadge from "../components/StatusBadge";
import Loading from "../components/Loading";

function Report() {
  const { auditId } = useParams();

    console.log("Report URL auditId:", auditId);

  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAudit(auditId)
      .then(setAudit)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [auditId]);

  if (loading) {
    return <Loading text="Loading audit report..." />;
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Audit Report</h2>
          <p>{audit.filename}</p>
        </div>

        <a
          href={getPdfUrl(auditId)}
          target="_blank"
          rel="noreferrer"
          className="primary-button"
        >
          Download PDF
        </a>
      </div>

      <div className="report-summary">
        <div className="score-card">
          <span>Compliance Score</span>
          <strong>{audit.score.toFixed(2)}%</strong>
        </div>

        <div className="score-card">
          <span>Total Controls</span>
          <strong>{audit.total_controls}</strong>
        </div>

        <div className="score-card pass">
          <span>Passed</span>
          <strong>{audit.passed}</strong>
        </div>

        <div className="score-card fail">
          <span>Failed</span>
          <strong>{audit.failed}</strong>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="card-header">
          <div>
            <h3>Framework</h3>
            <p>
              {audit.framework?.name}{" "}
              {audit.framework?.version &&
                `• ${audit.framework.version}`}
            </p>
          </div>

          <span className="audit-id">
            Audit #{audit.audit_id}
          </span>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Findings</h3>

        {audit.findings.length === 0 ? (
          <p>No findings.</p>
        ) : (
          <div className="findings">
            {audit.findings.map((finding) => (
              <div
                className="finding-card"
                key={finding.control_id}
              >
                <div className="finding-header">
                  <div>
                    <strong>{finding.control_id}</strong>
                    <h4>{finding.title}</h4>
                  </div>

                  <div className="badge-group">
                    <StatusBadge status={finding.status} />

                    <span
                      className={`severity ${finding.severity?.toLowerCase()}`}
                    >
                      {finding.severity}
                    </span>
                  </div>
                </div>

                <div className="finding-grid">
                  <div>
                    <span>SBM Field</span>
                    <code>{finding.sbm_field}</code>
                  </div>

                  <div>
                    <span>Actual</span>
                    <code>
                      {String(finding.actual_value)}
                    </code>
                  </div>

                  <div>
                    <span>Expected</span>
                    <code>
                      {String(finding.expected_value)}
                    </code>
                  </div>
                </div>

                {finding.description && (
                  <p>{finding.description}</p>
                )}

                {finding.remediation && (
                  <div className="remediation">
                    <h4>Remediation</h4>

                    <p>
                      <strong>Risk:</strong>{" "}
                      {finding.remediation.risk_explanation}
                    </p>

                    <h5>Fix Commands</h5>

                    <pre>
                      {finding.remediation.fix_commands?.join(
                        "\n"
                      )}
                    </pre>

                    <h5>Verification</h5>

                    <code>
                      {finding.remediation.verification_command}
                    </code>

                    {finding.remediation.caveat && (
                      <p className="caveat">
                        <strong>Caveat:</strong>{" "}
                        {finding.remediation.caveat}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Report;