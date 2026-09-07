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
    <main>
      <h1>Funds</h1>

      <label>
        Strategy:{" "}
        <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
          <option value="">All</option>
          {strategies.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>

      {error && <p className="error">Error: {error}</p>}

      {loading ? (
        <p>Loading…</p>
      ) : (
        <>
          <p>{funds.length} funds</p>
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
                  <td>{f.strategy}</td>
                  <td>{f.vintage_year}</td>
                  <td>{f.commitment ?? "—"}</td>
                  <td>{f.reported_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </main>
  );
}
