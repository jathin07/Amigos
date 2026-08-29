import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../modules/auth/hooks/useAuth";
import { Compass, AlertTriangle } from "lucide-react";

/**
 * ProtectedRoute component guards access to routes.
 * It checks authentication state and optional permission claims before rendering page content.
 * 
 * Props:
 * - permission: string | string[] (optional: permission tag required to view route)
 * - requireAll: boolean (default false, if true, user needs all permissions in list)
 */
export function ProtectedRoute({ children, permission, requireAll = false }) {
  const { isAuthenticated, isLoading, hasPermission, hasAnyPermission, hasAllPermissions } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-4">
          <Compass className="animate-spin text-blue-600 mx-auto" size={40} />
          <p className="text-sm font-medium text-slate-600">Verifying access credentials...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page, preserving the page they tried to visit
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  if (permission) {
    const requiredPerms = Array.isArray(permission) ? permission : [permission];
    const hasAccess = requireAll
      ? hasAllPermissions(requiredPerms)
      : hasAnyPermission(requiredPerms);

    if (!hasAccess) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
          <div className="max-w-md w-full text-center space-y-6 bg-white p-8 rounded-xl shadow-md border border-slate-200">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 text-red-600 mb-2">
              <AlertTriangle size={32} />
            </div>
            <div className="space-y-2">
              <h1 className="text-xl font-bold text-slate-900">Access Denied</h1>
              <p className="text-sm text-slate-600">
                You do not possess the required permission privileges ({Array.isArray(permission) ? permission.join(", ") : permission}) to view this workspace.
              </p>
            </div>
            <div className="pt-2">
              <Navigate to="/admin/dashboard" replace />
              <a
                href="/admin/dashboard"
                className="inline-flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700"
              >
                Return to Dashboard
              </a>
            </div>
          </div>
        </div>
      );
    }
  }

  return children;
}
export default ProtectedRoute;
