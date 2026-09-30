import { useCallback, useEffect, useState } from 'react';

export type ActionType = 'TRANSFER' | 'EXPEDITE' | 'URGENT_ORDER';
export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM';

export interface QueueItem {
  action_id: string; snapshot_date: string; priority: number; action_type: ActionType; severity: Severity;
  store_id: string; store_name: string; city: string; uf: string; region: string;
  sku: string; product_name: string; category: string;
  from_id: string | null; from_store_name: string | null; from_city: string | null;
  transfer_km: number | null; donor_days_of_cover: number | null;
  units: number; eta_days: number; on_hand_units: number; days_of_cover: number; inbound_units: number;
  eta_adjusted_days: number | null; supplier_id: string; supplier_name: string; supplier_on_time_rate: number;
  risk_probability: number; units_at_risk: number; revenue_at_risk: number; revenue_protected: number;
  rationale: string; rationale_source: 'AGENTE' | 'REGRA'; agent_confidence: string | null;
  agent_changed_action: boolean | null; agent_tools: string | null;
  decision?: 'APPROVED' | 'REJECTED' | null; decided_by?: string | null; decided_at?: string | null;
}
export interface Overview {
  as_of: string; days: number; lost_revenue_period: number; lost_share: number; lost_revenue_annualized: number;
  lost_revenue_7d: number; stockout_rate_today: number; stockout_rate_7d: number;
  queue_size: number; queue_critical: number; revenue_at_risk_7d: number; revenue_protectable_7d: number;
  action_mix: { type: ActionType; n: number; rs: number }[];
  protected_today: number; approved_today: number; rejected_today: number;
  stores_in_alert: number; stores_total: number;
  trend: { date: string; stockout_rate: number; lost_revenue: number }[];
}
export interface JourneyStep { step: string; stage: string; product: string; status: string; detail: string; job_run_id: string; updated_at: string | null }
export interface Journey { steps: JourneyStep[]; model: Record<string, number> }
export interface Store {
  store_id: string; store_name: string; city: string; uf: string; region: string; store_format: string;
  lat: number; lon: number; stockout_rate_7d: number; lost_revenue_7d: number; revenue_7d: number;
  queue_n: number; queue_critical: number; revenue_at_risk: number;
}
export interface Route { action_id: string; from_id: string; store_id: string; product_name: string; units: number; transfer_km: number; revenue_protected: number; severity: Severity; decision: string | null }
export interface Network { stores: Store[]; routes: Route[] }
/** Workspace deep-links (skill databricks-arch-diagram): empty url = inert tile. */
export type Resources = Record<string, { id: string; url: string }>;

export type QueueSort = 'impacto' | 'criticidade';

export interface StoreDetail {
  store: Store;
  actions: QueueItem[];
  at_risk: { product_name: string; category: string; on_hand_units: number; avg_units_28d: number; days_of_cover: number; inbound_units: number; days_until_inbound: number | null; risk_probability: number; revenue_at_risk: number }[];
}
export interface AgentView {
  items: QueueItem[]; run_detail: string | null; run_at: string | null; tool_usage: Record<string, number>; changed: number;
  suppliers: { supplier_name: string; orders_received: number; on_time_rate: number; avg_delay_when_late: number }[];
}
export interface LakebaseStatus {
  host: string; database: string; postgres: string; connected_as: string;
  tables: { table_schema: string; table_name: string; rows: number }[];
  latency: { calls: number; p50?: number; p95?: number; p99?: number; min?: number; max?: number; mean?: number };
  recent_actions: { decision: string; decided_by: string; decided_at: string; revenue_protected: number; product_name: string; store_name: string }[];
  recent_genie: { asked_at: string; user_email: string; question: string; row_count: number; duration_ms: number; status: string }[];
}
export interface GenieAnswer { conversation_id: string; status: string; answer: string | null; sql: string | null; description?: string; columns: string[]; rows: (string | null)[][]; duration_ms: number }

async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...init });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json() as Promise<T>;
}

export const api = {
  overview: () => j<Overview>('/api/overview'),
  journey: () => j<Journey>('/api/journey'),
  resources: () => j<Resources>('/api/resources'),
  network: () => j<Network>('/api/network'),
  store: (id: string) => j<StoreDetail>(`/api/stores/${id}`),
  queue: (p: { action_type?: string; severity?: string; store_id?: string; sort?: QueueSort; limit?: number } = {}) => {
    const qs = new URLSearchParams(Object.entries(p).filter(([, v]) => v).map(([k, v]) => [k, String(v)]));
    return j<QueueItem[]>(`/api/queue?${qs}`);
  },
  decide: (id: string, decision: 'APPROVED' | 'REJECTED') =>
    j<{ decision: string; decided_by: string; revenue_protected: number }>(`/api/queue/${id}/decide`, { method: 'POST', body: JSON.stringify({ decision }) }),
  approveAll: (ids: string[]) => j<{ approved: unknown[] }>('/api/queue/approve-all', { method: 'POST', body: JSON.stringify({ action_ids: ids }) }),
  decisions: () => j<{ action_id: string; decision: string; decided_by: string; decided_at: string; units: number; revenue_protected: number; action_type: ActionType; store_name: string; product_name: string; from_store_name: string | null }[]>('/api/decisions'),
  agent: () => j<AgentView>('/api/agent'),
  lakebase: () => j<LakebaseStatus>('/api/lakebase/status'),
  genie: (question: string, conversation_id?: string) =>
    j<GenieAnswer>('/api/genie/ask', { method: 'POST', body: JSON.stringify({ question, conversation_id }) }),
};

/** Poll an endpoint; returns [data, reload, error]. */
export function usePoll<T>(fn: () => Promise<T>, ms = 20000, deps: unknown[] = []): [T | null, () => void, string | null] {
  const [data, setData] = useState<T | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const load = useCallback(() => { fn().then((d) => { setData(d); setErr(null); }).catch((e) => setErr(String(e))); }, deps); // eslint-disable-line
  useEffect(() => { load(); const t = setInterval(load, ms); return () => clearInterval(t); }, [load, ms]);
  return [data, load, err];
}
