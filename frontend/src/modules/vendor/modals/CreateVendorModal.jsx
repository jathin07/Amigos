import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { X, Loader2, Store, Save, CheckCircle } from "lucide-react";
import vendorApi from "../services/vendorApi";

export function CreateVendorModal({ isOpen, onClose, onSubmit, isSubmitting }) {
  const [vendorName, setVendorName] = useState("");
  const [vendorTypeId, setVendorTypeId] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [contactPerson, setContactPerson] = useState("");
  const [serviceArea, setServiceArea] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [gstNumber, setGstNumber] = useState("");
  const [bankAccountName, setBankAccountName] = useState("");
  const [bankAccountNumber, setBankAccountNumber] = useState("");
  const [ifsc, setIfsc] = useState("");
  const [notes, setNotes] = useState("");

  // Get vendor types lookup
  const { data: typesLookup, isLoading: isTypesLoading } = useQuery({
    queryKey: ["lookups", "vendor-types"],
    queryFn: () => vendorApi.getVendorTypes(),
    enabled: isOpen,
  });

  const vendorTypes = typesLookup?.data || [];

  // Reset state on open
  useEffect(() => {
    if (isOpen) {
      setVendorName("");
      setVendorTypeId("");
      setPhone("");
      setEmail("");
      setContactPerson("");
      setServiceArea("");
      setCity("");
      setState("");
      setGstNumber("");
      setBankAccountName("");
      setBankAccountNumber("");
      setIfsc("");
      setNotes("");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleFormSubmit = (e) => {
    e.preventDefault();

    // Helper to sanitize empty string fields to null for validation safety
    const clean = (val) => (val && val.trim() !== "" ? val.trim() : null);

    const payload = {
      vendor_name: vendorName.trim(),
      vendor_type_id: vendorTypeId,
      phone: phone.trim(),
      email: clean(email),
      contact_person: clean(contactPerson),
      service_area: clean(serviceArea),
      city: clean(city),
      state: clean(state),
      gst_number: clean(gstNumber),
      bank_account_name: clean(bankAccountName),
      bank_account_number: clean(bankAccountNumber),
      ifsc: clean(ifsc),
      notes: clean(notes),
      is_active: true
    };

    onSubmit(payload);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 select-none">
      <div className="w-full max-w-2xl bg-white border border-slate-100 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2 text-slate-800">
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
              <Store size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold">Register New Supplier / Vendor</h2>
              <p className="text-[10px] text-slate-400 font-medium">Add operations partner to directory</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleFormSubmit} className="flex-1 overflow-y-auto p-6 space-y-5 text-xs font-semibold text-slate-700">
          
          {/* Main Info Section */}
          <div className="space-y-4">
            <h3 className="text-[10px] uppercase tracking-wider text-slate-400 font-bold border-b border-slate-100 pb-1">Supplier Core Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Company / Vendor Name *</label>
                <input
                  type="text"
                  required
                  value={vendorName}
                  onChange={(e) => setVendorName(e.target.value)}
                  placeholder="e.g. Grand Palace Hotel, Kerala Travels"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Vendor Type *</label>
                {isTypesLoading ? (
                  <div className="h-9 border border-slate-200 rounded-lg flex items-center justify-center bg-slate-50">
                    <Loader2 className="animate-spin text-blue-600" size={14} />
                  </div>
                ) : (
                  <select
                    required
                    value={vendorTypeId}
                    onChange={(e) => setVendorTypeId(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
                  >
                    <option value="">Select Service Area</option>
                    {vendorTypes.map((type) => (
                      <option key={type.id} value={type.id}>
                        {type.name}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Contact Person Name</label>
                <input
                  type="text"
                  value={contactPerson}
                  onChange={(e) => setContactPerson(e.target.value)}
                  placeholder="e.g. John Doe (Manager)"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Official Mobile *</label>
                <input
                  type="text"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="e.g. +91 9988220011"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Official Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. accounts@hotel.com"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Location & Tax Info Section */}
          <div className="space-y-4">
            <h3 className="text-[10px] uppercase tracking-wider text-slate-400 font-bold border-b border-slate-100 pb-1">Taxation & Service Territory</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Service Area / Coverage</label>
                <input
                  type="text"
                  value={serviceArea}
                  onChange={(e) => setServiceArea(e.target.value)}
                  placeholder="e.g. South India, Kochi Local, Munnar Hills"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">City</label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="e.g. Kochi"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">State</label>
                <input
                  type="text"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  placeholder="e.g. Kerala"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">GST Identification Number (GSTIN)</label>
                <input
                  type="text"
                  value={gstNumber}
                  onChange={(e) => setGstNumber(e.target.value)}
                  placeholder="e.g. 32AAAAA1111A1Z1"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Complete Office Address</label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Street name, landmark, PIN"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Bank Settlement Details Section */}
          <div className="space-y-4">
            <h3 className="text-[10px] uppercase tracking-wider text-slate-400 font-bold border-b border-slate-100 pb-1">Bank Settlement Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Beneficiary Account Name</label>
                <input
                  type="text"
                  value={bankAccountName}
                  onChange={(e) => setBankAccountName(e.target.value)}
                  placeholder="Beneficiary name on bank records"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Account Number</label>
                <input
                  type="text"
                  value={bankAccountNumber}
                  onChange={(e) => setBankAccountNumber(e.target.value)}
                  placeholder="10-18 digit account number"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">IFSC / Routing Code</label>
                <input
                  type="text"
                  value={ifsc}
                  onChange={(e) => setIfsc(e.target.value)}
                  placeholder="e.g. SBIN0001234"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                />
              </div>
            </div>
          </div>

          {/* Additional Notes */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 uppercase mb-1">Internal Operations Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record notes on contract validity, seasonal price revisions, credit periods..."
              rows={2}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Action CTAs */}
          <div className="pt-2 flex items-center justify-end space-x-2 shrink-0 border-t border-slate-100 mt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-500 text-xs font-bold rounded-lg transition-colors focus:outline-none disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-450 text-white text-xs font-bold rounded-lg shadow-md shadow-blue-500/10 transition-colors focus:outline-none disabled:opacity-80"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin" size={14} />
                  <span>Registering Partner...</span>
                </>
              ) : (
                <>
                  <Save size={14} />
                  <span>Register Vendor</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
