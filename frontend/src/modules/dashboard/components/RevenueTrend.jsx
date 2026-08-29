import React from "react";
import { useRevenueTrend } from "../hooks/useDashboard";
import WidgetCard from "../widgets/WidgetCard";

const formatCurrency = (val) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(val || 0);
};

export function RevenueTrend() {
  const { data, isLoading, error, refetch } = useRevenueTrend();

  if (!isLoading && !data && !error) {
    return null; // Omit if user lacks finance.read
  }

  const months = data?.data?.trend_months || [];
  const maxCollected = months.length > 0 ? Math.max(...months.map((m) => m.collected || 1)) : 1;

  return (
    <WidgetCard
      title="Monthly Sales & Billing Trend"
      description="Collected revenue and bookings volume overview"
      onRefresh={refetch}
      isRefreshing={isLoading}
      error={error}
    >
      <div className="flex-1 flex flex-col justify-between py-1 space-y-4">
        {months.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-xs">No trend logs found.</div>
        ) : (
          <div className="space-y-6">
            {/* Visual Histogram */}
            <div className="flex items-end justify-between h-36 pt-4 px-2 border-b border-slate-100">
              {months.map((item, idx) => {
                const heightPercentage = Math.max(10, ((item.collected || 0) / maxCollected) * 100);
                return (
                  <div key={idx} className="flex flex-col items-center flex-1 group relative">
                    {/* Hover Info Tooltip */}
                    <div className="absolute bottom-full mb-2 bg-slate-900 text-white text-[10px] rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none z-30 whitespace-nowrap shadow-md">
                      <div>Revenue: {formatCurrency(item.collected)}</div>
                      <div>Profit: {formatCurrency(item.profit)}</div>
                      <div>Bookings: {item.bookings_count} trips</div>
                    </div>

                    {/* Bar Pillar */}
                    <div className="w-full max-w-[20px] bg-slate-50 hover:bg-slate-100 rounded-t-md flex items-end h-full">
                      <div
                        className="w-full bg-gradient-to-t from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 rounded-t-md transition-all duration-300"
                        style={{ height: `${heightPercentage}%` }}
                      ></div>
                    </div>

                    {/* Month Label */}
                    <span className="text-[10px] font-bold text-slate-400 mt-2 uppercase tracking-wide">
                      {item.month}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Legend info */}
            <div className="flex justify-between items-center text-xs text-slate-400 px-1">
              <span className="flex items-center">
                <span className="w-2.5 h-2.5 rounded bg-blue-500 mr-1.5"></span>
                Collected Billing
              </span>
              <span>
                Period: <span className="font-semibold text-slate-700">{data?.data?.period || "6M"}</span>
              </span>
            </div>
          </div>
        )}
      </div>
    </WidgetCard>
  );
}
export default RevenueTrend;
