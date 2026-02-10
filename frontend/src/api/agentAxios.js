import axios from "axios";
import { getAccessToken } from "../utils/token";

const agentApi = axios.create({
  baseURL: import.meta.env.VITE_AGENT_API_URL
});

agentApi.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default agentApi;
