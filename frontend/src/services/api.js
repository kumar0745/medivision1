const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export function getToken() {
  return localStorage.getItem('mv_token');
}

export function setSession(data) {
  localStorage.setItem('mv_token', data.access_token);
  localStorage.setItem('mv_user', JSON.stringify(data.user));
}

export function clearSession() {
  localStorage.removeItem('mv_token');
  localStorage.removeItem('mv_user');
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (getToken()) headers.Authorization = `Bearer ${getToken()}`;
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${BASE}${path}`, { ...options, headers });
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = typeof data === 'object'
      ? data.detail || data.message
      : data;
    throw new Error(message || 'Something went wrong');
  }
  return data;
}
