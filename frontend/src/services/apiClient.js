import axios from "axios";

/**
 * Shared Axios instance for all backend requests.
 * The base URL defaults to the relative "/api/v1" path, which the Vite dev
 * proxy (development) or nginx (container deployment) forwards to FastAPI.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

export default apiClient;
