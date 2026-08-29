import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery } from "@tanstack/react-query";
import crmApi from "../services/crmApi";
import { X, Loader2, Save } from "lucide-react";
import { useOrganizationsLookup } from "../../organization/hooks/useOrganization";
import { axiosClient } from "../../../api/axiosClient";

const editLeadSchema = z.object({
  trip_type_id: z.string().uuid().optional().or(z.literal("")),
  priority_id: z.string().uuid().optional().or(z.literal("")),
  package_id: z.string().uuid().optional().or(z.literal("")),
  organization_division_id: z.string().optional().nullable(),
  traveler_count: z.coerce.number().min(1, "Must be at least 1 traveler"),
  male_count: z.coerce.number().min(0).optional(),
  female_count: z.coerce.number().min(0).optional(),
  faculty_count: z.coerce.number().min(0).optional(),
  travel_start_date: z.string().optional().or(z.literal("")),
  travel_end_date: z.string().optional().or(z.literal("")),
  expected_travel_date: z.string().optional().or(z.literal("")),
  estimated_trip_days: z.coerce.number().min(1).optional().or(z.literal("")),
  estimated_trip_nights: z.coerce.number().min(0).optional().or(z.literal("")),
  budget: z.coerce.number().min(0, "Budget must be positive").optional().or(z.literal("")),
  destinations: z.array(z.string()).optional().default([]),
  notes: z.string().max(2000).optional().or(z.literal("")),
}).refine(
  (data) => {
    if (data.travel_start_date && data.travel_end_date) {
      return new Date(data.travel_end_date) >= new Date(data.travel_start_date);
    }
    return true;
  },
  {
    message: "End date must be on or after start date",
    path: ["travel_end_date"],
  }
);

