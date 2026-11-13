import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001/api/disagreements/";

function App() {
  const organization = "ORG-A";
  const [reason, setReason] = useState("");
  const [sort, setSort] = useState("asc");
  const [disagreements, setDisagreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function fetchDisagreements() {
      setLoading(true);
      setError("");
      setDisagreements([]);

      try {
        const params = new URLSearchParams({
          org_id: organization,
          sort: sort,
        });

        if (reason) {
          params.append("reason", reason);
        }

        const response = await fetch(
          `${API_URL}?${params.toString()}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch disagreements");
        }

        const data = await response.json();

        setDisagreements(data.disagreements);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchDisagreements();

    return () => controller.abort();
  }, [organization, reason, sort]);

  return (
    <div className="container">
      <header>
        <h1>ADOSX Disagreement Dashboard</h1>
        <p>Compare System A and System B records</p>
      </header>

      <div className="filters">
<div>
  <label>Organization</label>
  <input
    type="text"
    value={organization}
    readOnly
    className="organization-input"
  />
</div>

        <div>
          <label>Filter by Reason</label>
          <select
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          >
            <option value="">All Reasons</option>
            <option value="MISSING_IN_B">Missing in B</option>
            <option value="ORPHAN_IN_B">Orphan in B</option>
            <option value="DUPLICATE_IN_B">Duplicate in B</option>
            <option value="VALUE_MISMATCH">Value Mismatch</option>
            <option value="INVALID_VALUE">Invalid Value</option>
            <option value="LOCATION_MISMATCH">Location Mismatch</option>
          </select>
        </div>

        <div>
          <label>Sort by Value</label>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
          >
            <option value="asc">Lowest First</option>
            <option value="desc">Highest First</option>
          </select>
        </div>
      </div>

      <div className="summary">
        <h2>Total Disagreements</h2>
        <span>{disagreements.length}</span>
      </div>

      {loading && <p>Loading disagreements...</p>}

      {error && <p className="error">{error}</p>}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Reason</th>
                <th>System A Value</th>
                <th>System B Value</th>
                <th>Location</th>
              </tr>
            </thead>

            <tbody>
              {disagreements.map((item, index) => (
                <tr key={`${item.record_id}-${item.reason}-${index}`}>
                  <td>{item.record_id}</td>

                  <td>
                    <span className="badge">
                      {item.reason.replaceAll("_", " ")}
                    </span>
                  </td>

                  <td>{item.system_a_value ?? "—"}</td>

                  <td>{item.system_b_value ?? "—"}</td>

                  <td>{item.location_id}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {disagreements.length === 0 && (
            <p className="empty">No disagreements found.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;