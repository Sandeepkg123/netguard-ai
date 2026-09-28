import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadConfig } from "../services/api";
import Loading from "../components/Loading";

function Upload() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) {
      setError("Please select a configuration file.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const data = await uploadConfig(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h2>Upload Configuration</h2>
          <p>
            Upload a network device configuration for AI-based analysis.
          </p>
        </div>
      </div>

      <div className="form-card">
        <form onSubmit={handleUpload}>
          <label className="upload-box">
            <input
              type="file"
              accept=".conf,.cfg,.txt"
              onChange={(event) => {
                setFile(event.target.files[0]);
                setResult(null);
                setError("");
              }}
            />

            <div className="upload-icon">↑</div>

            <strong>
              {file ? file.name : "Choose configuration file"}
            </strong>

            <span>
              Plain-text configuration • Maximum 10 MB
            </span>
          </label>

          {file && (
            <div className="selected-file">
              <span>Selected:</span>
              <strong>{file.name}</strong>
            </div>
          )}

          {error && <div className="error-box">{error}</div>}

          <button
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Upload & Analyze"}
          </button>
        </form>

        {loading && (
          <Loading text="Gemini is extracting the Security Baseline Model..." />
        )}

        {result && (
          <div className="success-box">
            <h3>Configuration analyzed successfully</h3>

            <div className="result-grid">
              <div>
                <span>File ID</span>
                <strong>{result.id}</strong>
              </div>

              <div>
                <span>Vendor</span>
                <strong>{result.sbm?.vendor}</strong>
              </div>

              <div>
                <span>OS</span>
                <strong>{result.sbm?.os}</strong>
              </div>

              <div>
                <span>Confidence</span>
                <strong>
                  {Math.round((result.sbm?.confidence || 0) * 100)}%
                </strong>
              </div>
            </div>

            <div className="button-row">
              <button
                className="secondary-button"
                onClick={() =>
                  navigate(`/sbm/${result.id}`)
                }
              >
                View SBM
              </button>

              <button
                className="primary-button"
                onClick={() =>
                  navigate(`/audit/${result.id}`)
                }
              >
                Continue to Audit
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Upload;