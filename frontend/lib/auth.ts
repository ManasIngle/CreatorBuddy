/**
 * Auth utilities for token storage and state.
 * Token lives in both Zustand (reactive) and localStorage (persistent).
 * No cookies — JWT in Authorization header only.
 */

const TOKEN_KEY = "access_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Decode a JWT payload without verification (verification happens server-side).
 * Used only for reading `exp` to proactively redirect before the API rejects.
 */
export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = parts[1];
    // atob doesn't handle URL-safe base64 — pad and replace chars
    const padded = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(padded);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

/**
 * Returns true if token is expired or will expire within `bufferSeconds`.
 * Default buffer is 60s — redirect to login before the API rejects.
 */
export function isTokenExpired(token: string, bufferSeconds = 60): boolean {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") return true;
  const nowSecs = Math.floor(Date.now() / 1000);
  return payload.exp < nowSecs + bufferSeconds;
}
