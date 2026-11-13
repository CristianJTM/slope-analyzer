export const BASE_URL = "http://127.0.0.1:8000/api/v1";

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Error ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}
