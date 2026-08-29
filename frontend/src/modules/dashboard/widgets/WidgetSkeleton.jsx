import React from "react";

export function WidgetSkeleton() {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col h-full min-h-[280px]">
      
      {/* Header Skeleton */}
      <div className="flex justify-between items-center mb-6 border-b border-slate-50 pb-3">
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-slate-100 rounded w-1/3 animate-pulse"></div>
          <div className="h-3 bg-slate-50 rounded w-1/4 animate-pulse"></div>
        </div>
        <div className="h-6 w-6 bg-slate-50 rounded-lg animate-pulse"></div>
      </div>

      {/* Body Skeleton */}
      <div className="flex-1 space-y-4 flex flex-col justify-center">
        <div className="h-3 bg-slate-100 rounded w-full animate-pulse"></div>
        <div className="h-3 bg-slate-100 rounded w-5/6 animate-pulse"></div>
        <div className="h-3 bg-slate-100 rounded w-4/5 animate-pulse"></div>
        <div className="h-3 bg-slate-100 rounded w-2/3 animate-pulse"></div>
      </div>

    </div>
  );
}
export default WidgetSkeleton;
