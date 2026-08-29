import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { authApi } from "../services/authApi";
import { Loader2, CheckCircle, Eye, EyeOff } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";

const resetPasswordSchema = z
  .object({
    new_password: z.string().min(8, "Password must be at least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your password"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export function ResetPasswordForm() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [isSuccess, setIsSuccess] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      new_password: "",
      confirm_password: "",
    },
  });

  const onSubmit = async (data) => {
    setServerError("");
    if (!token) {
      setServerError("Reset token is missing from the URL. Please request a new link.");
      return;
    }
    try {
      await authApi.resetPassword(token, data.new_password, data.confirm_password);
      setIsSuccess(true);
    } catch (err) {
      console.error("Password reset failed:", err);
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        "Failed to reset password. The link may have expired.";
      setServerError(errorMessage);
    }
  };

  if (isSuccess) {
    return (
      <div className="text-center space-y-4">
        <div className="flex justify-center text-emerald-500">
          <CheckCircle size={48} />
        </div>
        <h2 className="text-lg font-medium text-slate-900">Password Reset Complete</h2>
        <p className="text-sm text-slate-600">
          Your password has been successfully updated. You can now log in with your new credentials.
        </p>
        <div className="pt-4">
          <Link
            to="/admin/login"
            className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-150"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {serverError && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
          {serverError}
        </div>
      )}

      {/* New Password Field */}
      <div>
        <label htmlFor="new_password" className="block text-sm font-medium text-slate-700 mb-1">
          New Password
        </label>
        <div className="relative">
          <input
            id="new_password"
            type={showNewPassword ? "text" : "password"}
            className={`block w-full pl-3 pr-10 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.new_password ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
            }`}
            placeholder="Min 8 characters"
            {...register("new_password")}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
            onClick={() => setShowNewPassword(!showNewPassword)}
          >
            {showNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
        {errors.new_password && (
          <p className="mt-1 text-xs text-red-600 font-normal">{errors.new_password.message}</p>
        )}
      </div>

      {/* Confirm Password Field */}
      <div>
        <label htmlFor="confirm_password" className="block text-sm font-medium text-slate-700 mb-1">
          Confirm Password
        </label>
        <div className="relative">
          <input
            id="confirm_password"
            type={showConfirmPassword ? "text" : "password"}
            className={`block w-full pl-3 pr-10 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.confirm_password ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
            }`}
            placeholder="Repeat new password"
            {...register("confirm_password")}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
          >
            {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
        {errors.confirm_password && (
          <p className="mt-1 text-xs text-red-600 font-normal">{errors.confirm_password.message}</p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting || !token}
        className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="animate-spin mr-2" size={16} />
            Resetting Password...
          </>
        ) : (
          "Reset Password"
        )}
      </button>
    </form>
  );
}
export default ResetPasswordForm;
