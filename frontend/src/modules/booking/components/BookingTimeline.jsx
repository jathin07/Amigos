import React from "react";
import { useBookingTimeline } from "../hooks/useBooking";
import { Clock, User, ArrowRight, Activity, Loader2 } from "lucide-react";

export function BookingTimeline({ bookingId }) {
  const { data: response, isLoading } = useBookingTimeline(bookingId);
  const events = response?.data?.timeline_events || [];

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-10 space-y-2">
        <Loader2 className="animate-spin text-blue-600" size={20} />
        <p className="text-xs text-slate-500 font-semibold">Retrieving status timeline...</p>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
        <Activity className="mx-auto text-slate-400 mb-2" size={24} />
        <p className="text-xs font-semibold text-slate-800">No status updates logged yet</p>
        <p className="text-[10px] text-slate-400 mt-0.5">Booking status adjustments will populate audit logs here.</p>
      </div>
    );
  }

  return (
    <div className="relative pl-6 border-l border-slate-200 space-y-6 pt-2 select-none">
      {events.map((evt) => (
        <div key={evt.id} className="relative">
          
          {/* Timeline Node */}
          <div className="absolute -left-[35px] top-0 w-7 h-7 rounded-full border border-slate-200 bg-white flex items-center justify-center text-slate-500 shadow-xs">
            <Clock size={12} />
          </div>

          {/* Card */}
          <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-sm space-y-2">
            <div className="flex items-center justify-between flex-wrap gap-2">
              
              {/* Transition badges */}
              <div className="flex items-center space-x-1.5 text-xs font-bold">
                {evt.from_status ? (
                  <>
                    <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200 font-mono text-[10px]">
                      {evt.from_status.name}
                    </span>
                    <ArrowRight size={12} className="text-slate-400" />
                  </>
                ) : (
                  <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-100 text-[10px]">
                    INITIAL
                  </span>
                )}
                <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-100 font-mono text-[10px]">
                  {evt.to_status?.name || "Unknown"}
                </span>
              </div>

              {/* Timestamp */}
              <span className="text-[10px] text-slate-400 font-semibold">
                {evt.changed_at ? new Date(evt.changed_at).toLocaleString("en-IN") : ""}
              </span>
            </div>

            {/* Note contents */}
            {evt.notes && (
              <p className="text-xs text-slate-600 leading-relaxed font-semibold">
                {evt.notes}
              </p>
            )}

            {/* Author */}
            {evt.changed_by && (
              <div className="flex items-center space-x-1 text-[10px] text-slate-400 font-semibold pt-1 border-t border-slate-50">
                <User size={10} />
                <span>Changed by:</span>
                <span className="text-slate-600 font-bold">{evt.changed_by.display_name}</span>
              </div>
            )}

          </div>

        </div>
      ))}
    </div>
  );
}

export default BookingTimeline;
