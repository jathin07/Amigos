import React, { useState, useEffect } from "react";
import { X, Loader2, User } from "lucide-react";

export function AddEditTravelerDrawer({ isOpen, onClose, onSubmit, isPending, traveler = null }) {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "",
    id_proof_type: "",
    id_proof_number: "",
    emergency_contact: "",
    special_requirements: "",
    is_group_leader: false,
  });

  useEffect(() => {
    if (traveler) {
      setFormData({
        name: traveler.name || "",
        age: traveler.age !== null && traveler.age !== undefined ? String(traveler.age) : "",
        gender: traveler.gender || "",
        id_proof_type: traveler.id_proof_type || "",
        id_proof_number: traveler.id_proof_number || "",
        emergency_contact: traveler.emergency_contact || "",
        special_requirements: traveler.special_requirements || "",
        is_group_leader: !!traveler.is_group_leader,
      });
    } else {
      setFormData({
        name: "",
        age: "",
        gender: "",
        id_proof_type: "",
        id_proof_number: "",
        emergency_contact: "",
        special_requirements: "",
        is_group_leader: false,
      });
    }
  }, [traveler, isOpen]);

  if (!isOpen) return null;

  const handleChange = (key, val) => {
    setFormData((prev) => ({ ...prev, [key]: val }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert("Name is required.");
      return;
    }

    // Validation for Aadhaar format
    if (formData.id_proof_type === "Aadhaar" && formData.id_proof_number) {
      const aadhaarPattern = /^[0-9]{4}-[0-9]{4}-[0-9]{4}$/;
      if (!aadhaarPattern.test(formData.id_proof_number)) {
        alert("Aadhaar number must be in the format: XXXX-XXXX-XXXX");
        return;
      }
    }

    const payload = {
      name: formData.name.trim(),
      age: formData.age ? parseInt(formData.age, 10) : null,
      gender: formData.gender || null,
      id_proof_type: formData.id_proof_type || null,
      id_proof_number: formData.id_proof_number || null,
      emergency_contact: formData.emergency_contact || null,
      special_requirements: formData.special_requirements || null,
      is_group_leader: formData.is_group_leader,
    };

    if (traveler?.id) {
      onSubmit({ travelerId: traveler.id, ...payload });
    } else {
      onSubmit(payload);
    }
  };

  return (
    <>
      {/* Backdrop overlay */}
      <div className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs transition-opacity" onClick={onClose} />

      {/* Drawer panel */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white border-l border-slate-200 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 shrink-0">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <User size={18} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">
                {traveler ? "Edit Traveler Details" : "Add Traveler to Manifest"}
              </h3>
              <p className="text-[10px] font-semibold text-slate-400">Update passenger specs and government proof records</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-colors">
            <X size={16} />
          </button>
        </div>

        {/* Scrollable form body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5 space-y-4">
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Full Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Rahul Sharma"
              value={formData.name}
              onChange={(e) => handleChange("name", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Age</label>
              <input
                type="number"
                min="0"
                max="120"
                placeholder="e.g. 28"
                value={formData.age}
                onChange={(e) => handleChange("age", e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => handleChange("gender", e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
              >
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">ID Proof Type</label>
              <select
                value={formData.id_proof_type}
                onChange={(e) => handleChange("id_proof_type", e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
              >
                <option value="">None</option>
                <option value="Aadhaar">Aadhaar</option>
                <option value="Passport">Passport</option>
                <option value="Voter ID">Voter ID</option>
                <option value="PAN">PAN</option>
                <option value="Driving License">Driving License</option>
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">ID Proof Number</label>
              <input
                type="text"
                placeholder={formData.id_proof_type === "Aadhaar" ? "XXXX-XXXX-XXXX" : "ID reference number"}
                value={formData.id_proof_number}
                onChange={(e) => handleChange("id_proof_number", e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Emergency Contact Number</label>
            <input
              type="text"
              placeholder="e.g. +91 9988776655"
              value={formData.emergency_contact}
              onChange={(e) => handleChange("emergency_contact", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
            />
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Special Requirements</label>
            <textarea
              rows="3"
              placeholder="e.g. Wheelchair access needed, veg meal prep, medical condition..."
              value={formData.special_requirements}
              onChange={(e) => handleChange("special_requirements", e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <input
              type="checkbox"
              id="is_group_leader"
              checked={formData.is_group_leader}
              onChange={(e) => handleChange("is_group_leader", e.target.checked)}
              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
            />
            <label htmlFor="is_group_leader" className="text-xs font-bold text-slate-700">
              Designate as Lead Group Traveler
            </label>
          </div>
          <p className="text-[10px] text-slate-400 font-medium">Note: A booking manifest must have exactly one Lead Traveler assigned.</p>

        </form>

        {/* Footer actions */}
        <div className="px-5 py-4 border-t border-slate-100 shrink-0 flex items-center justify-end space-x-2 bg-slate-50">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-600 bg-white hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isPending}
            className="px-5 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-md transition-colors flex items-center space-x-1.5"
          >
            {isPending && <Loader2 className="animate-spin" size={12} />}
            <span>{traveler ? "Update Details" : "Add Traveler"}</span>
          </button>
        </div>

      </div>
    </>
  );
}

export default AddEditTravelerDrawer;
