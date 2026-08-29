import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery } from "@tanstack/react-query";
import { X, Loader2, Save } from "lucide-react";
import { axiosClient } from "../../../api/axiosClient";

// Helper to construct dynamic Zod schemas
const getValidationSchema = (slug) => {
  const base = {
    name: z.string().min(1, "Name is required").max(150, "Name cannot exceed 150 characters"),
    code: z.string().min(1, "Code is required").max(20, "Code cannot exceed 20 characters"),
    description: z.string().optional().nullable(),
    is_active: z.boolean().default(true),
    display_order: z.coerce.number().optional().nullable(),
  };

  if (slug === "countries") {
    return z.object({
      ...base,
      phone_code: z.string().min(1, "Phone code is required").regex(/^\+\d+$/, "Format must be +XX (e.g. +91)"),
    });
  }
  if (slug === "states") {
    return z.object({
      ...base,
      country_id: z.string().min(1, "Country selection is required"),
    });
  }
  if (slug === "districts") {
    return z.object({
      ...base,
      state_id: z.string().min(1, "State selection is required"),
    });
  }
  if (slug === "cities") {
    return z.object({
      ...base,
      state_id: z.string().min(1, "State selection is required"),
      District_id: z.string().min(1, "District selection is required"),
    });
  }
  if (slug === "destinations") {
    return z.object({
      ...base,
      slug: z.string().min(1, "Slug is required").regex(/^[a-z0-9\-]+$/, "Slug must be lowercase, digits, and hyphens only"),
      country_id: z.string().min(1, "Country selection is required"),
      state_id: z.string().min(1, "State selection is required"),
      district_id: z.string().min(1, "District selection is required"),
      cover_image: z.string().optional().nullable(),
    });
  }
  if (slug === "currencies") {
    return z.object({
      ...base,
      symbol: z.string().min(1, "Symbol is required"),
      is_default: z.boolean().optional(),
    });
  }
  if (slug === "cancellation-policies") {
    return z.object({
      ...base,
      refund_percentage: z.coerce.number().min(0, "Percentage must be >= 0").max(100, "Percentage must be <= 100"),
      days_before_travel: z.coerce.number().min(0, "Days must be >= 0"),
    });
  }
  if (slug === "tax-configurations") {
    return z.object({
      ...base,
      tax_rate: z.coerce.number().min(0, "Tax rate must be >= 0"),
      tax_type: z.enum(["INCLUSIVE", "EXCLUSIVE"], { errorMap: () => ({ message: "Select tax calculation type" }) }),
    });
  }

  return z.object(base);
};

