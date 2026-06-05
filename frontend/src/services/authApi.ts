import { api } from "./api";


export const loginRequest = (username: string, password: string) =>
  api.post("/auth/login", { username, password });


export const registerRequest = (username: string, password: string) =>
  api.post("/auth/register", { username, password });
