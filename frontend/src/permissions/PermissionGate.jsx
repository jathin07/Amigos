import React from "react";
import { useAuth } from "../modules/auth/hooks/useAuth";
import { hasAllPermissionClaims, hasAnyPermissionClaims } from "./permissions";

/**
 * PermissionGate component guards UI elements by checking user permissions.
 * Wraps buttons, links, or sections to show them only if the user is authorized.
 * 
 * Props:
 * - permission: string | string[] (single permission key or array of permissions)
 * - requireAll: boolean (default false, if true user must have all permissions in array)
 * - fallback: React.ReactNode (rendered if permission check fails)
 */
export function PermissionGate({ permission, requireAll = false, fallback = null, children }) {
  const { permissions, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return fallback;
  }

  const requiredPerms = Array.isArray(permission) ? permission : [permission];

  const hasAccess = requireAll
    ? hasAllPermissionClaims(permissions, requiredPerms)
    : hasAnyPermissionClaims(permissions, requiredPerms);

  if (!hasAccess) {
    return fallback;
  }

  return <>{children}</>;
}
export default PermissionGate;
