import React, { useState, useEffect } from "react";
import { X, Plus, Trash2, Save, Loader2, Mail, Phone, Globe, MapPin, User, UserCheck } from "lucide-react";
import { useOrganizationTypes } from "../hooks/useOrganization";

export function OrganizationFormModal({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
  editingItem = null,
}) {
  const isEdit = !!editingItem;
  const { data: typesRes } = useOrganizationTypes();
  const orgTypes = typesRes?.data || [];

  // Form states
  const [name, setName] = useState("");
  const [typeId, setTypeId] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");
  const [contacts, setContacts] = useState([]);
  const [divisions, setDivisions] = useState([]);

  // Sync state on edit load
  useEffect(() => {
    if (editingItem) {
      setName(editingItem.organization_name || "");
      setTypeId(editingItem.organization_type_id || "");
      setAddress(editingItem.address || "");
      setCity(editingItem.city || "");
      setState(editingItem.state || "");
      setPhone(editingItem.phone || "");
      setEmail(editingItem.email || "");
      setWebsite(editingItem.website || "");
      setNotes(editingItem.notes || "");
      setContacts(editingItem.contact_persons || []);
      setDivisions(editingItem.divisions || []);
    } else {
      setName("");
      setTypeId("");
      setAddress("");
      setCity("");
      setState("");
      setPhone("");
      setEmail("");
      setWebsite("");
      setNotes("");
      setContacts([]);
      setDivisions([]);
    }
  }, [editingItem, isOpen]);

  // Handlers for dynamic contact person list
  const handleAddContact = () => {
    setContacts((prev) => [
      ...prev,
      {
        id: undefined,
        name: "",
        designation: "",
        phone: "",
        alternate_phone: "",
        email: "",
        is_primary: prev.length === 0,
        preferred_contact_method: "Phone",
        notes: "",
        is_active: true,
      },
    ]);
  };

  const handleUpdateContactField = (index, field, value) => {
    setContacts((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], [field]: value };
      if (field === "is_primary" && value === true) {
        return copy.map((c, idx) => (idx === index ? c : { ...c, is_primary: false }));
      }
      return copy;
    });
  };

  const handleRemoveContact = (index) => {
    setContacts((prev) => prev.filter((_, idx) => idx !== index));
  };

  // Handlers for dynamic division/department list
  const handleAddDivision = () => {
    setDivisions((prev) => [
      ...prev,
      {
        id: undefined,
        department: "",
        course: "",
        section: "",
        year: "",
        semester: "",
        batch: "",
      },
    ]);
  };

  const handleUpdateDivisionField = (index, field, value) => {
    setDivisions((prev) => {
      const copy = [...prev];
      copy[index] = { ...copy[index], [field]: value };
      return copy;
    });
  };

  const handleRemoveDivision = (index) => {
    setDivisions((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();

    const clean = (val) => (val && val.trim() !== "" ? val.trim() : null);

    const payload = {
      organization_name: name.trim(),
      organization_type_id: typeId || null,
      address: clean(address),
      city: clean(city),
      state: clean(state),
      phone: clean(phone),
      email: clean(email),
      website: clean(website),
      notes: clean(notes),
      is_active: true,
      divisions: divisions.map((d) => ({
        id: d.id || null,
        department: clean(d.department),
        course: clean(d.course),
        section: clean(d.section),
        year: clean(d.year),
        semester: clean(d.semester),
        batch: clean(d.batch),
      })),
      contact_persons: contacts.map((c) => ({
        id: c.id || null,
        name: c.name.trim(),
        designation: clean(c.designation),
        phone: c.phone.trim(),
        alternate_phone: clean(c.alternate_phone),
        email: clean(c.email),
        is_primary: !!c.is_primary,
        preferred_contact_method: clean(c.preferred_contact_method),
        notes: clean(c.notes),
        is_active: !!c.is_active,
      })),
    };

    onSubmit(payload);
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
        <div className="w-screen max-w-2xl bg-white border-l border-slate-200 shadow-2xl flex flex-col justify-between">
          
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50 shrink-0">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                {isEdit ? "Update Registry" : "New Registration"}
              </span>
              <h2 className="text-base font-bold text-slate-800 tracking-tight">
                {isEdit ? `Edit Customer Org: ${editingItem.organization_name}` : "Register Customer Org"}
              </h2>
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
            id="org-form"
            onSubmit={handleFormSubmit}
            className="flex-1 overflow-y-auto p-6 space-y-5 text-xs font-semibold text-slate-600"
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-700 font-bold mb-1">Company / Institution Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Kochi University or Wipro Tech"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">Organization Category *</label>
                <select
                  required
                  value={typeId}
                  onChange={(e) => setTypeId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Category</option>
                  {orgTypes.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-slate-700 font-bold mb-1">
                  <Phone size={10} className="inline mr-1" /> Mobile / Phone
                </label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="e.g. +91 484 221100"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">
                  <Mail size={10} className="inline mr-1" /> Office Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. contact@college.edu"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">
                  <Globe size={10} className="inline mr-1" /> Web Domain
                </label>
                <input
                  type="url"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  placeholder="https://www.college.edu"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <label className="block text-slate-700 font-bold mb-1">
                  <MapPin size={10} className="inline mr-1" /> Address Location
                </label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Street and landmark details"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-700 font-bold mb-1">City</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="Kochi"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 font-bold mb-1">State</label>
                  <input
                    type="text"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="Kerala"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-slate-700 font-bold mb-1">Corporate Notes / Background</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Details of student strength, prior bookings history..."
                rows={2}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Nested contact list */}
            <div className="pt-4 border-t border-slate-200 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-1">
                <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Assigned Contact Persons & Staff
                </h4>
                <button
                  type="button"
                  onClick={handleAddContact}
                  className="px-2 py-1 bg-blue-55 hover:bg-blue-100 text-blue-700 rounded-md font-bold transition-all"
                >
                  + Add Contact
                </button>
              </div>

              {contacts.length === 0 ? (
                <p className="text-slate-400 font-bold text-center py-4">No contact managers assigned yet.</p>
              ) : (
                <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
                  {contacts.map((c, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl relative group space-y-2">
                      <button
                        type="button"
                        onClick={() => handleRemoveContact(idx)}
                        className="absolute top-2 right-2 p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-slate-200/50"
                      >
                        <Trash2 size={12} />
                      </button>

                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Name *</label>
                          <input
                            type="text"
                            required
                            value={c.name}
                            onChange={(e) => handleUpdateContactField(idx, "name", e.target.value)}
                            placeholder="Full Name"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Designation</label>
                          <input
                            type="text"
                            value={c.designation || ""}
                            onChange={(e) => handleUpdateContactField(idx, "designation", e.target.value)}
                            placeholder="e.g. HOD / HR Manager"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div className="flex items-end pb-1.5 space-x-1">
                          <input
                            type="checkbox"
                            id={`contact-primary-${idx}`}
                            checked={!!c.is_primary}
                            onChange={(e) => handleUpdateContactField(idx, "is_primary", e.target.checked)}
                            className="w-3.5 h-3.5 text-blue-650 rounded border-slate-300"
                          />
                          <label htmlFor={`contact-primary-${idx}`} className="text-[10px] font-bold text-slate-650 flex items-center">
                            <UserCheck size={10} className="mr-0.5 text-blue-600" />
                            <span>Primary</span>
                          </label>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Mobile Phone *</label>
                          <input
                            type="text"
                            required
                            value={c.phone}
                            onChange={(e) => handleUpdateContactField(idx, "phone", e.target.value)}
                            placeholder="+91 99..."
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Email Address</label>
                          <input
                            type="email"
                            value={c.email || ""}
                            onChange={(e) => handleUpdateContactField(idx, "email", e.target.value)}
                            placeholder="name@college.edu"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Nested divisions list */}
            <div className="pt-4 border-t border-slate-200 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-1">
                <div>
                  <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Academic Divisions & Department Batches
                  </h4>
                  <p className="text-[9px] text-slate-400 font-medium">Map courses, departments & batch years for student IV tours</p>
                </div>
                <button
                  type="button"
                  onClick={handleAddDivision}
                  className="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-md font-bold transition-all text-xs"
                >
                  + Add Division
                </button>
              </div>

              {divisions.length === 0 ? (
                <p className="text-slate-400 font-medium text-[11px] text-center py-3 italic">
                  No department divisions or batches configured.
                </p>
              ) : (
                <div className="space-y-3 max-h-56 overflow-y-auto pr-1">
                  {divisions.map((d, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl relative group space-y-2">
                      <button
                        type="button"
                        onClick={() => handleRemoveDivision(idx)}
                        className="absolute top-2 right-2 p-1 rounded text-slate-400 hover:text-rose-600 hover:bg-slate-200/50"
                      >
                        <Trash2 size={12} />
                      </button>

                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Department</label>
                          <input
                            type="text"
                            value={d.department || ""}
                            onChange={(e) => handleUpdateDivisionField(idx, "department", e.target.value)}
                            placeholder="e.g. Computer Science"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Course / Degree</label>
                          <input
                            type="text"
                            value={d.course || ""}
                            onChange={(e) => handleUpdateDivisionField(idx, "course", e.target.value)}
                            placeholder="e.g. B.Tech / MBA"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Batch / Year</label>
                          <input
                            type="text"
                            value={d.batch || ""}
                            onChange={(e) => handleUpdateDivisionField(idx, "batch", e.target.value)}
                            placeholder="e.g. 2023-2027"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-2">
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Section</label>
                          <input
                            type="text"
                            value={d.section || ""}
                            onChange={(e) => handleUpdateDivisionField(idx, "section", e.target.value)}
                            placeholder="e.g. Section A"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Year Level</label>
                          <input
                            type="text"
                            value={d.year || ""}
                            onChange={(e) => handleUpdateDivisionField(idx, "year", e.target.value)}
                            placeholder="e.g. 3rd Year"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] text-slate-500 font-bold mb-0.5">Semester</label>
                          <input
                            type="text"
                            value={d.semester || ""}
                            onChange={(e) => handleUpdateDivisionField(idx, "semester", e.target.value)}
                            placeholder="e.g. 6th Sem"
                            className="w-full px-2 py-1 border border-slate-200 rounded text-xs"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </form>

          {/* Footer Actions */}
          <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-end space-x-3 shrink-0">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-650 bg-white hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="org-form"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/10 flex items-center"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={14} />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save size={14} className="mr-1.5" />
                  <span>{isEdit ? "Update Registry" : "Register Org"}</span>
                </>
              )}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
export default OrganizationFormModal;
