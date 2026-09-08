import { useEffect, useState } from "react";
import { fetchFunds, fetchStrategies, formatCommitment, type Fund } from "./api";

const PAGE_SIZES = [10, 30, 50] as const;
type PageSize = (typeof PAGE_SIZES)[number] | "all";

export default function App() {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [total, setTotal] = useState(0);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [strategy, setStrategy] = useState("");
  const [pageSize, setPageSize] = useState<PageSize>(10);
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const paged = pageSize !== "all";
  const offset = paged ? (page - 1) * pageSize : 0;
  const pageCount = paged ? Math.max(1, Math.ceil(total / pageSize)) : 1;

  useEffect(() => {
    fetchStrategies()
      .then(setStrategies)
      .catch(() => setStrategies([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchFunds({
      strategy: strategy || undefined,
      limit: paged ? pageSize : undefined,
      offset,
    })
      .then((data) => {
        setFunds(data.funds);
        setTotal(data.total);
        setError(null);
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false));
  }, [strategy, pageSize, offset, paged]);

  // If the current page falls outside the result set (e.g. after filtering), snap back.
  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const rangeLabel = paged
    ? `${total === 0 ? 0 : offset + 1}–${Math.min(offset + pageSize, total)} of ${total}`
    : `${total} funds`;

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
              <select
                value={strategy}
                onChange={(e) => {
                  setStrategy(e.target.value);
                  setPage(1);
                }}
              >
                <option value="">All</option>
                {strategies.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Rows
              <select
                value={String(pageSize)}
                onChange={(e) => {
                  const v = e.target.value;
                  setPageSize(v === "all" ? "all" : (Number(v) as PageSize));
                  setPage(1);
                }}
              >
                {PAGE_SIZES.map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
                <option value="all">All</option>
              </select>
            </label>

            <div className="pager">
              <span className="count">{rangeLabel}</span>
              {paged && (
                <>
                  <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1}>
                    Prev
                  </button>
                  <span className="count">
                    {page} / {pageCount}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
                    disabled={page >= pageCount}
                  >
                    Next
                  </button>
                </>
              )}
            </div>
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
                    <th>Commitment</th>
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
                      <td className="commitment">
                        {formatCommitment(f.commitment_cents, f.currency)}
                      </td>
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
