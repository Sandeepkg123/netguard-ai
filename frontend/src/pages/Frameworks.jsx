import { useEffect, useState } from "react";
import { getFrameworks } from "../services/api";
import Loading from "../components/Loading";

function Frameworks() {
  const [frameworks, setFrameworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getFrameworks()
      .then(setFrameworks)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Loading text="Loading frameworks..." />;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Compliance Frameworks</h2>
          <p>
            Frameworks currently available to the auditor.
          </p>
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="framework-grid">
        {frameworks.map((framework) => (
          <div
            className="framework-card"
            key={framework.id}
          >
            <div className="framework-icon">✓</div>

            <h3>{framework.name}</h3>

            <p>
              Version:{" "}
              {framework.version || "Not specified"}
            </p>

            <div className="framework-meta">
              <span>
                {framework.rule_count} rules
              </span>

              <span>
                {framework.source}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Frameworks;