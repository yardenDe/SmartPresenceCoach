import {
  createContext,
  useEffect,
  useContext,
  useState,
  type ReactNode,
} from "react";

import { loginRequest, registerRequest } from "../services/authApi";
import { getApiErrorMessage, setAuthToken } from "../services/api";


type AuthContextValue = {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const TOKEN_STORAGE_KEY = "smart-presence-token";

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = Boolean(token);

  useEffect(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }, []);

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  const getTokenFromResponse = (data: unknown) => {
    if (typeof data === "string") {
      return data;
    }

    if (Array.isArray(data) && typeof data[1] === "string") {
      return data[1];
    }

    if (typeof data === "object" && data !== null) {
      const response = data as { access_token?: unknown };

      if (typeof response.access_token === "string") {
        return response.access_token;
      }

      if (Array.isArray(response.access_token) && typeof response.access_token[1] === "string") {
        return response.access_token[1];
      }
    }

    return null;
  };

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await loginRequest(username, password);
      const nextToken = getTokenFromResponse(response.data);

      if (!nextToken) {
        throw new Error("Login succeeded but no access token was returned.");
      }

      setToken(nextToken);
      setUsername(username);
    } catch (requestError) {
      const message = getApiErrorMessage(requestError);
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await registerRequest(username, password);
      const nextToken = getTokenFromResponse(response.data);

      if (nextToken) {
        setToken(nextToken);
        setUsername(username);
        return;
      }

      await login(username, password);
    } catch (requestError) {
      const message = getApiErrorMessage(requestError);
      setError(message);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUsername(null);
    setError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        username,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
};
