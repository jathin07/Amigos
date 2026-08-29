import React from "react";
import ResetPasswordForm from "../components/ResetPasswordForm";
import { Compass } from "lucide-react";

export function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        
        {/* Branding header */}
        <div className="text-center">
          <div className="flex justify-center text-blue-600 mb-2">
            <Compass size={48} className="stroke-[1.5]" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Reset Password
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Choose a secure new password for your account
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white py-8 px-6 sm:px-10 rounded-xl shadow-md border border-slate-200">
          <ResetPasswordForm />
        </div>

      </div>
    </div>
  );
}
export default ResetPasswordPage;
