import { axiosClient } from "./axiosClient";
import { tokenStorage } from "../modules/auth/utils/tokenStorage";

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Configure response interceptors on the Axios client.
 * Accepts callbacks for handling session expiration (logout) and showing error toasts.
 */
export function setupInterceptors(onSessionExpired, onPermissionDenied, onServerError) {
  axiosClient.interceptors.response.use(
    (response) => {
      // Standardize response to return the envelope data directly if needed,
      // or return the Axios response object. Let's return the full response object,
      // so components can check response.data.success etc.
      return response;
    },
    async (error) => {
      const originalRequest = error.config;

      // Handle network errors or server downtime
      if (!error.response) {
        if (onServerError) {
          onServerError({
            code: "ERR_NETWORK",
            message: "Network error. Please check your connection.",
          });
        }
        return Promise.reject(error);
      }

      const { status, data } = error.response;

      // Handle 401 Unauthorized (Expired Token)
      if (status === 401 && !originalRequest._retry) {
        // Skip token refresh for login/refresh routes to prevent infinite loops
        if (originalRequest.url.includes("/auth/login") || originalRequest.url.includes("/auth/refresh")) {
          return Promise.reject(error);
        }

        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return axiosClient(originalRequest);
            })
            .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        const refreshToken = tokenStorage.getRefreshToken();
        if (!refreshToken) {
          isRefreshing = false;
          if (onSessionExpired) onSessionExpired();
          return Promise.reject(error);
        }

        try {
          // Note: call auth/refresh with raw axios to bypass interceptor if needed,
          // but axiosClient is fine as we handle URL check above.
          const res = await axiosClient.post("/auth/refresh", {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = res.data.data;
          
          tokenStorage.setAccessToken(access_token);
          if (newRefreshToken) {
            tokenStorage.setRefreshToken(newRefreshToken);
          }

          processQueue(null, access_token);
          isRefreshing = false;

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return axiosClient(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          isRefreshing = false;
          tokenStorage.clearAll();
          if (onSessionExpired) onSessionExpired();
          return Promise.reject(refreshError);
        }
      }

      // Handle 403 Forbidden (Missing permissions)
      if (status === 403) {
        if (onPermissionDenied) {
          onPermissionDenied(data?.error || {
            code: "ERR_FORBIDDEN",
            message: "Access Denied: You do not have permission for this action.",
          });
        }
      }

      // Handle 500 Server Error
      if (status === 500) {
        if (onServerError) {
          onServerError(data?.error || {
            code: "ERR_SERVER",
            message: "An internal server error occurred. Please try again later.",
          });
        }
      }

      return Promise.reject(error);
    }
  );
}
