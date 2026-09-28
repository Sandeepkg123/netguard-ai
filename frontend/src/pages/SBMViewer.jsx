import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSBM } from "../services/api";
import Loading from "../components/Loading";

function SBMViewer() {
  const { fileId } = useParams();

  const [sbm, setSbm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getSBM(fileId)
      .then(setSbm)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [fileId]);

  if (loading) {
    return <Loading text="Loading Security Baseline Model..." />;
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Security Baseline Model</h2>
          <p>{sbm.filename}</p>
        </div>

        <a
          href={`/audit/${fileId}`}
          className="primary-button"
        >
          Run Audit
        </a>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Vendor</span>
          <strong>{sbm.vendor}</strong>
        </div>

        <div className="stat-card">
          <span>Operating System</span>
          <strong>{sbm.os}</strong>
        </div>

        <div className="stat-card">
          <span>Hostname</span>
          <strong>{sbm.hostname || "Unknown"}</strong>
        </div>

        <div className="stat-card">
          <span>Confidence</span>
          <strong>
            {Math.round(sbm.confidence * 100)}%
          </strong>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Security Controls</h3>

        <pre className="json-viewer">
          {JSON.stringify(sbm.security_controls, null, 2)}
        </pre>
      </div>

      <div className="dashboard-card">
        <h3>
          Unknown Blocks ({sbm.unknown_blocks?.length || 0})
        </h3>

        {sbm.unknown_blocks?.length === 0 ? (
          <p className="muted">
            No unknown configuration blocks were detected.
          </p>
        ) : (
          <div>
            {sbm.unknown_blocks.map((block, index) => (
              <div className="unknown-block" key={index}>
                <code>{block.raw_line}</code>
                <p>{block.reason}</p>
                <small>
                  Confidence:{" "}
                  {Math.round(block.confidence * 100)}%
                </small>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default SBMViewer;