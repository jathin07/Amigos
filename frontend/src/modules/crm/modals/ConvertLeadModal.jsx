import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery } from "@tanstack/react-query";
import { axiosClient } from "../../../api/axiosClient";
import { X, Loader2, RefreshCw } from "lucide-react";

const convertLeadSchema = z.object({
  trip_start_date: z.string().min(1, "Trip start date is required"),
  trip_end_date: z.string().min(1, "Trip end date is required"),
  total_amount: z.coerce.number().min(1, "Trip price must be a positive number"),
}).refine(
  (data) => new Date(data.trip_end_date) >= new Date(data.trip_start_date),
  {
    message: "End date must be on or after start date",
    path: ["trip_end_date"],
  }
);

export function ConvertLeadModal({ isOpen, onClose, onConvert, isSubmitting, defaultValues = {} }) {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(convertLeadSchema),
    defaultValues: {
      trip_start_date: defaultValues.travel_start_date || "",
      trip_end_date: defaultValues.travel_end_date || "",
      total_amount: defaultValues.budget || "",
    }
  });



  const handleFormSubmit = (data) => {
    onConvert(data, () => {
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
            <RefreshCw size={16} className="text-blue-600 animate-spin" />
            <h2 className="text-base font-bold">Convert Lead to Booking</h2>
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
          <p className="text-xs text-slate-500 font-medium">
            This action will create an active Booking file and transition the Lead status to <span className="text-emerald-600 font-bold">WON</span>.
          </p>

          {/* Start & End Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Confirmed Start Date *</label>
              <input
                type="date"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.trip_start_date ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                }`}
                {...register("trip_start_date")}
              />
              {errors.trip_start_date && (
                <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.trip_start_date.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Confirmed End Date *</label>
              <input
                type="date"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.trip_end_date ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                }`}
                {...register("trip_end_date")}
              />
              {errors.trip_end_date && (
                <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.trip_end_date.message}</p>
              )}
            </div>
          </div>

          {/* Pricing amount */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Confirmed Total Price (INR) *</label>
            <input
              type="number"
              placeholder="e.g. 75000"
              className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.total_amount ? "border-red-300 focus:ring-red-500" : "border-slate-200"
              }`}
              {...register("total_amount")}
            />
            {errors.total_amount && (
              <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.total_amount.message}</p>
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
              className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none shadow-md shadow-blue-500/10 flex items-center"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={14} />
                  <span>Converting...</span>
                </>
              ) : (
                "Convert Lead File"
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

export default ConvertLeadModal;
