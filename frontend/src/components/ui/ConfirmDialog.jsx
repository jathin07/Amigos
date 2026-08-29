import React from "react";
import { AlertTriangle, Loader2, X } from "lucide-react";

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message = "Are you sure you want to proceed?",
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "danger", // 'danger' | 'warning' | 'info'
  isLoading = false,
}) {
  if (!isOpen) return null;

  const variantStyles = {
    danger: {
      bgIcon: "bg-red-100 text-red-600 border-red-200",
      btnConfirm: "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500",
    },
    warning: {
      bgIcon: "bg-amber-100 text-amber-600 border-amber-200",
      btnConfirm: "bg-amber-600 hover:bg-amber-700 text-white focus:ring-amber-500",
    },
    info: {
      bgIcon: "bg-blue-100 text-blue-600 border-blue-200",
      btnConfirm: "bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500",
    },
  };

  const style = variantStyles[variant] || variantStyles.danger;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200 select-none">
      <div
        className="fixed inset-0"
        onClick={!isLoading ? onClose : undefined}
      />
      
      <div className="relative w-full max-w-md bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden z-10 animate-in zoom-in-95 duration-150">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          disabled={isLoading}
          className="absolute top-3 right-3 p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 focus:outline-none transition-colors"
        >
          <X size={16} />
        </button>

        <div className="p-6 space-y-4">
          <div className="flex items-start space-x-4">
            <div className={`p-2.5 rounded-xl border shrink-0 ${style.bgIcon}`}>
              <AlertTriangle size={24} />
            </div>
            <div className="space-y-1 pr-4">
              <h3 className="text-base font-bold text-slate-900 leading-snug">
                {title}
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                {message}
              </p>
            </div>
          </div>

          <div className="flex items-center justify-end space-x-2.5 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg focus:outline-none transition-colors disabled:opacity-50"
            >
              {cancelLabel}
            </button>
            
            <button
              type="button"
              onClick={onConfirm}
              disabled={isLoading}
              className={`flex items-center space-x-1.5 px-4 py-2 text-xs font-bold rounded-lg shadow-sm focus:outline-none transition-colors disabled:opacity-50 ${style.btnConfirm}`}
            >
              {isLoading && <Loader2 size={14} className="animate-spin" />}
              <span>{confirmLabel}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

export default ConfirmDialog;
