const BASE = import.meta.env.VITE_API_URL || '';

function getToken() {
  return localStorage.getItem('ss_token');
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem('ss_token');
    window.location.reload();
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  login: (username, password) => {
    const body = new URLSearchParams({ username, password });
    return fetch(`${BASE}/auth/token`, { method: 'POST', body }).then(async (r) => {
      if (!r.ok) throw new Error('Invalid credentials');
      return r.json();
    });
  },
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request('/users/me'),
  tasks: {
    list: () => request('/tasks/'),
    create: (data) => request('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/tasks/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id) => request(`/tasks/${id}`, { method: 'DELETE' }),
    transition: (id, new_status) => request(`/tasks/${id}/transition`, { method: 'POST', body: JSON.stringify({ new_status }) }),
  },
  ai: {
    suggest: (mode, title) => {
      const params = new URLSearchParams({ mode });
      if (title) params.set('title', title);
      return request(`/ai/suggest?${params}`, { method: 'POST' });
    },
  },
  stats: {
    topUsers: () => request('/stats/top-users'),
    cycleTime: () => request('/stats/cycle-time'),
  },
};
