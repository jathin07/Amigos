import React, { createContext, useState, useEffect, useCallback } from "react";
import { authApi } from "../modules/auth/services/authApi";
import { tokenStorage } from "../modules/auth/utils/tokenStorage";
import { setupInterceptors } from "../api/interceptors";
import { hasPermissionClaim, hasAnyPermissionClaims, hasAllPermissionClaims } from "../permissions/permissions";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [role, setRole] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);

  // Define logout callback
  const logout = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch (err) {
        console.error("Logout request failed on server:", err);
      }
    }
    tokenStorage.clearAll();
    localStorage.removeItem("amigos_admin_token"); // Backward compatibility
    setUser(null);
    setPermissions([]);
    setRole("");
    setIsAuthenticated(false);
    setSessionExpired(false);
  }, []);

  // Session expired handler (triggered by axios 401 interceptor)
  const handleSessionExpired = useCallback(() => {
    tokenStorage.clearAll();
    localStorage.removeItem("amigos_admin_token"); // Backward compatibility
    setUser(null);
    setPermissions([]);
    setRole("");
    setIsAuthenticated(false);
    setSessionExpired(true);
  }, []);

  // Hydrate user profile from /auth/me
  const hydrateProfile = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await authApi.getCurrentUser();
      const userData = response.data; // Standard envelope wraps model in .data
      
      setUser(userData.user || userData);
      // Map permissions from the model (extract string codes from PermissionDTO array)
      const userPerms = (userData.permissions || []).map(p => typeof p === 'string' ? p : p.code);
      setPermissions(userPerms);
      setRole(userData.user?.role || userData.role || "");
      setIsAuthenticated(true);
      setSessionExpired(false);
    } catch (err) {
      console.error("Profile hydration failed:", err);
      tokenStorage.clearAll();
      localStorage.removeItem("amigos_admin_token"); // Backward compatibility
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initialize and register Axios interceptors on mount
  useEffect(() => {
    setupInterceptors(
      handleSessionExpired,
      (forbiddenError) => {
        console.warn("Permission denied interceptor triggered:", forbiddenError);
      },
      (serverError) => {
        console.error("Server error interceptor triggered:", serverError);
      }
    );

    const token = tokenStorage.getAccessToken();
    if (token) {
      hydrateProfile();
    } else {
      setIsLoading(false);
    }
  }, [handleSessionExpired, hydrateProfile]);

  // Login handler
  const login = useCallback(async (email, password, rememberMe) => {
    setIsLoading(true);
    try {
      const response = await authApi.login(email, password, rememberMe);
      const { access_token, refresh_token, session } = response.data;
      
      // Match python model dumps
      const token = access_token || session?.access_token;
      const refresh = refresh_token || session?.refresh_token;

      if (!token) {
        throw new Error("No access token returned from authentication server.");
      }

      tokenStorage.setAccessToken(token);
      localStorage.setItem("amigos_admin_token", token); // Backward compatibility
      if (refresh) {
        tokenStorage.setRefreshToken(refresh);
      }

      // Re-hydrate profile
      await hydrateProfile();
      return response.data;
    } catch (err) {
      setIsLoading(false);
      throw err;
    }
  }, [hydrateProfile]);

  // Permission checks helper
  const hasPermission = useCallback((permissionName) => {
    return hasPermissionClaim(permissions, permissionName);
  }, [permissions]);

  const hasAnyPermission = useCallback((requiredPermissions = []) => {
    return hasAnyPermissionClaims(permissions, requiredPermissions);
  }, [permissions]);

  const hasAllPermissions = useCallback((requiredPermissions = []) => {
    return hasAllPermissionClaims(permissions, requiredPermissions);
  }, [permissions]);

  const clearSessionExpired = useCallback(() => {
    setSessionExpired(false);
  }, []);

  const value = {
    user,
    permissions,
    role,
    isAuthenticated,
    isLoading,
    sessionExpired,
    clearSessionExpired,
    login,
    logout,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