export function EditLeadDrawer({ isOpen, onClose, lead, onSubmit, isSubmitting }) {
  // Query lookups
  const { data: prioritiesLookup } = useQuery({
    queryKey: ["lookups", "priorities"],
    queryFn: () => crmApi.getLookups("priorities"),
    enabled: isOpen,
    staleTime: 24 * 60 * 60 * 1000,
  });

  const { data: packagesLookup } = useQuery({
    queryKey: ["packages"],
    queryFn: () => crmApi.getPackages(),
    enabled: isOpen,
    staleTime: 5 * 60 * 1000,
  });

  const { data: tripTypesLookup } = useQuery({
    queryKey: ["catalog", "trip-types"],
    queryFn: () => crmApi.getTripTypes(),
    enabled: isOpen,
  });

  const priorities = prioritiesLookup?.data || [];
  const packages = packagesLookup?.data?.items || [];
  const tripTypes = tripTypesLookup?.data || tripTypesLookup?.data?.items || [];

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(editLeadSchema),
    defaultValues: {
      trip_type_id: "",
      priority_id: "",
      package_id: "",
      traveler_count: 1,
      male_count: 0,
      female_count: 0,
      faculty_count: 0,
      travel_start_date: "",
      travel_end_date: "",
      expected_travel_date: "",
      estimated_trip_days: "",
      estimated_trip_nights: "",
      budget: "",
      destinations: [],
      notes: "",
    },
  });

  const selectedDestinations = watch("destinations") || [];

  // Reset values when lead updates or drawer opens
  useEffect(() => {
    if (lead && isOpen) {
      reset({
        trip_type_id: lead.trip_type?.id || "",
        priority_id: lead.priority?.id || "",
        package_id: lead.package?.id || "",
        traveler_count: lead.traveler_count || 1,
        male_count: lead.male_count || 0,
        female_count: lead.female_count || 0,
        faculty_count: lead.faculty_count || 0,
        travel_start_date: lead.travel_start_date || "",
        travel_end_date: lead.travel_end_date || "",
        expected_travel_date: lead.expected_travel_date || "",
        estimated_trip_days: lead.estimated_trip_days || "",
        estimated_trip_nights: lead.estimated_trip_nights || "",
        budget: lead.budget || "",
        destinations: lead.destinations?.map((d) => d.destination_id) || [],
        notes: lead.notes || "",
      });
    }
  }, [lead, isOpen, reset]);

  const handleDestinationToggle = (destId) => {
    const next = selectedDestinations.includes(destId)
      ? selectedDestinations.filter((id) => id !== destId)
      : [...selectedDestinations, destId];
    setValue("destinations", next, { shouldValidate: true });
  };

  const handleFormSubmit = (data) => {
    const payload = {
      version: lead.version, // optimistic lock version is REQUIRED
      trip_type_id: data.trip_type_id || null,
      priority_id: data.priority_id || null,
      package_id: data.package_id || null,
      traveler_count: data.traveler_count,
      male_count: data.male_count || 0,
      female_count: data.female_count || 0,
      faculty_count: data.faculty_count || 0,
      travel_start_date: data.travel_start_date || null,
      travel_end_date: data.travel_end_date || null,
      expected_travel_date: data.expected_travel_date || null,
      estimated_trip_days: data.estimated_trip_days ? parseInt(data.estimated_trip_days, 10) : null,
      estimated_trip_nights: data.estimated_trip_nights ? parseInt(data.estimated_trip_nights, 10) : null,
      budget: data.budget ? parseFloat(data.budget) : null,
      destinations: (data.destinations || []).map((dId) => ({
        destination_id: dId,
        priority: "High",
      })),
      notes: data.notes || null,
    };

    onSubmit(payload, () => {
      onClose();
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden select-none">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity duration-300"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-lg bg-white border-l border-slate-200 shadow-2xl flex flex-col justify-between">
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50 shrink-0">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Lead: {lead?.lead_number}
              </span>
              <h2 className="text-base font-bold text-slate-800 tracking-tight">Edit Lead Details</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 transition-colors focus:outline-none"
            >
              <X size={18} />
            </button>
          </div>

          {/* Form Content */}
          <form
            id="edit-lead-form"
            onSubmit={handleSubmit(handleFormSubmit)}
            className="flex-1 overflow-y-auto p-6 space-y-5 text-xs font-semibold text-slate-600"
          >
            {/* Section 1: Trip Specifications */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Trip Specifications</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Trip Type (Category)</label>
                  <select
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    {...register("trip_type_id")}
                  >
                    <option value="">Select trip type...</option>
                    {tripTypes.map((tt) => (
                      <option key={tt.id} value={tt.id}>{tt.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Priority</label>
                  <select
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    {...register("priority_id")}
                  >
                    <option value="">Select Priority</option>
                    {priorities.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Package Link</label>
                  <select
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    {...register("package_id")}
                  >
                    <option value="">None / Custom</option>
                    {packages.map((pkg) => (
                      <option key={pkg.id} value={pkg.id}>
                        {pkg.title}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Section 2: Traveler Demographics */}
            <div className="space-y-3 pt-3 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Traveler Demographics</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Total count *</label>
                  <input
                    type="number"
                    min="1"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.traveler_count ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                    }`}
                    {...register("traveler_count")}
                  />
                  {errors.traveler_count && (
                    <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.traveler_count.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Male</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("male_count")}
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Female</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("female_count")}
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Faculty</label>
                  <input
                    type="number"
                    min="0"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("faculty_count")}
                  />
                </div>
              </div>
            </div>

            {/* Section 3: Dates & Duration */}
            <div className="space-y-3 pt-3 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Dates & Budget</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="col-span-2 sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Budget (INR)</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="Flexible"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("budget")}
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Days</label>
                  <input
                    type="number"
                    min="1"
                    placeholder="Days"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("estimated_trip_days")}
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Nights</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="Nights"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("estimated_trip_nights")}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Start Date</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("travel_start_date")}
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">End Date</label>
                  <input
                    type="date"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.travel_end_date ? "border-red-300" : "border-slate-200"
                    }`}
                    {...register("travel_end_date")}
                  />
                  {errors.travel_end_date && (
                    <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.travel_end_date.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Alt Travel Date</label>
                  <input
                    type="date"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("expected_travel_date")}
                  />
                </div>
              </div>
            </div>

            {/* Destinations Checklist Removed */}

            {/* Section 5: Notes */}
            <div className="space-y-2 pt-3 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-600">Requirement Notes / Special Requests</label>
              <textarea
                rows="3"
                placeholder="Special notes or requests..."
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                {...register("notes")}
              />
            </div>
          </form>

          {/* Footer Actions */}
          <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-end space-x-3 shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 bg-white hover:bg-slate-100 focus:outline-none"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="edit-lead-form"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none shadow-md shadow-blue-500/10 flex items-center"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={14} />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save size={14} className="mr-1.5" />
                  <span>Update Details</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EditLeadDrawer;
