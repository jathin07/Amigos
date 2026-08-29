import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery } from "@tanstack/react-query";
import proposalApi from "../services/proposalApi";
import { X, Loader2, FileCheck } from "lucide-react";

const finalizeProposalSchema = z.object({
  approved_by_team_member_id: z.string().uuid("Approving manager is required"),
  approved_date: z.string().min(1, "Approval date is required"),
});

export function FinalizeProposalModal({ isOpen, onClose, onFinalize, isSubmitting, rowVersion }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(finalizeProposalSchema),
    defaultValues: {
      approved_date: new Date().toISOString().split("T")[0],
    }
  });

  // Query team lookup
  const { data: teamLookup } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => proposalApi.getTeamMembers(),
    enabled: isOpen,
  });

  const teamMembers = teamLookup?.data?.items || [];

  const handleFormSubmit = (data) => {
    onFinalize({
      ...data,
      row_version: rowVersion,
    }, () => {
      reset();
      onClose();
    });
  };

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
            <FileCheck size={16} className="text-emerald-600 animate-pulse" />
            <h2 className="text-base font-bold">Freeze & Finalize Proposal</h2>
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
            Finalizing will freeze this proposal as <strong className="text-slate-700">read-only</strong>, generate a formal customer version, and enable booking conversion.
          </p>

          {/* Approver Selection */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Approved By Manager *</label>
            <select
              className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.approved_by_team_member_id ? "border-red-300 focus:ring-red-500" : "border-slate-300"
              }`}
              {...register("approved_by_team_member_id")}
            >
              <option value="">Select manager</option>
              {teamMembers.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.display_name}
                </option>
              ))}
            </select>
            {errors.approved_by_team_member_id && (
              <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.approved_by_team_member_id.message}</p>
            )}
          </div>

          {/* Approved Date */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Approval Date *</label>
            <input
              type="date"
              className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.approved_date ? "border-red-300 focus:ring-red-500" : "border-slate-300"
              }`}
              {...register("approved_date")}
            />
            {errors.approved_date && (
              <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.approved_date.message}</p>
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
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none shadow-md shadow-emerald-500/10 flex items-center"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={14} />
                  <span>Freezing...</span>
                </>
              ) : (
                "Finalize & Freeze"
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

export default FinalizeProposalModal;
