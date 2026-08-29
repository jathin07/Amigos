import React, { useState, useEffect } from "react";
import { X, Loader2, Edit3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { axiosClient } from "../../../api/axiosClient";

export function EditBookingDrawer({ isOpen, onClose, onSubmit, isPending, booking = null }) {
  const [formData, setFormData] = useState({
    group_name: "",
    internal_notes: "",
    trip_coordinator_team_member_id: "",
    trip_start_date: "",
    trip_end_date: "",
    total_amount: "",
  });

  const { data: teamResponse } = useQuery({
    queryKey: ["team-members-lookup"],
    queryFn: async () => {
      const res = await axiosClient.get("/team-members", { params: { page_size: 100 } });
      return res.data?.data?.items || [];
    },
    enabled: isOpen,
  });

  useEffect(() => {
    if (booking) {
      setFormData({
        group_name: booking.group_name || "",
        internal_notes: booking.internal_notes || "",
        trip_coordinator_team_member_id: booking.trip_coordinator_team_member_id || booking.trip_coordinator?.id || "",
        trip_start_date: booking.trip_start_date ? booking.trip_start_date.slice(0, 10) : "",
        trip_end_date: booking.trip_end_date ? booking.trip_end_date.slice(0, 10) : "",
        total_amount: booking.total_amount !== undefined && booking.total_amount !== null ? String(booking.total_amount) : "",
      });
    }
  }, [booking, isOpen]);

  if (!isOpen) return null;

  const handleChange = (key, val) => {
    setFormData((prev) => ({ ...prev, [key]: val }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      row_version: booking.row_version,
      group_name: formData.group_name ? formData.group_name.trim() || null : null,
      internal_notes: formData.internal_notes ? formData.internal_notes.trim() || null : null,
      trip_coordinator_team_member_id: formData.trip_coordinator_team_member_id || null,
      trip_start_date: formData.trip_start_date || null,
      trip_end_date: formData.trip_end_date || null,
      total_amount: formData.total_amount ? parseFloat(formData.total_amount) : null,
    });
  };

  return (
    <>
      <div className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs transition-opacity" onClick={onClose} />

      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l border-slate-200 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <Edit3 size={18} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">Edit Booking File Details</h3>
              <p className="text-[10px] font-semibold text-slate-400">Update file name, trip dates, coordinator & price</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Scrollable form body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5 space-y-4">
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Assigned Trip Coordinator</label>
            <select
              value={formData.trip_coordinator_team_member_id}
              onChange={(e) => handleChange("trip_coordinator_team_member_id", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
            >
              <option value="">Unassigned</option>
              {teamResponse?.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.display_name || m.name} ({m.designation || "Staff"})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Group / File Name</label>
            <input
              type="text"
              placeholder="e.g. Agarwal Family Diwali Trip 2026"
              value={formData.group_name}
              onChange={(e) => handleChange("group_name", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
            />
          </div>

          {/* Trip Start & End Dates */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Trip Start Date</label>
              <input
                type="date"
                value={formData.trip_start_date}
                onChange={(e) => handleChange("trip_start_date", e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Trip End Date</label>
              <input
                type="date"
                value={formData.trip_end_date}
                onChange={(e) => handleChange("trip_end_date", e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Confirmed Total Price (INR)</label>
            <input
              type="number"
              step="0.01"
              placeholder="e.g. 100000"
              value={formData.total_amount}
              onChange={(e) => handleChange("total_amount", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-bold font-mono"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Internal Notes</label>
            <textarea
              rows="6"
              placeholder="Operational instructions, custom package requests, payment schedules notes, etc."
              value={formData.internal_notes}
              onChange={(e) => handleChange("internal_notes", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[9px] text-slate-400 font-medium mt-1">This notes field is only visible to team staff and won't be shown to the traveler.</p>
          </div>
        </form>

        {/* Footer actions */}
        <div className="px-5 py-4 border-t border-slate-100 shrink-0 flex items-center justify-end space-x-2 bg-slate-50">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 bg-white hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isPending}
            className="px-5 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-md transition-colors flex items-center space-x-1.5"
          >
            {isPending && <Loader2 className="animate-spin" size={12} />}
            <span>Save Changes</span>
          </button>
        </div>

      </div>
    </>
  );
}

export default EditBookingDrawer;
