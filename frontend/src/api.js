const KEY = "gw_token";
export function getToken() { return localStorage.getItem(KEY) || ""; }
export function setToken(t) { t ? localStorage.setItem(KEY, t) : localStorage.removeItem(KEY); }
export async function api(path, opts = {}) {
  const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  const tok = getToken();
  if (tok) headers.Authorization = `Bearer ${tok}`;
  const res = await fetch(path, { ...opts, headers, body: opts.body && typeof opts.body !== "string" ? JSON.stringify(opts.body) : opts.body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(data.detail || `HTTP ${res.status}`), { status: res.status, data });
  return data;
}
export const register = (handle, password, tier = "free") => api("/api/auth/register", { method: "POST", body: { handle, password, tier } });
export const login = (handle, password) => api("/api/auth/login", { method: "POST", body: { handle, password } });
