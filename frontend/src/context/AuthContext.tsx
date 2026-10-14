import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  UNAUTHORIZED_EVENT,
  clearStoredToken,
  getMe,
  getStoredToken,
  login as apiLogin,
  register as apiRegister,
  storeToken,
} from "../services/api";
import type { User } from "../types/auth";

export interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(() => getStoredToken() !== null);

  // Restore the session from a stored token.
  useEffect(() => {
    if (getStoredToken() === null) {
      return;
    }
    let cancelled = false;
    getMe()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => clearStoredToken())
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // The API layer fires this event when any request comes back 401.
  useEffect(() => {
    const handler = () => setUser(null);
    window.addEventListener(UNAUTHORIZED_EVENT, handler);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, handler);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await apiLogin({ email, password });
    storeToken(result.access_token);
    setUser(result.user);
  }, []);

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    const result = await apiRegister({ full_name: fullName, email, password });
    storeToken(result.access_token);
    setUser(result.user);
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
