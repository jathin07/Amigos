import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { authApi } from "../services/authApi";
import { Loader2, ArrowLeft, CheckCircle } from "lucide-react";
import { Link } from "react-router-dom";

const forgotPasswordSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email address"),
});

export function ForgotPasswordForm() {
  const [isSuccess, setIsSuccess] = useState(false);
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data) => {
    setServerError("");
    try {
      await authApi.forgotPassword(data.email);
      setIsSuccess(true);
    } catch (err) {
      console.error("Forgot password request failed:", err);
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        "Something went wrong. Please try again.";
      setServerError(errorMessage);
    }
  };

  if (isSuccess) {
    return (
      <div className="text-center space-y-4">
        <div className="flex justify-center text-emerald-500">
          <CheckCircle size={48} />
        </div>
        <h2 className="text-lg font-medium text-slate-900">Check your inbox</h2>
        <p className="text-sm text-slate-600 leading-relaxed">
          If an account exists for that email, we have sent a secure password reset link. Please check your inbox and spam folder.
        </p>
        <div className="pt-4">
          <Link
            to="/admin/login"
            className="inline-flex items-center text-sm font-semibold text-blue-600 hover:text-blue-700"
          >
            <ArrowLeft className="mr-2" size={16} />
            Back to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="text-center mb-4">
        <p className="text-sm text-slate-600">
          Enter your email address and we'll send you a link to reset your password.
        </p>
      </div>

      {serverError && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
          {serverError}
        </div>
      )}

      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          className={`block w-full px-3 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            errors.email ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
          }`}
          placeholder="admin@amigostourism.com"
          {...register("email")}
        />
        {errors.email && (
          <p className="mt-1 text-xs text-red-600 font-normal">{errors.email.message}</p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="animate-spin mr-2" size={16} />
            Sending Link...
          </>
        ) : (
          "Send Reset Link"
        )}
      </button>

      <div className="text-center pt-2">
        <Link
          to="/admin/login"
          className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-slate-800"
        >
          <ArrowLeft className="mr-1.5" size={14} />
          Back to Login
        </Link>
      </div>
    </form>
  );
}
export default ForgotPasswordForm;
