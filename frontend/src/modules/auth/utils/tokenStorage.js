const ACCESS_TOKEN_KEY = "amigos_access_token";
const REFRESH_TOKEN_KEY = "amigos_refresh_token";

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  setAccessToken: (token) => localStorage.setItem(ACCESS_TOKEN_KEY, token),
  clearAccessToken: () => localStorage.removeItem(ACCESS_TOKEN_KEY),

  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setRefreshToken: (token) => localStorage.setItem(REFRESH_TOKEN_KEY, token),
  clearRefreshToken: () => localStorage.removeItem(REFRESH_TOKEN_KEY),

  clearAll: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
};
