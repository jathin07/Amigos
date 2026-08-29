import React from "react";
import { RotateCw, AlertCircle } from "lucide-react";

/**
 * Reusable Widget Card wrapper for dashboard widgets.
 * Handles individual refresh actions and standardized card styling.
 */
export function WidgetCard({
  title,
  description,
  onRefresh,
  isRefreshing = false,
  error = null,
  children,
}) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col h-full hover:shadow-md transition-shadow duration-200">
      
      {/* Widget Header */}
      <div className="flex justify-between items-start mb-4 border-b border-slate-50 pb-3">
        <div>
          <h3 className="text-base font-semibold text-slate-800">{title}</h3>
          {description && (
            <p className="text-xs text-slate-500 mt-0.5">{description}</p>
          )}
        </div>
        
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="text-slate-400 hover:text-slate-600 p-1.5 hover:bg-slate-50 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh widget data"
          >
            <RotateCw size={14} className={isRefreshing ? "animate-spin" : ""} />
          </button>
        )}
      </div>

      {/* Widget Content */}
      <div className="flex-1 flex flex-col min-h-[220px]">
        {error ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-4 space-y-3 bg-red-50/50 rounded-xl border border-red-100 my-auto">
            <AlertCircle className="text-red-500" size={24} />
            <div className="space-y-1">
              <p className="text-sm font-semibold text-red-700">Unable to load widget</p>
              <p className="text-xs text-red-500 max-w-[200px]">{error.message || "An error occurred."}</p>
            </div>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="px-3 py-1.5 text-xs font-semibold text-red-700 bg-white hover:bg-red-50 border border-red-200 rounded-lg shadow-sm transition-colors"
              >
                Retry
              </button>
            )}
          </div>
        ) : (
          children
        )}
      </div>

    </div>
  );
}
export default WidgetCard;
