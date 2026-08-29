import React from "react";
import { Calendar, Users, DollarSign, FileText, User, Building, MapPin, Tag } from "lucide-react";

export function BookingOverviewTab({ booking, onEditClick }) {
  const snapshots = booking?.snapshots || {};
  const tripCoordinator = booking?.trip_coordinator || null;
  const audit = booking?.audit || {};

  return (
    <div className="space-y-6">
      
      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Total Confirmed Amount */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Confirmed Total Price</span>
            <span className="text-2xl font-extrabold text-slate-800 font-mono block mt-1">
              INR {Number(booking?.total_amount || 0).toLocaleString("en-IN")}
            </span>
          </div>
          <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-semibold pt-2 border-t border-slate-50">
            <Tag size={12} className="text-slate-400" />
            <span>Proposal Ref: </span>
            <span className="text-slate-600 font-bold font-mono">{booking?.proposal_version_id?.slice(0, 8).toUpperCase() || "Custom"}</span>
          </div>
        </div>

        {/* Schedule */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Travel Schedule</span>
            <span className="text-sm font-bold text-slate-800 flex items-center mt-2.5">
              <Calendar size={16} className="mr-2 text-blue-600" />
              {booking?.trip_start_date 
                ? `${new Date(booking.trip_start_date).toLocaleDateString("en-IN")} - ${booking.trip_end_date ? new Date(booking.trip_end_date).toLocaleDateString("en-IN") : "TBD"}` 
                : "Flexible Dates"}
            </span>
          </div>
          <div className="flex items-center space-x-1 text-[10px] text-slate-400 font-semibold pt-2 border-t border-slate-50">
            <span>Booking Date:</span>
            <span className="text-slate-600 font-bold">
              {booking?.booking_date ? new Date(booking.booking_date).toLocaleDateString("en-IN") : "—"}
            </span>
          </div>
        </div>

        {/* Travelers count */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Passenger Count</span>
            <span className="text-sm font-bold text-slate-800 flex items-center mt-2.5">
              <Users size={16} className="mr-2 text-emerald-600" />
              {booking?.total_travelers || booking?.travelers?.length || 0} Travelers
            </span>
          </div>
          <div className="flex items-center space-x-1 text-[10px] text-slate-400 font-semibold pt-2 border-t border-slate-50">
            <span>Group Lead Assigned:</span>
            <span className="text-slate-600 font-bold">
              {booking?.travelers?.find(t => t.is_group_leader)?.name || "None"}
            </span>
          </div>
        </div>

      </div>

      {/* Main details list & side notes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Detail specifications */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Booking Specifications</h3>
            <button
              onClick={onEditClick}
              className="px-2.5 py-1 border border-slate-200 hover:bg-slate-50 rounded-lg text-[10px] font-bold text-slate-600 shadow-xs transition-colors"
            >
              Edit Details
            </button>
          </div>

          <div className="p-5 divide-y divide-slate-100 text-xs font-semibold text-slate-700 space-y-3.5">
            
            <div className="flex justify-between items-center py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <FileText size={14} className="mr-1.5" /> File / Group Name
              </span>
              <span className="text-slate-800 font-bold">{booking?.group_name || "Individual Booking"}</span>
            </div>

            <div className="flex justify-between items-center pt-3.5 py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <User size={14} className="mr-1.5" /> Primary Customer
              </span>
              <span className="text-slate-800 font-bold">{snapshots.contact_person_name || "—"}</span>
            </div>

            <div className="flex justify-between items-center pt-3.5 py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <Building size={14} className="mr-1.5" /> Organization Unit
              </span>
              <span className="text-slate-800 font-bold">{snapshots.organization_name || "Individual"}</span>
            </div>

            <div className="flex justify-between items-center pt-3.5 py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <MapPin size={14} className="mr-1.5" /> Trip Title Snapshot
              </span>
              <span className="text-slate-800 font-bold">{snapshots.trip_name || "—"}</span>
            </div>

            <div className="flex justify-between items-center pt-3.5 py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <MapPin size={14} className="mr-1.5" /> Package Category
              </span>
              <span className="text-slate-800 font-bold">{snapshots.package_name || "—"}</span>
            </div>

            <div className="flex justify-between items-center pt-3.5 py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <User size={14} className="mr-1.5" /> Trip Coordinator
              </span>
              <span className="text-slate-800 font-bold">{tripCoordinator?.display_name || "Unassigned"}</span>
            </div>

            <div className="flex justify-between items-center pt-3.5 py-1">
              <span className="text-slate-400 font-bold flex items-center">
                <Tag size={14} className="mr-1.5" /> Entry Mode
              </span>
              <span className="text-slate-600 font-bold font-mono uppercase bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded text-[10px]">
                {booking?.entry_mode || "NORMAL"}
              </span>
            </div>

          </div>
        </div>

        {/* Side Panel Notes */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Internal Operations Notes
            </h4>
            {onEditClick && (
              <button
                onClick={onEditClick}
                className="text-[11px] font-bold text-blue-600 hover:text-blue-800 hover:underline flex items-center space-x-1"
              >
                <span>Edit Notes & Coordinator</span>
              </button>
            )}
          </div>
          {booking?.internal_notes ? (
            <p className="text-xs text-slate-600 font-semibold leading-relaxed whitespace-pre-line bg-slate-50 border border-slate-100 rounded-xl p-3.5">
              {booking.internal_notes}
            </p>
          ) : (
            <div className="text-center py-6 text-slate-400 text-xs font-medium italic">
              No internal coordination notes registered. Click "Edit Details" above to add operational instructions.
            </div>
          )}
        </div>

      </div>

    </div>
  );
}

export default BookingOverviewTab;
