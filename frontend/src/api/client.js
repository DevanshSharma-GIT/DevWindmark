const API_BASE = import.meta.env.VITE_API_URL || "";

async function request(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });
  const response = await fetch(url.toString());
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    const message = detail.detail || `Request failed (${response.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return response.json();
}

export const api = {
  health: () => request("/api/health"),
  summary: (params) => request("/api/summary", params),
  forecasts: (params) => request("/api/forecasts", params),
  accuracy: (params) => request("/api/accuracy", params),
  insights: () => request("/api/insights"),
  methodology: () => request("/api/methodology"),
};

export function formatMw(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "Unavailable";
  }
  return `${Number(value).toLocaleString("en-GB", { maximumFractionDigits: 1 })} MW`;
}

export function formatPercent(value) {
  if (value === null || value === undefined) {
    return "Unavailable";
  }
  return `${Number(value).toLocaleString("en-GB", { maximumFractionDigits: 2 })}%`;
}

export function formatStamp(value) {
  if (!value) {
    return "Unavailable";
  }
  return new Date(value).toLocaleString("en-GB", { timeZone: "UTC", hour12: false }) + " UTC";
}
