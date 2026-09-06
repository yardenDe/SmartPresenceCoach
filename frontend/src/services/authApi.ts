import { api } from "./api";

export type AuthTokenResponse = {
  access_token: string;
  token_type: string;
};

export const loginRequest = (username: string, password: string) =>
  api.post<AuthTokenResponse>("/auth/login", { username, password });


export const registerRequest = (username: string, password: string) =>
  api.post<AuthTokenResponse>("/auth/register", { username, password });
