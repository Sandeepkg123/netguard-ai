import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  getFrameworks,
  runAudit,
  getSBM,
} from "../services/api";
import Loading from "../components/Loading";

function Audit() {
  const { fileId } = useParams();
  const navigate = useNavigate();

  const [sbm, setSbm] = useState(null);
  const [frameworks, setFrameworks] = useState([]);
  const [frameworkId, setFrameworkId] = useState("");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [sbmData, frameworkData] = await Promise.all([
          getSBM(fileId),
          getFrameworks(),
        ]);

        setSbm(sbmData);
        setFrameworks(frameworkData);

        if (frameworkData.length > 0) {
          setFrameworkId(String(frameworkData[0].id));
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [fileId]);

  async function handleAudit() {
    if (!frameworkId) {
      setError("Please select a framework.");
      return;
    }

    setError("");
    setRunning(true);

    try {
      const result = await runAudit(
        Number(fileId),
        Number(frameworkId)
      );

      navigate(`/report/${result.audit_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

  if (loading) {
    return <Loading text="Preparing audit..." />;
  }

  if (error && !sbm) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Run Compliance Audit</h2>
          <p>Select a framework and audit the configuration.</p>
        </div>
      </div>

      <div className="audit-layout">
        <div className="dashboard-card">
          <h3>Configuration</h3>

          <div className="info-list">
            <div>
              <span>File</span>
              <strong>{sbm.filename}</strong>
            </div>

            <div>
              <span>Vendor</span>
              <strong>{sbm.vendor}</strong>
            </div>

            <div>
              <span>Operating System</span>
              <strong>{sbm.os}</strong>
            </div>

            <div>
              <span>Hostname</span>
              <strong>{sbm.hostname || "Unknown"}</strong>
            </div>
          </div>

          <button
            className="secondary-button"
            onClick={() => navigate(`/sbm/${fileId}`)}
          >
            View SBM
          </button>
        </div>

        <div className="dashboard-card">
          <h3>Compliance Framework</h3>

          <label className="field-label">
            Select Framework
          </label>

          <select
            value={frameworkId}
            onChange={(event) =>
              setFrameworkId(event.target.value)
            }
            className="select-input"
          >
            {frameworks.map((framework) => (
              <option
                key={framework.id}
                value={framework.id}
              >
                {framework.name}{" "}
                {framework.version
                  ? `(${framework.version})`
                  : ""}
              </option>
            ))}
          </select>

          <div className="framework-list">
            {frameworks.map((framework) => (
              <div
                key={framework.id}
                className="framework-item"
              >
                <strong>{framework.name}</strong>
                <span>
                  {framework.rule_count} rules
                </span>
              </div>
            ))}
          </div>

          {error && <div className="error-box">{error}</div>}

          <button
            className="primary-button full-width"
            onClick={handleAudit}
            disabled={running}
          >
            {running
              ? "Running Compliance Audit..."
              : "Run Compliance Audit"}
          </button>

          {running && (
            <Loading text="Compliance engine + remediation engine running..." />
          )}
        </div>
      </div>
    </div>
  );
}

export default Audit;