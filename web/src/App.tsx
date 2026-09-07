import { useEffect, useState } from "react";
import { fetchFunds, fetchStrategies, type Fund } from "./api";

export default function App() {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [strategy, setStrategy] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStrategies()
      .then(setStrategies)
      .catch(() => setStrategies([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchFunds(strategy || undefined)
      .then((data) => {
        setFunds(data.funds);
        setError(null);
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [strategy]);

  return (
    <>
      <header className="topbar">
        <h1>OWL Funds</h1>
      </header>

      <main>
        <div className="card">
          <div className="card-toolbar">
            <label>
              Strategy
              <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                <option value="">All</option>
                {strategies.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>
            {!loading && !error && <span className="count">{funds.length} funds</span>}
          </div>

          {error && <p className="error">Error: {error}</p>}

          {loading ? (
            <p className="muted">Loading…</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Manager</th>
                    <th>Strategy</th>
                    <th>Vintage</th>
                    <th>Commitment (raw)</th>
                    <th>Reported</th>
                  </tr>
                </thead>
                <tbody>
                  {funds.map((f) => (
                    <tr key={f.fund_id}>
                      <td>{f.fund_id}</td>
                      <td>{f.fund_name}</td>
                      <td>{f.manager}</td>
                      <td>
                        <span className="pill">{f.strategy}</span>
                      </td>
                      <td>{f.vintage_year}</td>
                      <td className="commitment">{f.commitment ?? "—"}</td>
                      <td>{f.reported_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
