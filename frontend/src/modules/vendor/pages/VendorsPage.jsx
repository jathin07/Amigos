import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Store,
  Plus,
  Search,
  MapPin,
  Phone,
  Mail,
  CheckCircle,
  AlertCircle,
  Loader2,
  Filter,
  Star,
  Check,
  XCircle,
  StarHalf
} from "lucide-react";
import { useVendors, useCreateVendor, useVerifyVendor } from "../hooks/useVendors";
import { CreateVendorModal } from "../modals/CreateVendorModal";

export function VendorsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Query vendors
  const { data: vendorRes, isLoading, error, refetch } = useVendors({
    page: 1,
    page_size: 100, // Load all for local filtering
  });

  // Mutations
  const createVendorMutation = useCreateVendor();
  const verifyVendorMutation = useVerifyVendor();

  const vendors = vendorRes?.data?.items || [];

  // Filter items
  const filteredVendors = vendors.filter((vendor) => {
    const matchesSearch =
      vendor.vendor_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vendor.contact_person?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vendor.city?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = selectedType === "" || vendor.vendor_type?.code === selectedType;
    
    const matchesStatus =
      selectedStatus === "" ||
      (selectedStatus === "verified" && vendor.is_verified) ||
      (selectedStatus === "unverified" && !vendor.is_verified);

    return matchesSearch && matchesType && matchesStatus;
  });

  const handleCreateSubmit = async (payload) => {
    try {
      await createVendorMutation.mutateAsync(payload);
      setIsCreateOpen(false);
      refetch();
    } catch (err) {
      alert(err?.response?.data?.message || "Failed to register supplier.");
    }
  };

  const handleToggleVerify = async (vendor) => {
    try {
      await verifyVendorMutation.mutateAsync({
        id: vendor.id,
        verify: !vendor.is_verified,
      });
      refetch();
    } catch (err) {
      alert(err?.response?.data?.message || "Failed to update verification status.");
    }
  };

  // Unique list of types present for filtering
  const vendorTypes = Array.from(new Set(vendors.map(v => JSON.stringify(v.vendor_type))))
    .map(str => JSON.parse(str))
    .filter(t => t);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-800 select-none">
      {/* Header and stats */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-850 flex items-center space-x-2">
            <Store className="text-blue-650" size={24} />
            <span>Supplier & Vendor Directory</span>
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            Manage allocations with verified partners across hotels, transport companies, and local guides.
          </p>
        </div>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center justify-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-md shadow-blue-500/10 transition-all focus:outline-none shrink-0"
        >
          <Plus size={14} />
          <span>Register Supplier</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-sm flex flex-col md:flex-row md:items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search suppliers by name, contact, city..."
            className="w-full pl-9 pr-4 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
          />
        </div>

        {/* Filter Type */}
        <div className="flex items-center space-x-2 text-xs">
          <Filter size={12} className="text-slate-400" />
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none font-semibold text-slate-600"
          >
            <option value="">All Services</option>
            {vendorTypes.map((type) => (
              <option key={type.id} value={type.code}>
                {type.name}
              </option>
            ))}
          </select>

          {/* Filter Verification */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-1.5 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none font-semibold text-slate-600"
          >
            <option value="">All Statuses</option>
            <option value="verified">Verified Partners</option>
            <option value="unverified">Unverified Partners</option>
          </select>
        </div>
      </div>

      {/* Vendors List Display */}
      {isLoading ? (
        <div className="py-24 flex flex-col items-center justify-center text-slate-400 text-xs">
          <Loader2 className="animate-spin text-blue-600 mb-2" size={28} />
          <span>Fetching suppliers roster...</span>
        </div>
      ) : error ? (
        <div className="py-24 text-center text-rose-500 text-xs font-bold">
          Failed to load vendors list. Please try again.
        </div>
      ) : filteredVendors.length === 0 ? (
        <div className="py-24 bg-white border border-slate-100 rounded-xl text-center text-slate-400 text-xs font-semibold">
          No registered suppliers match your filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredVendors.map((vendor) => (
            <div
              key={vendor.id}
              className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
            >
              {/* Card top */}
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1 max-w-[70%]">
                    <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-650 text-[9px] font-bold uppercase tracking-wider block w-fit">
                      {vendor.vendor_type?.name || "General Service"}
                    </span>
                    <h3 className="text-sm font-bold text-slate-800 truncate">{vendor.vendor_name}</h3>
                  </div>

                  {/* Verification badge */}
                  <button
                    onClick={() => handleToggleVerify(vendor)}
                    className={`flex items-center space-x-0.5 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase transition-colors select-none ${
                      vendor.is_verified
                        ? "bg-emerald-50 text-emerald-600 hover:bg-rose-50 hover:text-rose-600 hover:content-['Unverify']"
                        : "bg-amber-50 text-amber-600 hover:bg-emerald-50 hover:text-emerald-600"
                    }`}
                    title={vendor.is_verified ? "Click to unverify supplier" : "Click to verify supplier"}
                  >
                    {vendor.is_verified ? (
                      <>
                        <Check size={9} />
                        <span>Verified</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle size={9} />
                        <span>Pending</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Rating stars if active */}
                <div className="flex items-center space-x-0.5">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star
                      key={i}
                      size={11}
                      className={
                        i < (vendor.internal_rating || 3)
                          ? "fill-amber-450 text-amber-450"
                          : "text-slate-200"
                      }
                    />
                  ))}
                  <span className="text-[10px] text-slate-400 font-bold ml-1">
                    {(vendor.internal_rating || 3.0).toFixed(1)} Rating
                  </span>
                </div>

                {/* Contact grid */}
                <div className="pt-2 border-t border-slate-100 space-y-2 text-xs font-semibold text-slate-600">
                  {vendor.contact_person && (
                    <div className="flex items-center space-x-2 text-slate-500">
                      <span className="text-[9px] font-bold text-slate-400 uppercase w-10">Agent:</span>
                      <span className="text-slate-700 font-bold">{vendor.contact_person}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-2">
                    <Phone size={11} className="text-slate-400 shrink-0" />
                    <span>{vendor.phone}</span>
                  </div>
                  {vendor.email && (
                    <div className="flex items-center space-x-2 truncate">
                      <Mail size={11} className="text-slate-400 shrink-0" />
                      <span>{vendor.email}</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-2">
                    <MapPin size={11} className="text-slate-400 shrink-0" />
                    <span>
                      {vendor.city || "Local"}, {vendor.state || "India"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Card bottom details */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] font-bold">
                <span className="text-slate-400 font-bold">
                  GSTIN: <span className="font-mono text-slate-700">{vendor.gst_number || "N/A"}</span>
                </span>
                {vendor.service_area && (
                  <span className="text-slate-500 font-semibold truncate max-w-[60%]">
                    Area: {vendor.service_area}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <CreateVendorModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateSubmit}
        isSubmitting={createVendorMutation.isPending}
      />
    </div>
  );
}
export default VendorsPage;
