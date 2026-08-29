import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import LoginForm from "../components/LoginForm";
import { Compass } from "lucide-react";

export function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/admin/dashboard");
    }
  }, [isAuthenticated, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-4">
          <Compass className="animate-spin text-blue-600 mx-auto" size={40} />
          <p className="text-sm font-medium text-slate-600">Verifying security credentials...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        
        {/* Branding header */}
        <div className="text-center">
          <div className="flex justify-center text-blue-600 mb-2">
            <Compass size={48} className="stroke-[1.5]" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Amigos Tourism ERP
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Enterprise Management Workspace
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white py-8 px-6 sm:px-10 rounded-xl shadow-md border border-slate-200">
          <LoginForm onSuccess={() => navigate("/admin/dashboard")} />
        </div>

      </div>
    </div>
  );
}
export default LoginPage;
