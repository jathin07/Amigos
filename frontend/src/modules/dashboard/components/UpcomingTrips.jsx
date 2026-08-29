import React, { useState } from "react";
import { useUpcomingTrips } from "../hooks/useDashboard";
import WidgetCard from "../widgets/WidgetCard";
import { Compass, Calendar, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export function UpcomingTrips() {
  const [page, setPage] = useState(1);
  const { data, isLoading, error, refetch } = useUpcomingTrips(page, 4);

  const tripsData = data?.data || {};
  const trips = tripsData.upcoming_trips || [];
  const pagination = tripsData.pagination || {};

  return (
    <WidgetCard
      title="Upcoming Trip Executions"
      description="List of departures scheduled for execution in the next 7 days"
      onRefresh={refetch}
      isRefreshing={isLoading}
      error={error}
    >
      <div className="flex-1 flex flex-col justify-between py-1 space-y-4">
        {trips.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
            <Compass size={28} className="stroke-[1.5] text-slate-300" />
            <span>No upcoming departures scheduled for this week.</span>
          </div>
        ) : (
          <div className="space-y-3">
            {trips.map((trip, idx) => {
              return (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 border border-slate-100 rounded-xl hover:bg-slate-50/50 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">
                        {trip.booking_number}
                      </span>
                      <span className="text-xs text-slate-400">•</span>
                      <span className="text-xs font-semibold text-slate-800">{trip.customer}</span>
                    </div>
                    <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                      <Compass size={12} />
                      <span className="font-medium text-slate-500">{trip.destination}</span>
                      <span>•</span>
                      <span className="italic text-slate-500">Coord: {trip.coordinator || "Unassigned"}</span>
                    </div>
                  </div>

                  <div className="text-right space-y-1">
                    <div className="flex items-center justify-end text-xs font-bold text-indigo-600 space-x-1">
                      <Calendar size={12} />
                      <span>{trip.departure}</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-normal block">
                      Departs in {trip.remaining_days} days
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Small inline pagination controls */}
        {pagination.total_pages > 1 && (
          <div className="border-t border-slate-50 pt-3 flex justify-between items-center text-xs text-slate-400">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="text-slate-500 hover:text-slate-700 disabled:opacity-30"
            >
              Previous
            </button>
            <span>
              Page {page} of {pagination.total_pages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(pagination.total_pages, p + 1))}
              disabled={page === pagination.total_pages}
              className="text-slate-500 hover:text-slate-700 disabled:opacity-30"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </WidgetCard>
  );
}
export default UpcomingTrips;
