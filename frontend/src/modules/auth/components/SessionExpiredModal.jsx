import React from "react";
import { useAuth } from "../hooks/useAuth";
import { AlertCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function SessionExpiredModal() {
  const { sessionExpired, clearSessionExpired } = useAuth();
  const navigate = useNavigate();

  if (!sessionExpired) return null;

  const handleRedirect = () => {
    clearSessionExpired();
    navigate("/admin/login");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-sm border border-slate-200 p-6 space-y-4 text-center animate-bounce-in duration-200">
        
        <div className="flex justify-center text-amber-500">
          <AlertCircle size={40} />
        </div>

        <h3 className="text-lg font-semibold text-slate-900">Session Expired</h3>
        
        <p className="text-sm text-slate-600">
          Your active session has expired due to security timeout. Please log in again to continue working in the ERP workspace.
        </p>

        <button
          onClick={handleRedirect}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-150"
        >
          Return to Login
        </button>

      </div>
    </div>
  );
}
export default SessionExpiredModal;