export function MasterEditDrawer({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  editingItem = null,
  entityLabel = "Master Record",
  entitySlug = "",
}) {
  const isEdit = !!editingItem;

  // React Hook Form setup
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(getValidationSchema(entitySlug)),
    defaultValues: {
      name: "",
      code: "",
      description: "",
      is_active: true,
      display_order: "",
      phone_code: "",
      country_id: "",
      state_id: "",
      district_id: "",
      District_id: "",
      slug: "",
      cover_image: "",
      symbol: "",
      is_default: false,
      refund_percentage: "",
      days_before_travel: "",
      tax_rate: "",
      tax_type: "EXCLUSIVE",
    },
  });

  const nameVal = watch("name");

  // Query geography lookups
  const { data: countriesRes } = useQuery({
    queryKey: ["lookups", "countries"],
    queryFn: () => axiosClient.get("/masters/countries/lookup").then(res => res.data?.data?.items || []),
    enabled: isOpen && ["states", "destinations"].includes(entitySlug),
  });

  const { data: statesRes } = useQuery({
    queryKey: ["lookups", "states"],
    queryFn: () => axiosClient.get("/masters/states/lookup").then(res => res.data?.data?.items || []),
    enabled: isOpen && ["districts", "cities", "destinations"].includes(entitySlug),
  });

  const { data: districtsRes } = useQuery({
    queryKey: ["lookups", "districts"],
    queryFn: () => axiosClient.get("/masters/districts/lookup").then(res => res.data?.data?.items || []),
    enabled: isOpen && ["cities", "destinations"].includes(entitySlug),
  });

  const countriesList = countriesRes || [];
  const statesList = statesRes || [];
  const districtsList = districtsRes || [];

  // Sync edit item values on open
  useEffect(() => {
    if (editingItem) {
      reset({
        name: editingItem.name || "",
        code: editingItem.code || "",
        description: editingItem.description || "",
        is_active: editingItem.is_active !== undefined ? editingItem.is_active : true,
        display_order: editingItem.display_order !== undefined ? String(editingItem.display_order) : "",
        phone_code: editingItem.phone_code || "",
        country_id: editingItem.country_id || "",
        state_id: editingItem.state_id || "",
        district_id: editingItem.district_id || "",
        District_id: editingItem.District_id || "",
        slug: editingItem.slug || "",
        cover_image: editingItem.cover_image || "",
        symbol: editingItem.symbol || "",
        is_default: !!editingItem.is_default,
        refund_percentage: editingItem.refund_percentage !== undefined ? String(editingItem.refund_percentage) : "",
        days_before_travel: editingItem.days_before_travel !== undefined ? String(editingItem.days_before_travel) : "",
        tax_rate: editingItem.tax_rate !== undefined ? String(editingItem.tax_rate) : "",
        tax_type: editingItem.tax_type || "EXCLUSIVE",
      });
    } else {
      reset({
        name: "",
        code: "",
        description: "",
        is_active: true,
        display_order: "0",
        phone_code: "",
        country_id: "",
        state_id: "",
        district_id: "",
        District_id: "",
        slug: "",
        cover_image: "",
        symbol: "",
        is_default: false,
        refund_percentage: "",
        days_before_travel: "",
        tax_rate: "",
        tax_type: "EXCLUSIVE",
      });
    }
  }, [editingItem, reset, isOpen]);

  // Auto-generate code slug & route slug from name if creating new
  const handleNameBlur = () => {
    if (!isEdit && nameVal) {
      if (!watch("code")) {
        const generatedCode = nameVal
          .trim()
          .toUpperCase()
          .replace(/[^A-Z0-9\s]/g, "")
          .replace(/\s+/g, "_")
          .slice(0, 20);
        setValue("code", generatedCode);
      }
      if (entitySlug === "destinations" && !watch("slug")) {
        const generatedSlug = nameVal
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9\s-]/g, "")
          .replace(/\s+/g, "-")
          .replace(/-+/g, "-");
        setValue("slug", generatedSlug);
      }
    }
  };

  const handleFormSubmit = (data) => {
    const cleaned = {};
    
    // Core base fields
    cleaned.name = data.name.trim();
    cleaned.code = data.code.trim().toUpperCase();
    cleaned.description = data.description?.trim() || null;
    cleaned.is_active = data.is_active;
    cleaned.display_order = data.display_order !== "" ? parseInt(data.display_order, 10) : 0;

    // Entity-specific custom properties
    if (entitySlug === "countries") {
      cleaned.phone_code = data.phone_code.trim();
    } else if (entitySlug === "states") {
      cleaned.country_id = data.country_id;
    } else if (entitySlug === "districts") {
      cleaned.state_id = data.state_id;
    } else if (entitySlug === "cities") {
      cleaned.state_id = data.state_id;
      cleaned.District_id = data.District_id;
    } else if (entitySlug === "destinations") {
      cleaned.slug = data.slug.trim().toLowerCase();
      cleaned.country_id = data.country_id;
      cleaned.state_id = data.state_id;
      cleaned.district_id = data.district_id;
      cleaned.cover_image = data.cover_image?.trim() || null;
    } else if (entitySlug === "currencies") {
      cleaned.symbol = data.symbol.trim();
      cleaned.is_default = data.is_default;
    } else if (entitySlug === "cancellation-policies") {
      cleaned.refund_percentage = parseFloat(data.refund_percentage);
      cleaned.days_before_travel = parseInt(data.days_before_travel, 10);
    } else if (entitySlug === "tax-configurations") {
      cleaned.tax_rate = parseFloat(data.tax_rate);
      cleaned.tax_type = data.tax_type;
    }

    // Retain optimistic locking version when updating existing entries
    if (isEdit && editingItem?.version !== undefined) {
      cleaned.version = editingItem.version;
    }

    onSubmit(cleaned, () => {
      reset();
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
        <div className="w-screen max-w-md bg-white border-l border-slate-200 shadow-2xl flex flex-col justify-between">
          
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50 shrink-0">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                {isEdit ? "Update Configuration" : "New Master Entry"}
              </span>
              <h2 className="text-base font-bold text-slate-800 tracking-tight animate-fade-in">
                {isEdit ? `Edit ${entityLabel}` : `Add ${entityLabel}`}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-slate-650 hover:bg-slate-100 transition-colors focus:outline-none"
            >
              <X size={18} />
            </button>
          </div>

          {/* Form Content */}
          <form
            id="master-form"
            onSubmit={handleSubmit(handleFormSubmit)}
            className="flex-1 overflow-y-auto p-6 space-y-4 text-xs font-semibold text-slate-600"
          >
            {/* Name */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder={`e.g. ${entityLabel} Name`}
                onBlur={handleNameBlur}
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.name ? "border-rose-300 focus:ring-rose-500" : "border-slate-350"
                }`}
                {...register("name")}
              />
              {errors.name && (
                <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.name.message}</p>
              )}
            </div>

            {/* Code */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Code <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="e.g. DELUXE_ROOM, GST_18"
                disabled={isEdit}
                className={`w-full px-3 py-2 border rounded-lg text-xs uppercase disabled:opacity-60 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.code ? "border-rose-300 focus:ring-rose-500" : "border-slate-350"
                } ${isEdit ? "bg-slate-100 cursor-not-allowed" : "bg-slate-50"}`}
                {...register("code")}
              />
              {errors.code && (
                <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.code.message}</p>
              )}
            </div>

            {/* Entity-specific Fields */}

            {/* countries: phone_code */}
            {entitySlug === "countries" && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  International Phone Code <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. +91"
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.phone_code ? "border-rose-300 focus:ring-rose-500" : "border-slate-350"
                  }`}
                  {...register("phone_code")}
                />
                {errors.phone_code && (
                  <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.phone_code.message}</p>
                )}
              </div>
            )}

            {/* states: country_id */}
            {entitySlug === "states" && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Country <span className="text-rose-500">*</span>
                </label>
                <select
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                    errors.country_id ? "border-rose-300" : "border-slate-355"
                  }`}
                  {...register("country_id")}
                >
                  <option value="">Select Country</option>
                  {countriesList.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.code})
                    </option>
                  ))}
                </select>
                {errors.country_id && (
                  <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.country_id.message}</p>
                )}
              </div>
            )}

            {/* districts: state_id */}
            {entitySlug === "districts" && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  State / Province <span className="text-rose-500">*</span>
                </label>
                <select
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                    errors.state_id ? "border-rose-300" : "border-slate-355"
                  }`}
                  {...register("state_id")}
                >
                  <option value="">Select State</option>
                  {statesList.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.code})
                    </option>
                  ))}
                </select>
                {errors.state_id && (
                  <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.state_id.message}</p>
                )}
              </div>
            )}

            {/* cities: state_id and District_id */}
            {entitySlug === "cities" && (
              <>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    State / Province <span className="text-rose-500">*</span>
                  </label>
                  <select
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.state_id ? "border-rose-300" : "border-slate-355"
                    }`}
                    {...register("state_id")}
                  >
                    <option value="">Select State</option>
                    {statesList.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.code})
                      </option>
                    ))}
                  </select>
                  {errors.state_id && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.state_id.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    District <span className="text-rose-500">*</span>
                  </label>
                  <select
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.District_id ? "border-rose-300" : "border-slate-355"
                    }`}
                    {...register("District_id")}
                  >
                    <option value="">Select District</option>
                    {districtsList.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name} ({d.code})
                      </option>
                    ))}
                  </select>
                  {errors.District_id && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.District_id.message}</p>
                  )}
                </div>
              </>
            )}

            {/* destinations: slug, country_id, state_id, district_id, cover_image */}
            {entitySlug === "destinations" && (
              <>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Slug Identifier <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. ooty-nilgiris"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.slug ? "border-rose-300 focus:ring-rose-500" : "border-slate-350"
                    }`}
                    {...register("slug")}
                  />
                  {errors.slug && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.slug.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-755 mb-1">Country *</label>
                    <select
                      className="w-full px-2 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                      {...register("country_id")}
                    >
                      <option value="">Country</option>
                      {countriesList.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-755 mb-1">State *</label>
                    <select
                      className="w-full px-2 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                      {...register("state_id")}
                    >
                      <option value="">State</option>
                      {statesList.map((s) => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-755 mb-1">District *</label>
                    <select
                      className="w-full px-2 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                      {...register("district_id")}
                    >
                      <option value="">District</option>
                      {districtsList.map((d) => (
                        <option key={d.id} value={d.id}>{d.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Cover Image URL</label>
                  <input
                    type="text"
                    placeholder="e.g. /images/places/ooty.jpg"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                    {...register("cover_image")}
                  />
                </div>
              </>
            )}

            {/* currencies: symbol, is_default */}
            {entitySlug === "currencies" && (
              <>
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Currency Symbol <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. ₹ or $"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.symbol ? "border-rose-300" : "border-slate-350"
                    }`}
                    {...register("symbol")}
                  />
                  {errors.symbol && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.symbol.message}</p>
                  )}
                </div>

                <div className="flex items-center space-x-2 pt-2">
                  <input
                    type="checkbox"
                    id="is-default-checkbox"
                    className="w-4 h-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                    {...register("is_default")}
                  />
                  <label htmlFor="is-default-checkbox" className="text-xs font-bold text-slate-700">
                    Set as system default currency
                  </label>
                </div>
              </>
            )}

            {/* cancellation-policies: refund_percentage, days_before_travel */}
            {entitySlug === "cancellation-policies" && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Refund Percentage (%) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="e.g. 50"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.refund_percentage ? "border-rose-300" : "border-slate-350"
                    }`}
                    {...register("refund_percentage")}
                  />
                  {errors.refund_percentage && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.refund_percentage.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Days Prior to Travel <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 15"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.days_before_travel ? "border-rose-300" : "border-slate-350"
                    }`}
                    {...register("days_before_travel")}
                  />
                  {errors.days_before_travel && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.days_before_travel.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* tax-configurations: tax_rate, tax_type */}
            {entitySlug === "tax-configurations" && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Tax / GST Rate (%) <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="e.g. 18.00"
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.tax_rate ? "border-rose-300" : "border-slate-350"
                    }`}
                    {...register("tax_rate")}
                  />
                  {errors.tax_rate && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.tax_rate.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Tax Application Type <span className="text-rose-500">*</span>
                  </label>
                  <select
                    className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none ${
                      errors.tax_type ? "border-rose-300" : "border-slate-355"
                    }`}
                    {...register("tax_type")}
                  >
                    <option value="EXCLUSIVE">EXCLUSIVE</option>
                    <option value="INCLUSIVE">INCLUSIVE</option>
                  </select>
                  {errors.tax_type && (
                    <p className="mt-1 text-[10px] font-bold text-rose-600">{errors.tax_type.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* Display Order */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Display Sequence / Order</label>
              <input
                type="number"
                placeholder="e.g. 0"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...register("display_order")}
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Description</label>
              <textarea
                rows="3"
                placeholder="Optional notes or configuration details..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...register("description")}
              />
            </div>

            {/* Status Toggle */}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
              <div>
                <label className="text-xs font-bold text-slate-700 block">Record Status</label>
                <p className="text-[10px] text-slate-400">Inactive records are hidden from dropdown options.</p>
              </div>
              <input
                type="checkbox"
                className="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                {...register("is_active")}
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
              form="master-form"
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
                  <span>{isEdit ? "Update Master" : "Save Master"}</span>
                </>
              )}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default MasterEditDrawer;
