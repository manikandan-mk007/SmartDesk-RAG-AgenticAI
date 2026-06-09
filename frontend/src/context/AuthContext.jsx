import { createContext, useContext, useEffect, useState } from "react";
import { getProfile, loginUser, registerUser } from "../api/authApi";

const AuthContext = createContext(null);

function getStoredUser() {
  try {
    const saved = localStorage.getItem("smartdesk_user");
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const storedUser = getStoredUser();
  const storedToken = localStorage.getItem("smartdesk_access_token");

  const [user, setUser] = useState(storedUser);
  const [loading, setLoading] = useState(Boolean(storedToken && !storedUser));

  const isAuthenticated = Boolean(user || localStorage.getItem("smartdesk_access_token"));

  const login = async (payload) => {
    const response = await loginUser(payload);

    localStorage.setItem("smartdesk_access_token", response.data.access);
    localStorage.setItem("smartdesk_refresh_token", response.data.refresh);
    localStorage.setItem("smartdesk_user", JSON.stringify(response.data.user));

    setUser(response.data.user);

    return response.data.user;
  };

  const register = async (payload) => {
    return registerUser(payload);
  };

  const logout = () => {
    localStorage.removeItem("smartdesk_access_token");
    localStorage.removeItem("smartdesk_refresh_token");
    localStorage.removeItem("smartdesk_user");
    setUser(null);
  };

  const refreshProfile = async () => {
    try {
      setLoading(true);
      const response = await getProfile();
      setUser(response.data.user);
      localStorage.setItem("smartdesk_user", JSON.stringify(response.data.user));
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("smartdesk_access_token");

    if (token && !user) {
      refreshProfile();
    } else {
      setLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshProfile,
        isAuthenticated,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}