import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery } from "@tanstack/react-query";
import crmApi from "../services/crmApi";
import { X, Loader2, AlertOctagon } from "lucide-react";

const markLostSchema = z.object({
  lost_reason_id: z.string().uuid("Please select a valid lost reason"),
  lost_date: z.string().min(1, "Lost date is required"),
});

export function MarkLeadLostModal({ isOpen, onClose, onConfirm, isSubmitting }) {
  // Queries for lost reasons dropdown options
  const { data: lostReasonsLookup, isLoading: isLoadingReasons } = useQuery({
    queryKey: ["lookups", "lost_reasons"],
    queryFn: () => crmApi.getLookups("lost_reasons"),
    enabled: isOpen,
    staleTime: 24 * 60 * 60 * 1000, // Caches lost reasons for 24h
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(markLostSchema),
    defaultValues: {
      lost_reason_id: "",
      lost_date: new Date().toISOString().split("T")[0], // Defaults to today
    }
  });

  const handleFormSubmit = (data) => {
    onConfirm(data, () => {
      reset();
      onClose();
    });
  };

  const reasons = lostReasonsLookup?.data || [];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl relative flex flex-col z-10 animate-in scale-in duration-200 select-none">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2 text-slate-800">
            <AlertOctagon size={16} className="text-red-500" />
            <h2 className="text-base font-bold">Mark Lead as Lost</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors focus:outline-none"
          >
            <X size={16} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-4">
          <p className="text-xs text-slate-500 font-medium leading-relaxed">
            Please select the primary reason for losing this lead, and verify the lost date. This action will transition the status to <span className="text-red-600 font-bold">LOST</span>.
          </p>

          {/* Lost Reason Select */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Lost Reason *</label>
            {isLoadingReasons ? (
              <div className="h-9 w-full bg-slate-50 animate-pulse rounded-lg border border-slate-200" />
            ) : (
              <select
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.lost_reason_id ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                }`}
                {...register("lost_reason_id")}
              >
                <option value="">Select Reason</option>
                {reasons.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            )}
            {errors.lost_reason_id && (
              <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.lost_reason_id.message}</p>
            )}
          </div>

          {/* Lost Date Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Lost Date *</label>
            <input
              type="date"
              className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.lost_date ? "border-red-300 focus:ring-red-500" : "border-slate-200"
              }`}
              {...register("lost_date")}
            />
            {errors.lost_date && (
              <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.lost_date.message}</p>
            )}
          </div>

          {/* Footer Actions */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3 shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 focus:outline-none"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || isLoadingReasons}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-red-600 hover:bg-red-700 focus:outline-none shadow-md shadow-red-500/10 flex items-center"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={14} />
                  <span>Marking Lost...</span>
                </>
              ) : (
                "Mark as Lost"
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

export default MarkLeadLostModal;
