import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { X, Loader2, UserPlus, Save } from "lucide-react";

const teamMemberSchema = z.object({
  first_name: z.string().min(1, "First name is required").max(100),
  last_name: z.string().max(100).optional().nullable(),
  display_name: z.string().min(1, "Display name is required").max(150),
  employee_code: z.string().min(1, "Employee ID code is required").max(50),
  official_email: z.string().email("Valid official email is required"),
  personal_email: z.string().email("Valid email").optional().or(z.literal("")).nullable(),
  phone: z.string().min(1, "Phone number is required").max(20),
  designation: z.string().max(100).optional().nullable(),
  employment_status: z.string().optional().nullable(),
  joined_date: z.string().optional().nullable(),
  emergency_contact_name: z.string().max(150).optional().nullable(),
  emergency_contact_phone: z.string().max(20).optional().nullable(),
  is_active: z.boolean().default(true),
});

export function CreateTeamMemberModal({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  editingMember = null,
}) {
  const isEdit = !!editingMember;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(teamMemberSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      display_name: "",
      employee_code: "",
      official_email: "",
      personal_email: "",
      phone: "",
      designation: "",
      employment_status: "Full-Time",
      joined_date: new Date().toISOString().split("T")[0],
      emergency_contact_name: "",
      emergency_contact_phone: "",
      is_active: true,
    },
  });

  const firstNameVal = watch("first_name");
  const lastNameVal = watch("last_name");

  // Sync form values on Edit mode
  useEffect(() => {
    if (editingMember) {
      reset({
        first_name: editingMember.first_name || "",
        last_name: editingMember.last_name || "",
        display_name: editingMember.display_name || "",
        employee_code: editingMember.employee_code || "",
        official_email: editingMember.official_email || "",
        personal_email: editingMember.personal_email || "",
        phone: editingMember.phone || "",
        designation: editingMember.designation || "",
        employment_status: editingMember.employment_status || "Full-Time",
        joined_date: editingMember.joined_date || "",
        emergency_contact_name: editingMember.emergency_contact_name || "",
        emergency_contact_phone: editingMember.emergency_contact_phone || "",
        is_active: editingMember.is_active !== undefined ? editingMember.is_active : true,
      });
    } else {
      reset({
        first_name: "",
        last_name: "",
        display_name: "",
        employee_code: `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
        official_email: "",
        personal_email: "",
        phone: "",
        designation: "",
        employment_status: "Full-Time",
        joined_date: new Date().toISOString().split("T")[0],
        emergency_contact_name: "",
        emergency_contact_phone: "",
        is_active: true,
      });
    }
  }, [editingMember, reset, isOpen]);

  // Auto-generate display name from first and last name
  useEffect(() => {
    if (!isEdit && (firstNameVal || lastNameVal)) {
      const combined = `${firstNameVal || ""} ${lastNameVal || ""}`.trim();
      setValue("display_name", combined);
    }
  }, [firstNameVal, lastNameVal, isEdit, setValue]);

  const handleFormSubmit = (data) => {
    const sanitized = { ...data };
    Object.keys(sanitized).forEach((key) => {
      if (sanitized[key] === "") {
        sanitized[key] = null;
      }
    });
    onSubmit(sanitized, () => {
      reset();
      onClose();
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 select-none">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Modal Container */}
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl relative flex flex-col z-10 animate-in scale-in duration-200">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2 text-slate-800">
            <UserPlus size={18} className="text-blue-600" />
            <h2 className="text-base font-bold">
              {isEdit ? "Update Staff Record" : "Add New Team Member"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors focus:outline-none"
          >
            <X size={16} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
          
          {/* First & Last Name */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                First Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Jathin"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                  errors.first_name ? "border-rose-300 focus:ring-rose-500" : "border-slate-300"
                }`}
                {...register("first_name")}
              />
              {errors.first_name && (
                <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.first_name.message}</p>
              )}
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">Last Name</label>
              <input
                type="text"
                placeholder="e.g. Mohan"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                {...register("last_name")}
              />
            </div>
          </div>

          {/* Display Name & Employee Code */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Display Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Jathin M"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                  errors.display_name ? "border-rose-300 focus:ring-rose-500" : "border-slate-300"
                }`}
                {...register("display_name")}
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Employee Code / ID <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. EMP-1002"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none font-mono ${
                  errors.employee_code ? "border-rose-300 focus:ring-rose-500" : "border-slate-300"
                }`}
                {...register("employee_code")}
              />
            </div>
          </div>

          {/* Official Email & Phone */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Official Email <span className="text-rose-500">*</span>
              </label>
              <input
                type="email"
                placeholder="jathin@amigos.com"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                  errors.official_email ? "border-rose-300 focus:ring-rose-500" : "border-slate-300"
                }`}
                {...register("official_email")}
              />
              {errors.official_email && (
                <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.official_email.message}</p>
              )}
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">
                Phone Number <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="+91 9790612207"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                  errors.phone ? "border-rose-300 focus:ring-rose-500" : "border-slate-300"
                }`}
                {...register("phone")}
              />
            </div>
          </div>

          {/* Designation & Employment Status */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">Designation</label>
              <input
                type="text"
                placeholder="e.g. Senior Travel Specialist"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                {...register("designation")}
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">Employment Status</label>
              <select
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none font-semibold text-slate-700"
                {...register("employment_status")}
              >
                <option value="Full-Time">Full-Time</option>
                <option value="Part-Time">Part-Time</option>
                <option value="Probation">Probation</option>
                <option value="Contract">Contract</option>
              </select>
            </div>
          </div>

          {/* Joined Date */}
          <div className="text-xs">
            <label className="block font-bold text-slate-700 mb-1">Joining Date</label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
              {...register("joined_date")}
            />
          </div>

          {/* Emergency Contact */}
          <div className="pt-2 border-t border-slate-100 space-y-3">
            <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Emergency Contact Details</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Contact Name</label>
                <input
                  type="text"
                  placeholder="e.g. Relative Name"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                  {...register("emergency_contact_name")}
                />
              </div>
              <div>
                <label className="block font-bold text-slate-700 mb-1">Contact Phone</label>
                <input
                  type="text"
                  placeholder="+91 9876543210"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                  {...register("emergency_contact_phone")}
                />
              </div>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end space-x-3 shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 bg-white hover:bg-slate-50 focus:outline-none"
            >
              Cancel
            </button>
            <button
              type="submit"
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
                  <span>{isEdit ? "Update Staff" : "Add Staff Member"}</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

export default CreateTeamMemberModal;
