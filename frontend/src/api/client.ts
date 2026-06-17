/**
 * API client — thin fetch wrapper for the backend API.
 *
 * Base URL is proxied through Vite in development (localhost:5173 → localhost:8000).
 * In production, the frontend is served by FastAPI on the same origin.
 */

const API_BASE = "/api";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const config: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorBody = await response.text();
    throw new ApiError(
      response.status,
      errorBody || response.statusText,
    );
  }

  return response.json();
}

// ── Hand history endpoints ─────────────────────────────────────────────────

export const handsApi = {
  list: (params: Record<string, string | number | undefined> = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) query.set(key, String(value));
    });
    return request<any>(`/hands/?${query}`);
  },
  get: (id: number) => request<any>(`/hands/${id}`),
  search: (q: string, limit = 50) =>
    request<any>(`/hands/search?q=${encodeURIComponent(q)}&limit=${limit}`),
};

// ── Import endpoints ───────────────────────────────────────────────────────

export const importApi = {
  upload: (file: File, site?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (site) formData.append("site", site);
    return fetch(`${API_BASE}/import/upload`, {
      method: "POST",
      body: formData,
    });
  },
  formats: () => request<any>("/import/formats"),
  logs: (page = 1) => request<any>(`/import/logs?page=${page}`),
};

// ── Analytics endpoints ─────────────────────────────────────────────────────

export const analyticsApi = {
  summary: (params: Record<string, string | undefined> = {}) => {
    const query = new URLSearchParams(params as Record<string, string>);
    return request<any>(`/analytics/summary?${query}`);
  },
  profitChart: (params: Record<string, string | undefined> = {}) => {
    const query = new URLSearchParams(params as Record<string, string>);
    return request<any>(`/analytics/profit-chart?${query}`);
  },
  positionStats: (params: Record<string, string | undefined> = {}) => {
    const query = new URLSearchParams(params as Record<string, string>);
    return request<any>(`/analytics/position-stats?${query}`);
  },
};

// ── Player endpoints ────────────────────────────────────────────────────────

export const playersApi = {
  list: (params: Record<string, string | number | undefined> = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) query.set(key, String(value));
    });
    return request<any>(`/players/?${query}`);
  },
  get: (name: string, site: string) =>
    request<any>(`/players/${encodeURIComponent(name)}?site=${encodeURIComponent(site)}`),
};

// ── Session endpoints ───────────────────────────────────────────────────────

export const sessionsApi = {
  list: (params: Record<string, string | number | undefined> = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) query.set(key, String(value));
    });
    return request<any>(`/sessions/?${query}`);
  },
  get: (id: number) => request<any>(`/sessions/${id}`),
};

// ── AI endpoints ────────────────────────────────────────────────────────────

export const aiApi = {
  query: (question: string) =>
    request<any>("/ai/query", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
};
