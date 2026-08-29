import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import crmApi from "../services/crmApi";
import { X, Loader2, ChevronDown, Plus, Building, Package } from "lucide-react";
import { useOrganizationsLookup } from "../../organization/hooks/useOrganization";
import { axiosClient } from "../../../api/axiosClient";

const createLeadSchema = z.object({
  contact_person: z.object({
    name: z.string().min(1, "Customer name is required").max(150),
    phone: z.string().min(10, "Phone number must be at least 10 digits").max(20),
    email: z.string().email("Invalid email address").optional().or(z.literal("")),
    designation: z.string().max(100).optional().or(z.literal("")),
    organization_id: z.string().optional().nullable(),
  }),
  lead_source_id: z.string().uuid("Lead source is required"),
  priority_id: z.string().uuid("Priority is required").optional().or(z.literal("")),
  trip_type_id: z.string().uuid().optional().or(z.literal("")),
  package_id: z.string().uuid("Package is required").optional().or(z.literal("")),
  organization_division_id: z.string().optional().nullable(),
  traveler_count: z.coerce.number().min(1, "Must be at least 1 traveler"),
  male_count: z.coerce.number().min(0).optional(),
  female_count: z.coerce.number().min(0).optional(),
  faculty_count: z.coerce.number().min(0).optional(),
  budget: z.coerce.number().min(0, "Budget must be a positive number").optional().or(z.literal("")),
  travel_start_date: z.string().optional().or(z.literal("")),
  travel_end_date: z.string().optional().or(z.literal("")),
  expected_travel_date: z.string().optional().or(z.literal("")),
  estimated_trip_days: z.coerce.number().min(1).optional().or(z.literal("")),
  destinations: z.array(z.string()).optional().default([]),
  notes: z.string().max(2000).optional().or(z.literal("")),
});

