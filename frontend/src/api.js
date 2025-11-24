// Minimal API helper for frontend
export function getApiBase() {
  return import.meta.env.VITE_API_BASE || 'http://localhost:8000';
}

async function parseResponse(res) {
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch (e) {
    return text;
  }
}

export async function apiFetch(path, opts = {}) {
  const base = getApiBase();
  const url = path.startsWith('http') ? path : `${base}${path}`;

  const headers = new Headers(opts.headers || {});

  // Attach JSON content-type if sending a body that is not FormData
  if (opts.body && !(opts.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const token = localStorage.getItem('authToken');
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const res = await fetch(url, { ...opts, headers, credentials: 'include' });
  const data = await parseResponse(res);
  if (!res.ok) {
    const err = new Error('Request failed');
    err.status = res.status;
    err.body = data;
    throw err;
  }
  return data;
}

export default apiFetch;
