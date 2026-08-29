import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { authApi } from "../services/authApi";
import { Loader2, X, Eye, EyeOff } from "lucide-react";

const changePasswordSchema = z
  .object({
    current_password: z.string().min(8, "Current password must be at least 8 characters"),
    new_password: z.string().min(8, "New password must be at least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your new password"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "New passwords do not match",
    path: ["confirm_password"],
  });

export function ChangePasswordModal({ isOpen, onClose }) {
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [serverError, setServerError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  if (!isOpen) return null;

  const onSubmit = async (data) => {
    setServerError("");
    setSuccessMessage("");
    try {
      await authApi.changePassword(
        data.current_password,
        data.new_password,
        data.confirm_password
      );
      setSuccessMessage("Password updated successfully.");
      reset();
      setTimeout(() => {
        setSuccessMessage("");
        onClose();
      }, 1500);
    } catch (err) {
      console.error("Password update failed:", err);
      const errorMessage =
        err.response?.data?.error?.message ||
        err.message ||
        "Failed to update password. Please check your current password.";
      setServerError(errorMessage);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md border border-slate-200 overflow-hidden animate-opacity duration-200">
        
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-800">Change Password</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 rounded-lg p-1 hover:bg-slate-50 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
          {serverError && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
              {serverError}
            </div>
          )}

          {successMessage && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm rounded-lg">
              {successMessage}
            </div>
          )}

          {/* Current Password */}
          <div>
            <label htmlFor="current_password" className="block text-sm font-medium text-slate-700 mb-1">
              Current Password
            </label>
            <div className="relative">
              <input
                id="current_password"
                type={showCurrent ? "text" : "password"}
                className={`block w-full pl-3 pr-10 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.current_password ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
                }`}
                placeholder="Enter current password"
                {...register("current_password")}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                onClick={() => setShowCurrent(!showCurrent)}
              >
                {showCurrent ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.current_password && (
              <p className="mt-1 text-xs text-red-600 font-normal">{errors.current_password.message}</p>
            )}
          </div>

          {/* New Password */}
          <div>
            <label htmlFor="new_password" className="block text-sm font-medium text-slate-700 mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                id="new_password"
                type={showNew ? "text" : "password"}
                className={`block w-full pl-3 pr-10 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.new_password ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
                }`}
                placeholder="Min 8 characters"
                {...register("new_password")}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                onClick={() => setShowNew(!showNew)}
              >
                {showNew ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.new_password && (
              <p className="mt-1 text-xs text-red-600 font-normal">{errors.new_password.message}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-slate-700 mb-1">
              Confirm New Password
            </label>
            <div className="relative">
              <input
                id="confirm_password"
                type={showConfirm ? "text" : "password"}
                className={`block w-full pl-3 pr-10 py-2 border rounded-lg text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.confirm_password ? "border-red-300 focus:ring-red-500 focus:border-red-500" : "border-slate-300"
                }`}
                placeholder="Repeat new password"
                {...register("confirm_password")}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                onClick={() => setShowConfirm(!showConfirm)}
              >
                {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.confirm_password && (
              <p className="mt-1 text-xs text-red-600 font-normal">{errors.confirm_password.message}</p>
            )}
          </div>

          {/* Footer Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 border border-slate-300 rounded-lg focus:outline-none transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex justify-center items-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={16} />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
export default ChangePasswordModal;