export function CreateLeadModal({ isOpen, onClose, onSubmit, isSubmitting }) {
  const queryClient = useQueryClient();
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    reset
  } = useForm({
    resolver: zodResolver(createLeadSchema),
    defaultValues: {
      traveler_count: 1,
      male_count: 0,
      faculty_count: 0,
      destinations: [],
    }
  });

  // Destination Combobox state
  const [destSearchInput, setDestSearchInput] = useState("");
  const [showDestMenu, setShowDestMenu] = useState(false);
  const [selectedDestList, setSelectedDestList] = useState([]); // Array of { id?: string, name: string }
  const [isCreatingDest, setIsCreatingDest] = useState(false);
  
  // Organization Combobox state
  const [orgInput, setOrgInput] = useState("");
  const [orgSelectedId, setOrgSelectedId] = useState("");
  const [showOrgMenu, setShowOrgMenu] = useState(false);
  const [isCreatingOrg, setIsCreatingOrg] = useState(false);

  // Division Combobox state
  const [divisionInput, setDivisionInput] = useState("");
  const [showDivMenu, setShowDivMenu] = useState(false);

  // Package Combobox state
  const [packageInput, setPackageInput] = useState("");
  const [packageSelectedId, setPackageSelectedId] = useState("");
  const [showPackageMenu, setShowPackageMenu] = useState(false);

  const selectedDestinations = watch("destinations") || [];
  const selectedTripTypeId = watch("trip_type_id");

  // Query lookups
  const { data: sourcesLookup } = useQuery({
    queryKey: ["lookups", "sources"],
    queryFn: () => crmApi.getLookups("sources"),
    enabled: isOpen,
  });

  const { data: prioritiesLookup } = useQuery({
    queryKey: ["lookups", "priorities"],
    queryFn: () => crmApi.getLookups("priorities"),
    enabled: isOpen,
  });

  const { data: packagesLookup } = useQuery({
    queryKey: ["packages"],
    queryFn: () => crmApi.getPackages(),
    enabled: isOpen,
  });

  const { data: tripTypesLookup } = useQuery({
    queryKey: ["catalog", "trip-types"],
    queryFn: () => crmApi.getTripTypes(),
    enabled: isOpen,
  });

  const { data: destinationsLookup } = useQuery({
    queryKey: ["catalog", "destinations"],
    queryFn: () => crmApi.getDestinations(),
    enabled: isOpen,
  });

  const { data: orgsLookup } = useOrganizationsLookup();

  const { data: orgDetails } = useQuery({
    queryKey: ["organization", orgSelectedId],
    queryFn: () => axiosClient.get(`/organization/${orgSelectedId}`).then((res) => res.data?.data || {}),
    enabled: !!orgSelectedId && orgSelectedId !== "",
  });

  const sources = sourcesLookup?.data || [];
  const priorities = prioritiesLookup?.data || [];
  const packages = packagesLookup?.data?.items || [];
  const tripTypes = tripTypesLookup?.data?.items || [];
  const allDestinations = destinationsLookup?.data || destinationsLookup?.data?.items || [];
  const organizations = orgsLookup?.data?.items || [];
  const divisions = orgDetails?.divisions || [];

  const selectedTripType = tripTypes.find((t) => t.id === selectedTripTypeId);

  const handleAddDestObj = (destObj) => {
    if (!selectedDestList.some((d) => d.name.toLowerCase() === destObj.name.toLowerCase())) {
      setSelectedDestList((prev) => [...prev, destObj]);
    }
    setDestSearchInput("");
    setShowDestMenu(false);
  };

  const handleRemoveDestObj = (destName) => {
    setSelectedDestList((prev) => prev.filter((d) => d.name.toLowerCase() !== destName.toLowerCase()));
  };

  const handleCreateNewDestination = async (nameToCreate) => {
    const trimmed = nameToCreate.trim();
    if (!trimmed) return;
    try {
      setIsCreatingDest(true);
      const res = await crmApi.createDestination(trimmed);
      const createdObj = res.data || { name: trimmed };
      queryClient.invalidateQueries({ queryKey: ["catalog", "destinations"] });
      queryClient.invalidateQueries({ queryKey: ["destinations"] });
      handleAddDestObj({ id: createdObj.id, name: createdObj.name || trimmed });
    } catch (err) {
      console.error("Auto destination creation error:", err);
      // Fallback add locally
      handleAddDestObj({ name: trimmed });
    } finally {
      setIsCreatingDest(false);
    }
  };

  const handleFormSubmit = async (data) => {
    let finalOrgId = orgSelectedId || null;
    let finalDivisionId = data.organization_division_id || null;

    // 1. Check if user entered a custom organization name not in DB yet
    if (!finalOrgId && orgInput.trim()) {
      const trimmedOrg = orgInput.trim();
      const existingMatch = organizations.find(
        (o) => o.name.toLowerCase() === trimmedOrg.toLowerCase()
      );
      if (existingMatch) {
        finalOrgId = existingMatch.id;
      } else {
        try {
          setIsCreatingOrg(true);
          const divisionsPayload = divisionInput.trim()
            ? [{ department: divisionInput.trim(), batch: divisionInput.trim() }]
            : null;

          const newOrgRes = await axiosClient.post("/organization", {
            organization_name: trimmedOrg,
            is_active: true,
            divisions: divisionsPayload,
          });
          const createdOrgData = newOrgRes.data?.data;
          finalOrgId = createdOrgData?.id || null;
          if (createdOrgData?.divisions?.length > 0) {
            finalDivisionId = createdOrgData.divisions[0].id;
          }
          queryClient.invalidateQueries({ queryKey: ["organizations"] });
          queryClient.invalidateQueries({ queryKey: ["organizations-lookup"] });
        } catch (err) {
          console.error("Auto organization creation error:", err);
        } finally {
          setIsCreatingOrg(false);
        }
      }
    }

    // 1b. If organization exists but user typed a new division name not in DB yet
    if (finalOrgId && !finalDivisionId && divisionInput.trim()) {
      const trimmedDiv = divisionInput.trim();
      const existingDiv = divisions.find(
        (d) => (d.department || d.batch || "").toLowerCase() === trimmedDiv.toLowerCase()
      );
      if (existingDiv) {
        finalDivisionId = existingDiv.id;
      } else {
        try {
          const updateOrgRes = await axiosClient.put(`/organization/${finalOrgId}`, {
            organization_name: orgInput.trim(),
            divisions: [
              ...divisions.map(d => ({
                id: d.id,
                department: d.department,
                course: d.course,
                batch: d.batch
              })),
              { department: trimmedDiv, batch: trimmedDiv }
            ]
          });
          const updatedDivs = updateOrgRes.data?.data?.divisions || [];
          const newDiv = updatedDivs.find(d => d.department === trimmedDiv || d.batch === trimmedDiv);
          if (newDiv) {
            finalDivisionId = newDiv.id;
          }
          queryClient.invalidateQueries({ queryKey: ["organization", finalOrgId] });
        } catch (err) {
          console.error("Auto division creation error:", err);
        }
      }
    }

    // 2. Check if user entered a custom package name not in DB yet
    let finalPackageId = packageSelectedId || null;
    if (!finalPackageId && packageInput.trim()) {
      const trimmedPkg = packageInput.trim();
      const matchedPkg = packages.find(
        (p) => p.title.toLowerCase() === trimmedPkg.toLowerCase()
      );
      if (matchedPkg) {
        finalPackageId = matchedPkg.id;
      } else {
        try {
          const newPkgRes = await axiosClient.post("/packages", {
            title: trimmedPkg,
            duration_days: data.estimated_trip_days ? parseInt(data.estimated_trip_days, 10) : 1,
            duration_nights: data.estimated_trip_days ? Math.max(0, parseInt(data.estimated_trip_days, 10) - 1) : 0,
            is_active: true,
          });
          finalPackageId = newPkgRes.data?.data?.id || null;
          queryClient.invalidateQueries({ queryKey: ["packages"] });
        } catch (err) {
          console.error("Auto package creation error:", err);
        }
      }
    }

    // 3. Destinations auto-creation in DB
    const currentList = [...selectedDestList];
    if (destSearchInput.trim()) {
      const typed = destSearchInput.trim();
      if (!currentList.some((d) => d.name.toLowerCase() === typed.toLowerCase())) {
        const match = allDestinations.find((d) => d.name.toLowerCase() === typed.toLowerCase());
        if (match) {
          currentList.push(match);
        } else {
          currentList.push({ name: typed });
        }
      }
    }

    const finalDestObjects = [];
    let hasCreatedNew = false;
    for (const item of currentList) {
      if (item.id) {
        finalDestObjects.push(item);
      } else {
        try {
          const res = await crmApi.createDestination(item.name);
          const created = res.data;
          if (created && created.id) {
            finalDestObjects.push({ id: created.id, name: created.name });
            hasCreatedNew = true;
          }
        } catch (err) {
          console.error("Error creating destination on submit:", err);
        }
      }
    }

    if (hasCreatedNew) {
      queryClient.invalidateQueries({ queryKey: ["catalog", "destinations"] });
      queryClient.invalidateQueries({ queryKey: ["destinations"] });
      queryClient.invalidateQueries({ queryKey: ["masters", "destinations"] });
    }

    const payload = {
      ...data,
      contact_person: {
        ...data.contact_person,
        email: data.contact_person.email || null,
        designation: data.contact_person.designation || null,
        organization_id: finalOrgId,
      },
      priority_id: data.priority_id || null,
      trip_type_id: data.trip_type_id || null,
      package_id: finalPackageId,
      organization_division_id: finalDivisionId,
      budget: data.budget ? parseFloat(data.budget) : null,
      travel_start_date: data.travel_start_date || null,
      travel_end_date: data.travel_end_date || null,
      expected_travel_date: data.expected_travel_date || null,
      estimated_trip_days: data.estimated_trip_days ? parseInt(data.estimated_trip_days, 10) : null,
      male_count: data.male_count || 0,
      female_count: data.female_count || 0,
      faculty_count: data.faculty_count || 0,
      destinations: finalDestObjects.filter(d => !!d.id).map((d) => ({
        destination_id: d.id,
        priority: "High",
      })),
      notes: data.notes || null,
    };
    
    onSubmit(payload, () => {
      reset();
      setDestSearchInput("");
      setSelectedDestList([]);
      setOrgInput("");
      setOrgSelectedId("");
      setDivisionInput("");
      setPackageInput("");
      setPackageSelectedId("");
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
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl relative flex flex-col z-10 animate-in scale-in duration-200 select-none">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <h2 className="text-base font-bold text-slate-800">Intake New Sales Lead</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors focus:outline-none"
          >
            <X size={16} />
          </button>
        </div>

        {/* Scrollable Form Body */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="flex-1 overflow-y-auto p-6 space-y-5">
          
          {/* Section 1: Customer & Trip Context */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Customer & Group Context</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Customer Name *</label>
                <input
                  type="text"
                  placeholder="e.g. Sanjay Kumar"
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.contact_person?.name ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                  }`}
                  {...register("contact_person.name")}
                />
                {errors.contact_person?.name && (
                  <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.contact_person.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Mobile Phone *</label>
                <input
                  type="text"
                  placeholder="e.g. +91 98765 43210"
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.contact_person?.phone ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                  }`}
                  {...register("contact_person.phone")}
                />
                {errors.contact_person?.phone && (
                  <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.contact_person.phone.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Email Address</label>
                <input
                  type="email"
                  placeholder="e.g. sanjay@example.com"
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.contact_person?.email ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                  }`}
                  {...register("contact_person.email")}
                />
                {errors.contact_person?.email && (
                  <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.contact_person.email.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Trip Type (Category)</label>
                <select
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("trip_type_id")}
                >
                  <option value="">Select trip type (Family, College, Corporate...)</option>
                  {tripTypes.map((tt) => (
                    <option key={tt.id} value={tt.id}>{tt.name}</option>
                  ))}
                </select>
              </div>

              <div className="relative">
                <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                  <span>Organization / Institution</span>
                  {orgSelectedId ? (
                    <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100 flex items-center">
                      <Building size={9} className="mr-0.5" /> Registered DB Org
                    </span>
                  ) : orgInput.trim() ? (
                    <span className="text-[10px] text-blue-600 font-bold bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100 flex items-center">
                      <Plus size={9} className="mr-0.5" /> New Org (Will save in DB)
                    </span>
                  ) : selectedTripType ? (
                    <span className="text-[10px] text-blue-600 font-bold bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">
                      {selectedTripType.name} Context
                    </span>
                  ) : null}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Type or select Organization / College..."
                    value={orgInput}
                    onChange={(e) => {
                      const val = e.target.value;
                      setOrgInput(val);
                      setShowOrgMenu(true);
                      const match = organizations.find((o) => o.name.toLowerCase() === val.trim().toLowerCase());
                      setOrgSelectedId(match ? match.id : "");
                      setValue("contact_person.organization_id", match ? match.id : "");
                    }}
                    onFocus={() => setShowOrgMenu(true)}
                    className="w-full pl-3 pr-8 py-2 border border-slate-250 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-700"
                  />
                  <button
                    type="button"
                    onClick={() => setShowOrgMenu((prev) => !prev)}
                    className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600"
                  >
                    <ChevronDown size={14} />
                  </button>
                </div>

                {showOrgMenu && (
                  <div className="absolute z-30 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    <div
                      className="px-3 py-1.5 text-xs text-slate-500 hover:bg-slate-50 cursor-pointer font-semibold"
                      onClick={() => {
                        setOrgInput("");
                        setOrgSelectedId("");
                        setValue("contact_person.organization_id", "");
                        setShowOrgMenu(false);
                      }}
                    >
                      None (Individual / Direct)
                    </div>
                    {organizations
                      .filter((o) => o.name.toLowerCase().includes(orgInput.toLowerCase()))
                      .map((o) => (
                        <div
                          key={o.id}
                          className="px-3 py-1.5 text-xs text-slate-700 hover:bg-blue-50 hover:text-blue-700 cursor-pointer font-semibold flex items-center justify-between"
                          onClick={() => {
                            setOrgInput(o.name);
                            setOrgSelectedId(o.id);
                            setValue("contact_person.organization_id", o.id);
                            setShowOrgMenu(false);
                          }}
                        >
                          <span>{o.name}</span>
                          <span className="text-[9px] text-slate-400 font-normal">Registered Org</span>
                        </div>
                      ))}
                    {orgInput.trim() && !organizations.some((o) => o.name.toLowerCase() === orgInput.trim().toLowerCase()) && (
                      <div
                        className="px-3 py-2 text-xs text-blue-600 bg-blue-50/70 hover:bg-blue-100 cursor-pointer font-bold border-t border-slate-100 flex items-center space-x-1"
                        onClick={() => setShowOrgMenu(false)}
                      >
                        <Plus size={12} />
                        <span>Add &quot;{orgInput.trim()}&quot; as New Organization in DB</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="relative">
                <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                  <span>Organization Division / Batch</span>
                  {watch("organization_division_id") ? (
                    <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100 flex items-center">
                      <Building size={9} className="mr-0.5" /> Registered Division
                    </span>
                  ) : divisionInput.trim() ? (
                    <span className="text-[10px] text-blue-600 font-bold bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100 flex items-center">
                      <Plus size={9} className="mr-0.5" /> New Batch (Will save in DB)
                    </span>
                  ) : null}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder={orgSelectedId || orgInput.trim() ? "Select or type Batch / Department..." : "Select Organization first..."}
                    disabled={!orgSelectedId && !orgInput.trim()}
                    value={divisionInput}
                    onChange={(e) => {
                      const val = e.target.value;
                      setDivisionInput(val);
                      setShowDivMenu(true);
                      const match = divisions.find(
                        (d) => (d.department || d.batch || "").toLowerCase() === val.trim().toLowerCase()
                      );
                      setValue("organization_division_id", match ? match.id : "");
                    }}
                    onFocus={() => setShowDivMenu(true)}
                    className="w-full pl-3 pr-8 py-2 border border-slate-250 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    type="button"
                    onClick={() => setShowDivMenu((prev) => !prev)}
                    className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600"
                  >
                    <ChevronDown size={14} />
                  </button>
                </div>

                {showDivMenu && (
                  <div className="absolute z-30 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    <div
                      className="px-3 py-1.5 text-xs text-slate-500 hover:bg-slate-50 cursor-pointer font-semibold"
                      onClick={() => {
                        setDivisionInput("");
                        setValue("organization_division_id", "");
                        setShowDivMenu(false);
                      }}
                    >
                      None (General / Direct)
                    </div>
                    {divisions
                      .filter((d) => {
                        const labelStr = `${d.course || ""} ${d.department || ""} ${d.batch || ""}`.toLowerCase();
                        return labelStr.includes(divisionInput.toLowerCase());
                      })
                      .map((d) => {
                        const labelText = `${d.course ? `${d.course} ` : ""}${d.department ? `(${d.department}) ` : ""}${d.batch ? `- Batch ${d.batch}` : ""}`;
                        return (
                          <div
                            key={d.id}
                            className="px-3 py-1.5 text-xs text-slate-700 hover:bg-blue-50 hover:text-blue-700 cursor-pointer font-semibold flex items-center justify-between"
                            onClick={() => {
                              setDivisionInput(labelText);
                              setValue("organization_division_id", d.id);
                              setShowDivMenu(false);
                            }}
                          >
                            <span>{labelText}</span>
                            <span className="text-[9px] text-slate-400 font-normal">Registered Division</span>
                          </div>
                        );
                      })}
                    {divisionInput.trim() && !divisions.some((d) => (d.department || d.batch || "").toLowerCase() === divisionInput.trim().toLowerCase()) && (
                      <div
                        className="px-3 py-2 text-xs text-blue-600 bg-blue-50/70 hover:bg-blue-100 cursor-pointer font-bold border-t border-slate-100 flex items-center space-x-1"
                        onClick={() => setShowDivMenu(false)}
                      >
                        <Plus size={12} />
                        <span>Add &quot;{divisionInput.trim()}&quot; as New Division/Batch in DB</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Section 2: Requirements */}
          <div className="space-y-3 pt-3 border-t border-slate-100">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Trip Specifications & Package</h3>
            
            {/* Source, Priority, Package */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Lead Source *</label>
                <select
                  className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    errors.lead_source_id ? "border-red-300 focus:ring-red-500" : "border-slate-200"
                  }`}
                  {...register("lead_source_id")}
                >
                  <option value="">Select source</option>
                  {sources.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
                {errors.lead_source_id && (
                  <p className="mt-1 text-[10px] text-red-600 font-semibold">{errors.lead_source_id.message}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Priority</label>
                <select
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("priority_id")}
                >
                  <option value="">Select priority</option>
                  {priorities.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              <div className="relative">
                <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                  <span>Package Template / Custom</span>
                  {packageSelectedId ? (
                    <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100 flex items-center">
                      <Package size={9} className="mr-0.5" /> Template
                    </span>
                  ) : packageInput.trim() ? (
                    <span className="text-[10px] text-amber-700 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-100">
                      Custom Request
                    </span>
                  ) : null}
                </label>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Select template or type custom package..."
                    value={packageInput}
                    onChange={(e) => {
                      const val = e.target.value;
                      setPackageInput(val);
                      setShowPackageMenu(true);
                      const match = packages.find((p) => p.title.toLowerCase() === val.trim().toLowerCase());
                      setPackageSelectedId(match ? match.id : "");
                      setValue("package_id", match ? match.id : "");
                    }}
                    onFocus={() => setShowPackageMenu(true)}
                    className="w-full pl-3 pr-8 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-700"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPackageMenu((prev) => !prev)}
                    className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600"
                  >
                    <ChevronDown size={14} />
                  </button>
                </div>

                {showPackageMenu && (
                  <div className="absolute z-30 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    <div
                      className="px-3 py-1.5 text-xs text-slate-500 hover:bg-slate-50 cursor-pointer font-semibold"
                      onClick={() => {
                        setPackageInput("");
                        setPackageSelectedId("");
                        setValue("package_id", "");
                        setShowPackageMenu(false);
                      }}
                    >
                      Custom Package / None
                    </div>
                    {packages
                      .filter((pkg) => pkg.title.toLowerCase().includes(packageInput.toLowerCase()))
                      .map((pkg) => (
                        <div
                          key={pkg.id}
                          className="px-3 py-1.5 text-xs text-slate-700 hover:bg-blue-50 hover:text-blue-700 cursor-pointer font-semibold flex items-center justify-between"
                          onClick={() => {
                            setPackageInput(pkg.title);
                            setPackageSelectedId(pkg.id);
                            setValue("package_id", pkg.id);
                            setShowPackageMenu(false);
                          }}
                        >
                          <span>{pkg.title}</span>
                          <span className="text-[9px] text-slate-400 font-mono">
                            {pkg.duration_nights}N/{pkg.duration_days}D
                          </span>
                        </div>
                      ))}
                  </div>
                )}
              </div>
            </div>

            {/* Counts, Budget */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Total Traveler Count *</label>
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
                <label className="block text-xs font-semibold text-slate-600 mb-1">Expected Budget (INR)</label>
                <input
                  type="number"
                  placeholder="e.g. 50000"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("budget")}
                />
              </div>
            </div>

            {/* Demographics */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Male Count</label>
                <input
                  type="number"
                  min="0"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("male_count")}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Female Count</label>
                <input
                  type="number"
                  min="0"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("female_count")}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Faculty Count</label>
                <input
                  type="number"
                  min="0"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("faculty_count")}
                />
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Start Date</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("travel_start_date")}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">End Date</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("travel_end_date")}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Alt Travel Date</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("expected_travel_date")}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Duration (Days)</label>
                <input
                  type="number"
                  min="1"
                  placeholder="e.g. 3"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  {...register("estimated_trip_days")}
                />
              </div>
            </div>

            {/* Target Destinations (DB-driven Combobox + Auto Add) */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-600 flex items-center justify-between">
                <span>Target Destinations</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  {selectedDestList.length} destination{selectedDestList.length !== 1 ? "s" : ""} selected
                </span>
              </label>

              {/* Selected Tag Badges */}
              {selectedDestList.length > 0 && (
                <div className="flex flex-wrap gap-1.5 p-2 bg-slate-50 border border-slate-200 rounded-lg">
                  {selectedDestList.map((d, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-bold bg-blue-600 text-white shadow-xs"
                    >
                      <span>{d.name}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveDestObj(d.name)}
                        className="hover:text-blue-200 transition-colors ml-1 focus:outline-none"
                      >
                        <X size={12} />
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Input + Combobox Menu */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Type destination name or click dropdown..."
                  value={destSearchInput}
                  onChange={(e) => {
                    setDestSearchInput(e.target.value);
                    setShowDestMenu(true);
                  }}
                  onFocus={() => setShowDestMenu(true)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && destSearchInput.trim()) {
                      e.preventDefault();
                      const match = allDestinations.find(
                        (d) => d.name.toLowerCase() === destSearchInput.trim().toLowerCase()
                      );
                      if (match) {
                        handleAddDestObj(match);
                      } else {
                        handleCreateNewDestination(destSearchInput.trim());
                      }
                    }
                  }}
                  className="w-full pl-3 pr-8 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold text-slate-700"
                />
                <button
                  type="button"
                  onClick={() => setShowDestMenu((prev) => !prev)}
                  className="absolute right-2 top-2.5 text-slate-400 hover:text-slate-600"
                >
                  <ChevronDown size={14} />
                </button>

                {showDestMenu && (
                  <div className="absolute z-30 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    {allDestinations
                      .filter((d) => d.name.toLowerCase().includes(destSearchInput.toLowerCase()))
                      .map((d) => {
                        const isSelected = selectedDestList.some((s) => s.name.toLowerCase() === d.name.toLowerCase());
                        return (
                          <div
                            key={d.id}
                            className={`px-3 py-1.5 text-xs cursor-pointer font-semibold flex items-center justify-between transition-colors ${
                              isSelected
                                ? "bg-blue-50 text-blue-700 font-bold"
                                : "text-slate-700 hover:bg-slate-50"
                            }`}
                            onClick={() => {
                              if (isSelected) {
                                handleRemoveDestObj(d.name);
                              } else {
                                handleAddDestObj(d);
                              }
                            }}
                          >
                            <span>{d.name}</span>
                            <span className="text-[9px] text-slate-400 font-mono">
                              {isSelected ? "Selected ✓" : "Master DB"}
                            </span>
                          </div>
                        );
                      })}
                    {destSearchInput.trim() &&
                      !allDestinations.some((d) => d.name.toLowerCase() === destSearchInput.trim().toLowerCase()) && (
                        <div
                          className="px-3 py-2 text-xs text-blue-600 bg-blue-50/70 hover:bg-blue-100 cursor-pointer font-bold border-t border-slate-100 flex items-center space-x-1"
                          onClick={() => handleCreateNewDestination(destSearchInput.trim())}
                        >
                          <Plus size={12} />
                          <span>Add &quot;{destSearchInput.trim()}&quot; to Master DB Destinations</span>
                        </div>
                      )}
                  </div>
                )}
              </div>
              <p className="text-[10px] text-slate-400 font-medium">
                Select destinations from master database. Typed new destinations will be automatically created in the database.
              </p>
            </div>
          </div>

          {/* Section 3: Notes */}
          <div className="space-y-2 pt-3 border-t border-slate-100">
            <label className="block text-xs font-semibold text-slate-600">Requirement Notes / Special Requests</label>
            <textarea
              rows="3"
              placeholder="e.g. Prefers 4-star hotels, vegetarian meal options, or customizable itineraries."
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              {...register("notes")}
            />
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
                  <span>Submitting...</span>
                </>
              ) : (
                "Save Lead File"
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}

export default CreateLeadModal;
