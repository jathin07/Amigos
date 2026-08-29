import axios from "axios";
import { tokenStorage } from "../modules/auth/utils/tokenStorage";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/, "");

export const axiosClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach access token to headers
axiosClient.interceptors.request.use(
  (config) => {
    const token = tokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor structure is exported or attached via dynamic binding,
// but since we want it clean, let's write it in this file or a separate interceptors.js file.
// Let's create src/api/interceptors.js to define and bind the interceptors, keeping code clean.
