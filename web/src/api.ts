export interface Fund {
  fund_id: string;
  fund_name: string;
  manager: string;
  strategy: string;
  vintage_year: number;
  commitment: string | null;
  reported_at: string;
}

export interface FundsResponse {
  funds: Fund[];
  total: number;
  limit: number | null;
  offset: number;
}

export interface FundsQuery {
  strategy?: string;
  limit?: number;
  offset?: number;
}

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(path, BASE_URL);
  for (const [key, value] of Object.entries(params ?? {})) {
    url.searchParams.set(key, value);
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export function fetchFunds({ strategy, limit, offset }: FundsQuery = {}): Promise<FundsResponse> {
  const params: Record<string, string> = {};
  if (strategy) params.strategy = strategy;
  if (limit != null) params.limit = String(limit);
  if (offset) params.offset = String(offset);
  return getJson<FundsResponse>("/funds", params);
}

export async function fetchStrategies(): Promise<string[]> {
  const data = await getJson<{ strategies: string[] }>("/strategies");
  return data.strategies;
}
