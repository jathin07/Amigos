import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useAuth } from "../hooks/useAuth";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";

const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  remember_me: z.boolean().optional().default(false),
});

export function LoginForm({ onSuccess }) {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      remember_me: false,
    },
  });

  const onSubmit = async (data) => {
    setServerError("");
    try {
      await login(data.email, data.password, data.remember_me);
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error("Login failed:", err);
      // Handle standard Flask error responses
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        "Invalid email or password.";
      setServerError(errorMessage);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {serverError && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg animate-pulse">
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

      {/* Password Field */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <label htmlFor="password" className="block text-sm font-medium text-slate-700">
            Password
          </label>
          <Link
            to="/admin/forgot-password"
            className="text-xs font-medium text-blue-600 hover:text-blue-700"
          >
            Forgot Password?
          </Link>
        </div>
        <div className="relative">
          <input
            id="password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            className={`block w-full pl-3 pr-10 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.password ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
            }`}
            placeholder="••••••••"
            {...register("password")}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>
        {errors.password && (
          <p className="mt-1 text-xs text-red-600 font-normal">{errors.password.message}</p>
        )}
      </div>

      {/* Remember Me Checkbox */}
      <div className="flex items-center">
        <input
          id="remember_me"
          type="checkbox"
          className="h-4 w-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
          {...register("remember_me")}
        />
        <label htmlFor="remember_me" className="ml-2 block text-sm text-slate-700">
          Remember me for 30 days
        </label>
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
            Authenticating...
          </>
        ) : (
          "Sign In"
        )}
      </button>
    </form>
  );
}
export default LoginForm;
