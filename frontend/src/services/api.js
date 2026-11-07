const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

export function getToken() {
  // Browser authentication is handled by an HttpOnly cookie, never JavaScript storage.
  return null;
}

export function setSession() {
  // Authentication tokens and personal profile details stay out of browser storage.
  localStorage.removeItem('mv_token');
  localStorage.removeItem('mv_user');
}

export function clearSession() {
  localStorage.removeItem('mv_token');
  localStorage.removeItem('mv_user');
}

export function downloadAttachment(recordId) {
  const url = `${BASE}/api/diagnosis/${encodeURIComponent(recordId)}/attachment`;
  window.open(url, '_blank', 'noopener,noreferrer');
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(`${BASE}${path}`, {
    ...options, headers, credentials: 'include',
  });
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    const message = typeof data === 'object' ? data.detail || data.message : data;
    throw new Error(message || 'Something went wrong');
  }
  return data;
}
