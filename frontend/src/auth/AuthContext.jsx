import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { login as loginApi } from "../api/auth.api";
import { getAccessToken, clearTokens } from "../utils/token";

const USER_KEY = "auth_user";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const bootstrap = useCallback(() => {
    const token = getAccessToken();

    if (!token) {
      setLoading(false);
      return;
    }

    const rawUser = localStorage.getItem(USER_KEY);

    if (rawUser) {
      try {
        setUser(JSON.parse(rawUser));
      } catch {
        clearTokens();
        localStorage.removeItem(USER_KEY);
      }
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = useCallback(async ({ email, password }) => {
    const data = await loginApi({ email, password });

    if (!data?.access_token || !data?.role || !data?.id) {
      throw new Error("Invalid login response");
    }

    const userObj = {
      id: data.id,
      email: data.email,
      role: data.role
    };

    
    localStorage.setItem(USER_KEY, JSON.stringify(userObj));
    setUser(userObj);

    return data;
  }, []);

  const logout = useCallback(() => {
  clearTokens();
  localStorage.removeItem(USER_KEY);
  setUser(null);
}, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      refreshUser: bootstrap
    }),
    [user, loading, login, logout, bootstrap]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
