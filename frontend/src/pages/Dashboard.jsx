import { useEffect, useState } from "react";
import { getHealth, getReports } from "../services/api";
import Loading from "../components/Loading";

function Dashboard() {
  const [backend, setBackend] = useState("Checking...");

  const [reports, setReports] = useState({
    total_audits: 0,
    average_score: 0,
    recent_audits: [],
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [health, reportData] = await Promise.all([
          getHealth(),
          getReports(),
        ]);

        if (health.status === "ok") {
          setBackend("Connected");
        }

        console.log("REPORT DATA:", reportData);
        setReports(reportData);
      } catch {
        setBackend("Disconnected");
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Dashboard</h2>
          <p>Overview of your network security audits.</p>
        </div>

        <a className="primary-button" href="/upload">
          + Upload Configuration
        </a>
      </div>

      {loading ? (
        <Loading text="Loading dashboard..." />
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <span>Total Audits</span>

              <strong>{reports.total_audits}</strong>

              <small>Audit history</small>
            </div>

            <div className="stat-card">
              <span>Average Score</span>

              <strong>{reports.average_score}%</strong>

              <small>Across audits</small>
            </div>

            <div className="stat-card">
              <span>Backend</span>

              <strong>{backend}</strong>

              <small>FastAPI service</small>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>How NetGuard AI works</h3>

            <div className="pipeline">
              <div>
                <strong>01</strong>
                <span>Upload Config</span>
              </div>

              <div className="pipeline-arrow">→</div>

              <div>
                <strong>02</strong>
                <span>AI → SBM</span>
              </div>

              <div className="pipeline-arrow">→</div>

              <div>
                <strong>03</strong>
                <span>Compliance</span>
              </div>

              <div className="pipeline-arrow">→</div>

              <div>
                <strong>04</strong>
                <span>Remediation</span>
              </div>

              <div className="pipeline-arrow">→</div>

              <div>
                <strong>05</strong>
                <span>PDF Report</span>
              </div>
            </div>
          </div>

          <div className="dashboard-card">
            <h3>Audit workflow</h3>

            <p>
              Upload a network configuration, allow NetGuard AI to
              extract the Security Baseline Model, select a compliance
              framework, and run an audit.
            </p>

            <a className="secondary-button" href="/upload">
              Start an Audit
            </a>
          </div>

          <div className="dashboard-card">
            <h3>Recent Audits</h3>

            {reports.recent_audits.length === 0 ? (
              <p>No audits have been run yet.</p>
            ) : (
              <div className="framework-list">
                {reports.recent_audits.map((audit) => (
                  <div
                    className="framework-item"
                    key={audit.audit_id}
                  >
                    <div>
                      <strong>{audit.filename}</strong>

                      <div>
                        <small>
                          {audit.framework} • Audit #{audit.audit_id}
                        </small>
                      </div>
                    </div>

                    <div>
                      <strong>{audit.score}%</strong>

                      <div>
                        <small>
                          {audit.passed} passed / {audit.failed} failed
                        </small>
                      </div>
                    </div>

                    <a
                      className="secondary-button"
                      href={`/report/${audit.audit_id}`}
                    >
                      View
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;