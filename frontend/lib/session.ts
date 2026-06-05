const SESSION_KEY = "handbookiq_session_id";

export function createSessionId(): string {
  return crypto.randomUUID();
}

export function getStoredSessionId(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(SESSION_KEY);
}

export function storeSessionId(id: string): void {
  sessionStorage.setItem(SESSION_KEY, id);
}

export function clearStoredSessionId(): void {
  sessionStorage.removeItem(SESSION_KEY);
}

export function getOrCreateSessionId(): string {
  return getStoredSessionId() ?? createSessionId();
}
