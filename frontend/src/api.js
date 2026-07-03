const API = 'http://localhost:8000';

export const apiFetch = async (path, options = {}) => {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
};

export const api = {
  health:         ()           => apiFetch('/health'),
  stats:          ()           => apiFetch('/dashboard/stats'),
  agents:         ()           => apiFetch('/agents'),
  createAgent:    (body)       => apiFetch('/agents', { method: 'POST', body: JSON.stringify(body) }),
  scenarios:      ()           => apiFetch('/scenarios'),
  genScenarios:   (body)       => apiFetch('/scenarios/generate', { method: 'POST', body: JSON.stringify(body) }),
  baselines:      ()           => apiFetch('/baseline'),
  createBaseline: (body)       => apiFetch('/baseline/create', { method: 'POST', body: JSON.stringify(body) }),
  sessions:       ()           => apiFetch('/sessions'),
  alerts:         ()           => apiFetch('/alerts'),
  drift:          (baselineId) => apiFetch(`/drift?baseline_id=${baselineId}`),
  login:          (body)       => apiFetch('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
};
