import React, { useState } from "react";
import { AlertCircle, X, Loader2 } from "lucide-react";

export function CancelBookingModal({ isOpen, onClose, onCancel, isPending, rowVersion, bookingNumber }) {
  const [reason, setReason] = useState("");

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!reason || reason.trim().length < 5) {
      alert("Please provide a reason of at least 5 characters.");
      return;
    }
    onCancel({
      row_version: rowVersion,
      cancellation_reason: reason.trim(),
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
              <AlertCircle size={18} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">Cancel Booking File</h3>
              <p className="text-[10px] font-semibold text-slate-400">Abort operational fulfillment lifecycle</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          
          {/* Quick Context Card */}
          <div className="bg-slate-50 border border-slate-100 rounded-xl p-3 flex justify-between items-center text-xs font-semibold text-slate-600">
            <div>
              <span className="text-[10px] text-slate-400 block uppercase font-bold">Booking Ref</span>
              <span className="text-slate-800 font-mono font-bold">{bookingNumber}</span>
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Reason for Cancellation *</label>
            <textarea
              rows="4"
              required
              placeholder="State clear reasons (e.g. customer request, payment default, schedule conflict)..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            />
            <p className="text-[9px] text-slate-400 font-medium mt-1">Minimum 5 characters. This will be permanently recorded in the status audit timeline.</p>
          </div>

          <div className="flex items-center space-x-2 p-3 bg-rose-50/50 border border-rose-100 rounded-xl">
            <AlertCircle className="text-rose-600 shrink-0" size={14} />
            <p className="text-[10px] text-rose-800 font-semibold leading-normal">
              Warning: Cancellation is a terminal status action. This will release all locked supplier allotments and cancel all unpaid installments.
            </p>
          </div>

          {/* Footer Action Buttons */}
          <div className="flex items-center justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 bg-white hover:bg-slate-50 transition-colors"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="px-5 py-2 rounded-lg text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 shadow-md transition-colors flex items-center space-x-1.5"
            >
              {isPending && <Loader2 className="animate-spin" size={12} />}
              <span>Cancel File</span>
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}

export default CancelBookingModal;
