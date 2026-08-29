import React from "react";
import { useBookingPipeline } from "../hooks/useDashboard";
import WidgetCard from "../widgets/WidgetCard";

export function BookingPipeline() {
  const { data, isLoading, error, refetch } = useBookingPipeline();

  const bookingStats = data?.data || [];

  return (
    <WidgetCard
      title="Booking Pipeline"
      description="Active booking distribution across statuses"
      onRefresh={refetch}
      isRefreshing={isLoading}
      error={error}
    >
      <div className="flex-1 flex flex-col justify-between py-2 space-y-4">
        {bookingStats.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-xs">No active bookings data.</div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {bookingStats.map((item, idx) => {
              return (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 border border-slate-100 rounded-xl space-y-1.5 hover:bg-slate-100/50 transition-colors"
                >
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    {item.status.replace("_", " ")}
                  </span>
                  <div className="flex justify-between items-baseline">
                    <span className="text-lg font-bold text-slate-800">{item.count}</span>
                    <span className="text-xs font-semibold text-slate-500">
                      {item.percentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="border-t border-slate-50 pt-3 text-center">
          <span className="text-xs text-slate-400 font-normal">
            Total active bookings tracked:{" "}
            <span className="font-semibold text-slate-700">
              {bookingStats.reduce((acc, curr) => acc + curr.count, 0)}
            </span>
          </span>
        </div>
      </div>
    </WidgetCard>
  );
}
export default BookingPipeline;
