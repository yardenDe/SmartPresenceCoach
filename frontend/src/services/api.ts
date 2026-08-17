import axios from "axios";

type BackendErrorResponse = {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
  };
  detail?: string | Array<{ msg?: string }>;
};

const resolveApiBaseUrl = () => {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

  if (
    window.location.hostname === "127.0.0.1" &&
    configuredUrl.includes("localhost")
  ) {
    return configuredUrl.replace("localhost", "127.0.0.1");
  }

  return configuredUrl;
};

export const api = axios.create({
  baseURL: resolveApiBaseUrl(),
  timeout: 15000,
});

export const getApiErrorMessage = (error: unknown) => {
  if (!axios.isAxiosError(error)) {
    return "Something went wrong. Please try again.";
  }

  const data = error.response?.data as BackendErrorResponse | undefined;

  if (data?.error?.code === "LLM_UNAVAILABLE") {
    const llmError = data.error.details?.llm_error;
    if (typeof llmError === "string" && llmError.trim()) {
      return llmError;
    }
  }

  if (error.code === "ECONNABORTED") {
    return "The server did not respond in time. Please check that the backend is running.";
  }

  if (data?.error?.message) {
    return data.error.message;
  }

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
    return data.detail[0].msg ?? "Request validation failed.";
  }

  if (error.message) {
    return error.message;
  }

  return "Something went wrong. Please try again.";
};

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }

  delete api.defaults.headers.common.Authorization;
};
