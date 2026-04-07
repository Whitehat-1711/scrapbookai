const normalizeBaseUrl = (value) => {
  if (!value) {
    return "http://localhost:8000";
  }
  return value.endsWith("/") ? value.slice(0, -1) : value;
};

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_URL);

const buildUrl = (path) => `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

const defaultHeaders = {
  "Content-Type": "application/json",
};

async function request(path, { method = "GET", body, headers, signal } = {}) {
  const response = await fetch(buildUrl(path), {
    method,
    headers: {
      ...defaultHeaders,
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
    signal,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    // no-op: allow payload to stay null for non-JSON responses
  }

  if (!response.ok) {
    const message = payload?.detail || payload?.error || response.statusText || "Request failed";
    const reqError = new Error(message);
    reqError.status = response.status;
    reqError.payload = payload;
    throw reqError;
  }

  return payload;
}

export const api = {
  keywords: {
    cluster: (payload, options = {}) => request("/keywords/cluster", { method: "POST", body: payload, ...options }),
    suggest: ({ seed, location = "India" }) => {
      const params = new URLSearchParams({ seed, location });
      return request(`/keywords/suggest?${params.toString()}`);
    },
  },
  serp: {
    analyze: (payload, options = {}) => request("/serp/analyze", { method: "POST", body: payload, ...options }),
  },
  blog: {
    generate: (payload, options = {}) => request("/blog/generate", { method: "POST", body: payload, ...options }),
    titleSuggestions: (payload, options = {}) =>
      request("/blog/title-suggestions", { method: "POST", body: payload, ...options }),
    list: ({ limit = 50, skip = 0, status } = {}, options = {}) => {
      const params = new URLSearchParams({ limit, skip });
      if (status) params.set("status", status);
      return request(`/blog/list?${params.toString()}`, options);
    },
    count: ({ status } = {}, options = {}) => {
      const params = new URLSearchParams();
      if (status) params.set("status", status);
      return request(`/blog/list/count?${params.toString()}`, options);
    },
    get: (id, options = {}) => request(`/blog/${id}`, options),
    updateStatus: (id, status, options = {}) =>
      request(`/blog/${id}/status`, { method: "PUT", body: { status }, ...options }),
    delete: (id, options = {}) => request(`/blog/${id}`, { method: "DELETE", ...options }),
  },
  seo: {
    analyze: (payload, options = {}) => request("/seo/analyze", { method: "POST", body: payload, ...options }),
    detectAI: (payload, options = {}) => request("/seo/detect-ai", { method: "POST", body: payload, ...options }),
    snippet: (payload, options = {}) => request("/seo/snippet", { method: "POST", body: payload, ...options }),
    links: (payload, options = {}) => request("/seo/links", { method: "POST", body: payload, ...options }),
  },
  humanize: {
    run: (payload, options = {}) => request("/humanize", { method: "POST", body: payload, ...options }),
  },
  health: () => request("/health"),
};
