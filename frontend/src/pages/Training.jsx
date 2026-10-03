import { useEffect, useState } from "react";

import Loading from "../components/Loading";

import {
  getPendingTraining,
  saveTrainingLabel,
  reanalyzeConfig,
  getTrainingLabels,
} from "../services/api";


function Training() {

  const [pending, setPending] = useState([]);
  const [labels, setLabels] = useState([]);

  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [mappings, setMappings] = useState({});


  async function loadTraining() {

    setLoading(true);
    setError("");

    try {

      const [pendingData, labelData] =
        await Promise.all([
          getPendingTraining(),
          getTrainingLabels(),
        ]);

      setPending(
        pendingData.items || []
      );

      setLabels(
        labelData || []
      );

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {
    loadTraining();
  }, []);


  function updateMapping(
    index,
    field,
    value
  ) {

    setMappings((previous) => ({

      ...previous,

      [index]: {

        ...previous[index],

        [field]: value,

      },

    }));
  }


  async function handleSave(item, index) {

    const mapping =
      mappings[index] || {};

    if (!mapping.sbm_field_path) {

      setError(
        "Please enter an SBM field path."
      );

      return;
    }

    if (
      mapping.mapped_value === undefined ||
      mapping.mapped_value === ""
    ) {

      setError(
        "Please enter the mapped value."
      );

      return;
    }

    setSavingId(index);
    setError("");
    setMessage("");

    try {

      await saveTrainingLabel({

        config_file_id:
          item.config_file_id,

        raw_line:
          item.raw_line,

        sbm_field_path:
          mapping.sbm_field_path,

        mapped_value:
          mapping.mapped_value,

      });

      setMessage(
        "Training mapping saved successfully."
      );

      await loadTraining();

    } catch (err) {

      setError(err.message);

    } finally {

      setSavingId(null);

    }
  }


  async function handleReanalyze(
    fileId
  ) {

    setError("");
    setMessage("");

    try {

      const result =
        await reanalyzeConfig(
          fileId
        );

      setMessage(
        `Re-analysis complete. New confidence: ${Math.round(
          result.sbm.confidence * 100
        )}%`
      );

      await loadTraining();

    } catch (err) {

      setError(err.message);

    }
  }


  if (loading) {

    return (
      <Loading
        text="Loading training data..."
      />
    );

  }


  return (

    <div>

      <div className="page-heading">

        <div>

          <h2>
            AI Training Center
          </h2>

          <p>
            Teach NetGuard how unknown
            configuration lines map to the
            Security Baseline Model.
          </p>

        </div>

      </div>


      {error && (
        <div className="error-box">
          {error}
        </div>
      )}


      {message && (
        <div className="success-box">
          {message}
        </div>
      )}


      <div className="dashboard-card">

        <div className="card-header">

          <div>

            <h3>
              Unknown Configuration
            </h3>

            <p>
              These lines need administrator
              mapping before they can be
              reliably understood.
            </p>

          </div>

          <strong>
            {pending.length} pending
          </strong>

        </div>


        {pending.length === 0 ? (

          <div className="success-box">

            <h3>
              No pending mappings
            </h3>

            <p>
              All currently detected unknown
              configuration blocks have been
              handled.
            </p>

          </div>

        ) : (

          <div className="findings">

            {pending.map(
              (item, index) => {

                const mapping =
                  mappings[index] || {};

                return (

                  <div
                    className="finding-card"
                    key={`${item.config_file_id}-${index}`}
                  >

                    <div className="finding-header">

                      <div>

                        <strong>
                          {item.filename}
                        </strong>

                        <h4>
                          Unknown Configuration
                        </h4>

                      </div>

                      <span
                        className="severity medium"
                      >
                        {Math.round(
                          item.confidence * 100
                        )}% confidence
                      </span>

                    </div>


                    <div className="finding-grid">

                      <div>

                        <span>
                          Vendor
                        </span>

                        <strong>
                          {item.vendor}
                        </strong>

                      </div>


                      <div>

                        <span>
                          OS
                        </span>

                        <strong>
                          {item.os}
                        </strong>

                      </div>


                      <div>

                        <span>
                          Reason
                        </span>

                        <strong>
                          {item.reason}
                        </strong>

                      </div>

                    </div>


                    <div>

                      <span>
                        Raw configuration line
                      </span>

                      <pre>
                        {item.raw_line}
                      </pre>

                    </div>


                    <div className="form-card">

                      <label>

                        <span>
                          SBM field path
                        </span>

                        <input
                          type="text"
                          placeholder="security_controls.remote_access_protocols.ssh.enabled"
                          value={
                            mapping.sbm_field_path ||
                            ""
                          }
                          onChange={(event) =>
                            updateMapping(
                              index,
                              "sbm_field_path",
                              event.target.value
                            )
                          }
                        />

                      </label>


                      <label>

                        <span>
                          Meaning / value
                        </span>

                        <input
                          type="text"
                          placeholder="true"
                          value={
                            mapping.mapped_value ||
                            ""
                          }
                          onChange={(event) =>
                            updateMapping(
                              index,
                              "mapped_value",
                              event.target.value
                            )
                          }
                        />

                      </label>


                      <button
                        className="primary-button"
                        disabled={
                          savingId === index
                        }
                        onClick={() =>
                          handleSave(
                            item,
                            index
                          )
                        }
                      >

                        {savingId === index
                          ? "Saving..."
                          : "Save Mapping"}

                      </button>

                    </div>


                    <button
                      className="secondary-button"
                      onClick={() =>
                        handleReanalyze(
                          item.config_file_id
                        )
                      }
                    >
                      Re-analyze Configuration
                    </button>

                  </div>

                );

              }
            )}

          </div>

        )}

      </div>


      <div className="dashboard-card">

        <h3>
          Approved Training Mappings
        </h3>

        {labels.length === 0 ? (

          <p>
            No approved mappings yet.
          </p>

        ) : (

          <div className="framework-list">

            {labels.map((label) => (

              <div
                className="framework-item"
                key={label.id}
              >

                <div>

                  <strong>
                    {label.raw_line}
                  </strong>

                  <small>
                    {label.vendor} • {label.os}
                  </small>

                </div>


                <div>

                  <code>
                    {label.sbm_field_path}
                  </code>

                </div>


                <div>

                  <strong>
                    {label.mapped_value}
                  </strong>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </div>

  );
}


export default Training;