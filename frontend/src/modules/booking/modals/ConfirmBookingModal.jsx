import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { axiosClient } from "../../../api/axiosClient";
import { AlertTriangle, X, Loader2, Check } from "lucide-react";

export function ConfirmBookingModal({ isOpen, onClose, onConfirm, isPending, rowVersion, bookingNumber, totalAmount }) {
  const [coordinatorId, setCoordinatorId] = useState("");
  const [notes, setNotes] = useState("");

  const { data: teamResponse, isLoading: isLoadingTeam } = useQuery({
    queryKey: ["team-members-lookup"],
    queryFn: async () => {
      const res = await axiosClient.get("/team-members", { params: { page_size: 100 } });
      return res.data?.data?.items || [];
    },
    enabled: isOpen,
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!coordinatorId) {
      alert("Please select a trip coordinator.");
      return;
    }
    onConfirm({
      row_version: rowVersion,
      trip_coordinator_team_member_id: coordinatorId,
      notes: notes || null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <Check size={18} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">Confirm Booking File</h3>
              <p className="text-[10px] font-semibold text-slate-400">Unlock operational planning & fulfillment</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          
          {/* Quick Context Card */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-3.5 flex justify-between items-center text-xs font-semibold text-slate-600">
            <div>
              <span className="text-[10px] text-slate-400 block uppercase font-bold">Booking Ref</span>
              <span className="text-slate-800 font-mono font-bold">{bookingNumber}</span>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 block uppercase font-bold">Confirmed Total</span>
              <span className="text-slate-800 font-bold">INR {Number(totalAmount).toLocaleString("en-IN")}</span>
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Assign Trip Coordinator *</label>
            {isLoadingTeam ? (
              <div className="h-9 border border-slate-200 rounded-lg flex items-center justify-center bg-slate-50">
                <Loader2 className="animate-spin text-blue-600 mr-2" size={14} />
                <span className="text-xs text-slate-500 font-medium">Loading active team roster...</span>
              </div>
            ) : (
              <select
                value={coordinatorId}
                onChange={(e) => setCoordinatorId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
                required
              >
                <option value="">Select Coordinator</option>
                {teamResponse?.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.display_name || m.name} ({m.designation || "Staff"})
                  </option>
                ))}
              </select>
            )}
            <p className="text-[9px] text-slate-400 font-medium mt-1">This coordinator will own the operations trip plan and supplier allocations.</p>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Confirmation Notes</label>
            <textarea
              rows="3"
              placeholder="Add optional notes about special traveler requirements, voucher status, or group specs..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            />
          </div>

          <div className="flex items-center space-x-2 p-3 bg-amber-50/50 border border-amber-100 rounded-xl">
            <AlertTriangle className="text-amber-600 shrink-0" size={14} />
            <p className="text-[10px] text-amber-800 font-semibold leading-normal">
              Confirming will set this booking file to CONFIRMED. Once confirmed, payment tracking and supplier coordination commence.
            </p>
          </div>

          {/* Footer Action Buttons */}
          <div className="flex items-center justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 bg-white hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending || isLoadingTeam}
              className="px-5 py-2 rounded-lg text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-md transition-colors flex items-center space-x-1.5"
            >
              {isPending && <Loader2 className="animate-spin" size={12} />}
              <span>Confirm File</span>
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}

export default ConfirmBookingModal;
