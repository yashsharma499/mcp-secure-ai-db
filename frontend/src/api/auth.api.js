import api from "./axios";
import { setTokens } from "../utils/token";

export const login = async ({ email, password }) => {
  const { data } = await api.post("/auth/login", {
    email: email.trim(),
    password
  });

 
  setTokens(data.access_token, data.refresh_token);

  return data;
};

export const signup = async ({ email, password }) => {
  const { data } = await api.post("/auth/signup", {
    email: email.trim(),
    password
  });

  return data;
};
