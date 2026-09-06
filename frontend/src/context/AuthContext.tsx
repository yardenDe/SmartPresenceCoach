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

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = Boolean(token);

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  const authenticate = async (
    request: typeof loginRequest,
    username: string,
    password: string,
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await request(username, password);
      const nextToken = response.data.access_token;

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

  const login = (username: string, password: string) =>
    authenticate(loginRequest, username, password);

  const register = (username: string, password: string) =>
    authenticate(registerRequest, username, password);

  const logout = () => {
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
