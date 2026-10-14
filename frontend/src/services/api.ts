import axios from "axios";

import type { TokenResponse, User } from "../types/auth";
import type { PolicyListResponse } from "../types/policy";

export interface HealthResponse {
  status: "ok" | "degraded";
  app: string;
  version: string;
  environment: string;
  database: "connected" | "unavailable";
  timestamp: string;
}

interface ApiErrorBody {
  error?: {
    code: number;
    message: string;
    details?: { field: string; message: string }[];
  };
}

export const TOKEN_KEY = "claimiq_token";
export const UNAUTHORIZED_EVENT = "claimiq:unauthorized";

// The token lives in localStorage for simplicity. It is readable by any script on the
// page (XSS risk); an httpOnly-cookie design is a possible hardening step for production.
export function getStoredToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function storeToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* storage unavailable: session will not persist */
  }
}

export function clearStoredToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url: string = error?.config?.url ?? "";
    const isAuthForm = url.startsWith("/auth/login") || url.startsWith("/auth/register");
    if (axios.isAxiosError(error) && error.response?.status === 401 && !isAuthForm) {
      clearStoredToken();
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
    }
    return Promise.reject(error);
  },
);

export function extractErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "Cannot reach the server. Is the backend running?";
    }
    const body = error.response.data as ApiErrorBody | undefined;
    const details = body?.error?.details;
    if (details && details.length > 0) {
      return details.map((d) => (d.field ? `${d.field}: ${d.message}` : d.message)).join(" ");
    }
    if (body?.error?.message) {
      return body.error.message;
    }
  }
  return fallback;
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("/health");
  return data;
}

export async function register(payload: {
  email: string;
  full_name: string;
  password: string;
}): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/register", payload);
  return data;
}

export async function login(payload: { email: string; password: string }): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", payload);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

export async function listPolicies(page = 1, pageSize = 20): Promise<PolicyListResponse> {
  const { data } = await api.get<PolicyListResponse>("/policies", {
    params: { page, page_size: pageSize },
  });
  return data;
}
