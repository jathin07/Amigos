const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/, "");

export const getApiBaseUrl = () => API_BASE_URL;

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.error ||
      payload?.message ||
      `Request failed (${response.status})`;

    throw new Error(message);
  }

  return payload;
}