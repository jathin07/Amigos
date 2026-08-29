import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useProposalDetail, useCreateProposal, useUpdateProposal } from "../hooks/useProposal";
import { useLeadDetail } from "../../crm/hooks/useLeadDetail";
import proposalApi from "../services/proposalApi";
import { 
  Compass, 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Save, 
  Sparkles, 
  Loader2, 
  DollarSign, 
  MapPin, 
  Home as HomeIcon, 
  Plane, 
  Coffee,
  HelpCircle,
  AlertTriangle
} from "lucide-react";

export function ProposalBuilderPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const leadId = searchParams.get("lead_id");

  // Mode: isEdit if we have route ID parameter
  const isEdit = !!id;

  // Queries
  const { data: proposalResponse, isLoading: isProposalLoading } = useProposalDetail(id);
  const proposal = proposalResponse?.data;

  // Resolve lead ID from proposal if in edit mode
  const activeLeadId = isEdit ? proposal?.lead_id : leadId;
  const { data: leadResponse, isLoading: isLeadLoading } = useLeadDetail(activeLeadId);
  const lead = leadResponse?.data;

  // Catalog lookups
  const { data: destinationsLookup } = useQuery({
    queryKey: ["catalog", "destinations"],
    queryFn: () => proposalApi.getDestinations(),
  });
  const destinations = destinationsLookup?.data?.items || [];

  // State Management
  const [proposalTitle, setProposalTitle] = useState("");
  const [validUntil, setValidUntil] = useState("");
  const [internalNotes, setInternalNotes] = useState("");
  const [markupPercent, setMarkupPercent] = useState(15);
  const [days, setDays] = useState([
    {
      title: "Arrival and Check-in",
      destination_id: "",
      overnightStay: true,
      hotelName: "",
      hotelCost: 0,
      transportMode: "Sedan Transfer",
      transportCost: 0,
      activities: "Pick up from airport and check in to hotel. Free leisure evening.",
      activityCost: 0,
      meals: ["Breakfast"],
      notes: ""
    }
  ]);

  // Mutations
  const createMutation = useCreateProposal();
  const updateMutation = useUpdateProposal(id);

  // Sync state with loaded proposal on Edit mode
  useEffect(() => {
    if (isEdit && proposal) {
      setProposalTitle(proposal.proposal_title || "");
      setValidUntil(proposal.valid_until || "");
      setInternalNotes(proposal.internal_notes || "");
      
      // Load structured days if saved, else fallback
      if (proposal.structured_itinerary?.days) {
        setDays(proposal.structured_itinerary.days);
      }
      if (proposal.structured_itinerary?.markupPercent) {
        setMarkupPercent(proposal.structured_itinerary.markupPercent);
      }
    } else if (lead) {
      setProposalTitle(`Custom Trip for ${lead.contact_person?.name || "Client"}`);
      // Default validity = today + 10 days
      const targetDate = new Date();
      targetDate.setDate(targetDate.getDate() + 10);
      setValidUntil(targetDate.toISOString().split("T")[0]);
    }
  }, [isEdit, proposal, lead]);

  // Cost Calculations
  const travelersCount = lead?.traveler_count || 1;

  const calculateSubtotal = () => {
    return days.reduce((sum, d) => {
      const hC = parseFloat(d.hotelCost) || 0;
      const tC = parseFloat(d.transportCost) || 0;
      const aC = parseFloat(d.activityCost) || 0;
      return sum + hC + tC + aC;
    }, 0);
  };

  const subtotal = calculateSubtotal();
  const markupAmount = subtotal * (parseFloat(markupPercent) / 100 || 0);
  const totalSellingPrice = subtotal + markupAmount;
  const pricePerPerson = totalSellingPrice / travelersCount;
  const profitAmount = markupAmount;

  // Itinerary editors handlers
  const handleAddDay = () => {
    setDays((prev) => [
      ...prev,
      {
        title: `Day ${prev.length + 1} Sightseeing`,
        destination_id: prev[prev.length - 1]?.destination_id || "",
        overnightStay: true,
        hotelName: prev[prev.length - 1]?.hotelName || "",
        hotelCost: 0,
        transportMode: prev[prev.length - 1]?.transportMode || "Private SUV",
        transportCost: 0,
        activities: "Local sightseeing and leisure walks.",
        activityCost: 0,
        meals: ["Breakfast"],
        notes: ""
      }
    ]);
  };

  const handleDeleteDay = (index) => {
    if (days.length <= 1) return;
    setDays((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleDayFieldChange = (index, field, val) => {
    setDays((prev) =>
      prev.map((d, idx) => (idx === index ? { ...d, [field]: val } : d))
    );
  };

  const handleMealsToggle = (dayIndex, meal) => {
    const currentMeals = days[dayIndex].meals || [];
    const nextMeals = currentMeals.includes(meal)
      ? currentMeals.filter((m) => m !== meal)
      : [...currentMeals, meal];
    handleDayFieldChange(dayIndex, "meals", nextMeals);
  };

  const handleSave = () => {
    if (!proposalTitle) {
      alert("Please specify a proposal title.");
      return;
    }
    if (!activeLeadId) {
      alert("Lead reference missing.");
      return;
    }

    // Format destinations parameter
    const destinationsPayload = days
      .filter((d) => d.destination_id && d.destination_id.length > 0)
      .map((d, index) => ({
        destination_id: d.destination_id,
        day_order: index + 1,
        sequence_no: index + 1,
        overnight_stay: !!d.overnightStay,
        day_title: d.title || `Day ${index + 1}`,
        travel_mode: d.transportMode || null,
        notes: d.activities || null,
      }));

    const structuredPayload = {
      days,
      markupPercent,
      subtotal,
      totalSellingPrice,
      pricePerPerson,
      profitAmount,
    };

    const payload = {
      lead_id: activeLeadId,
      proposal_title: proposalTitle,
      price_per_person: pricePerPerson,
      total_amount: totalSellingPrice,
      valid_until: validUntil || null,
      internal_notes: internalNotes || null,
      structured_itinerary: structuredPayload,
      destinations: destinationsPayload,
    };

    if (isEdit) {
      updateMutation.mutate({
        ...payload,
        row_version: proposal.row_version,
      }, {
        onSuccess: () => {
          navigate(`/admin/proposals/${id}`);
        }
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: (res) => {
          const newId = res.data?.id;
          if (newId) {
            navigate(`/admin/proposals/${newId}`);
          } else {
            navigate("/admin/proposals");
          }
        }
      });
    }
  };

  const isSaving = createMutation.isPending || updateMutation.isPending;

  if (isProposalLoading || isLeadLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4">
        <Loader2 className="animate-spin text-blue-600" size={45} />
        <p className="text-xs font-semibold text-slate-600">Initializing travel builder workspace...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* 1. Sticky Header Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200 shrink-0 flex-wrap gap-3">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => navigate(isEdit ? `/admin/proposals/${id}` : "/admin/proposals")}
            className="p-1.5 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <ArrowLeft size={16} />
          </button>
          <div>
            <h1 className="text-lg font-bold text-slate-800 tracking-tight">
              {isEdit ? "Revise Itinerary Quotation" : "Travel Itinerary Designer"}
            </h1>
            <p className="text-[10px] text-slate-400 font-semibold">
              Linked Client: <span className="text-slate-600 font-bold">{lead?.contact_person?.name || "Client"}</span> ({lead?.traveler_count || 1} travelers)
            </p>
          </div>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-md shadow-blue-500/10 transition-colors focus:outline-none"
        >
          {isSaving ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
          <span>{isEdit ? "Save Revision" : "Create Proposal"}</span>
        </button>
      </div>

      {/* 2. Three Panel Workspace Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0 min-w-0">
        
        {/* Left Sidebar - Navigation steps & Settings */}
        <div className="lg:col-span-1 flex flex-col space-y-4 overflow-y-auto pr-1">
          {/* Settings Card */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center">
              <Sparkles size={12} className="mr-1.5 text-blue-500" />
              General Details
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-600 mb-1">Proposal Title *</label>
                <input
                  type="text"
                  value={proposalTitle}
                  onChange={(e) => setProposalTitle(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                  placeholder="e.g. Munnar Deluxe Couple Getaway"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-600 mb-1">Price Validity Expiry</label>
                <input
                  type="date"
                  value={validUntil}
                  onChange={(e) => setValidUntil(e.target.value)}
                  className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-600 mb-1">Private Internal Notes</label>
                <textarea
                  rows="3"
                  value={internalNotes}
                  onChange={(e) => setInternalNotes(e.target.value)}
                  placeholder="Hotel vouchers details, negotiation limits, discounts..."
                  className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Central Workspace - Itinerary Editor */}
        <div className="lg:col-span-2 flex flex-col min-h-0 min-w-0 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          {/* Header */}
          <div className="px-5 py-3.5 border-b border-slate-200 bg-slate-50 flex items-center justify-between shrink-0">
            <h3 className="text-xs font-bold text-slate-800 flex items-center uppercase tracking-wider">
              <Compass size={14} className="mr-2 text-blue-500" />
              Day-by-Day schedule
            </h3>
            <button
              onClick={handleAddDay}
              className="flex items-center space-x-1 px-2.5 py-1 bg-white border border-slate-200 hover:border-slate-300 text-slate-700 rounded-md text-[10px] font-bold shadow-sm transition-all focus:outline-none"
            >
              <Plus size={10} />
              <span>Add Day</span>
            </button>
          </div>

          {/* Form lists */}
          <div className="flex-1 overflow-y-auto p-5 space-y-6 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
            {days.map((day, dayIdx) => (
              <div key={dayIdx} className="border border-slate-200 rounded-xl p-4 bg-slate-50/20 space-y-4 relative">
                
                {/* Delete CTA */}
                {days.length > 1 && (
                  <button
                    onClick={() => handleDeleteDay(dayIdx)}
                    className="absolute top-4 right-4 p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-red-600 transition-all focus:outline-none"
                  >
                    <Trash2 size={14} />
                  </button>
                )}

                {/* Day title & Location */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block font-bold text-slate-500 uppercase text-[9px] mb-1">
                      Day {dayIdx + 1} Title *
                    </label>
                    <input
                      type="text"
                      value={day.title}
                      onChange={(e) => handleDayFieldChange(dayIdx, "title", e.target.value)}
                      placeholder="e.g. Arrival & Hotel Check-in"
                      className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-500 uppercase text-[9px] mb-1">
                      Location / Destination
                    </label>
                    <select
                      value={day.destination_id}
                      onChange={(e) => handleDayFieldChange(dayIdx, "destination_id", e.target.value)}
                      className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none font-semibold text-slate-600"
                    >
                      <option value="">Select location</option>
                      {destinations.map((d) => (
                        <option key={d.id} value={d.id}>{d.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Overnight checkbox */}
                <div className="flex items-center space-x-2 text-xs font-semibold text-slate-600">
                  <input
                    type="checkbox"
                    checked={day.overnightStay}
                    onChange={(e) => handleDayFieldChange(dayIdx, "overnightStay", e.target.checked)}
                    id={`overnight-${dayIdx}`}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor={`overnight-${dayIdx}`}>Overnight stay at this destination</label>
                </div>

                {/* Cost builders */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-2 border-t border-slate-100">
                  {/* Hotel */}
                  <div>
                    <label className="block font-bold text-slate-500 uppercase text-[9px] mb-1 flex items-center">
                      <HomeIcon size={10} className="mr-1 text-blue-500" /> Accommodation Name
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Broad Bean Resort"
                      value={day.hotelName}
                      onChange={(e) => handleDayFieldChange(dayIdx, "hotelName", e.target.value)}
                      className="w-full px-2 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                    <input
                      type="number"
                      placeholder="Cost (INR)"
                      value={day.hotelCost || ""}
                      onChange={(e) => handleDayFieldChange(dayIdx, "hotelCost", e.target.value)}
                      className="w-full mt-1.5 px-2 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                  </div>

                  {/* Transfer */}
                  <div>
                    <label className="block font-bold text-slate-500 uppercase text-[9px] mb-1 flex items-center">
                      <Plane size={10} className="mr-1 text-purple-500" /> Transfer Mode
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Sedan A/C Cab"
                      value={day.transportMode}
                      onChange={(e) => handleDayFieldChange(dayIdx, "transportMode", e.target.value)}
                      className="w-full px-2 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                    <input
                      type="number"
                      placeholder="Cost (INR)"
                      value={day.transportCost || ""}
                      onChange={(e) => handleDayFieldChange(dayIdx, "transportCost", e.target.value)}
                      className="w-full mt-1.5 px-2 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                  </div>

                  {/* Activities */}
                  <div>
                    <label className="block font-bold text-slate-500 uppercase text-[9px] mb-1 flex items-center">
                      <Compass size={10} className="mr-1 text-emerald-500" /> Sightseeing / Guide
                    </label>
                    <input
                      type="text"
                      placeholder="Activity detail notes..."
                      value={day.activities}
                      onChange={(e) => handleDayFieldChange(dayIdx, "activities", e.target.value)}
                      className="w-full px-2 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                    <input
                      type="number"
                      placeholder="Cost (INR)"
                      value={day.activityCost || ""}
                      onChange={(e) => handleDayFieldChange(dayIdx, "activityCost", e.target.value)}
                      className="w-full mt-1.5 px-2 py-1.5 border border-slate-200 rounded-lg bg-white focus:outline-none"
                    />
                  </div>
                </div>

                {/* Meals Inclusions checklist */}
                <div className="pt-2 border-t border-slate-100 flex items-center space-x-4 text-xs font-semibold text-slate-500 flex-wrap gap-2">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Meals:</span>
                  {["Breakfast", "Lunch", "Dinner"].map((meal) => {
                    const isChecked = day.meals?.includes(meal);
                    return (
                      <button
                        key={meal}
                        type="button"
                        onClick={() => handleMealsToggle(dayIdx, meal)}
                        className={`px-2 py-0.5 rounded border text-[10px] transition-all focus:outline-none ${
                          isChecked
                            ? "bg-blue-50 border-blue-200 text-blue-700 font-bold"
                            : "bg-white border-slate-200 hover:bg-slate-50"
                        }`}
                      >
                        {meal}
                      </button>
                    );
                  })}
                </div>

              </div>
            ))}
          </div>
        </div>

        {/* Right Sidebar - Cost calculations & Profit margins */}
        <div className="lg:col-span-1 flex flex-col space-y-4 overflow-y-auto pr-1">
          {/* Summary Panel */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-5">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center">
              <DollarSign size={12} className="mr-1.5 text-blue-500" />
              Live Pricing Sheet
            </h3>

            {/* Calculations display */}
            <div className="space-y-3.5 text-xs">
              
              <div className="flex items-center justify-between font-semibold text-slate-500">
                <span>Subtotal (Net Cost):</span>
                <span>INR {subtotal.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-slate-100">
                <label className="block font-semibold text-slate-600">Company Markup (%)</label>
                <div className="relative">
                  <input
                    type="number"
                    min="0"
                    value={markupPercent}
                    onChange={(e) => setMarkupPercent(parseFloat(e.target.value) || 0)}
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none font-bold text-slate-700"
                  />
                  <span className="absolute right-3 top-2 text-slate-400 font-bold">%</span>
                </div>
              </div>

              <div className="flex items-center justify-between font-semibold text-slate-500 pt-2">
                <span>Profit Margin:</span>
                <span className="text-emerald-600 font-bold">
                  + INR {profitAmount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl space-y-2 pt-3 border-t border-slate-200">
                <div className="flex items-center justify-between font-black text-slate-800">
                  <span>Grand Total:</span>
                  <span>INR {totalSellingPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold">
                  <span>Per Person (x{travelersCount}):</span>
                  <span>INR {pricePerPerson.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
                </div>
              </div>

            </div>

            {/* Profit margin threshold check warning */}
            {profitAmount === 0 && (
              <div className="p-3 bg-rose-50 border border-rose-100 rounded-xl text-[10px] text-rose-700 font-bold flex items-start space-x-2">
                <AlertTriangle size={14} className="shrink-0 mt-0.5" />
                <span>Zero company markup added. Verify itinerary pricing costs before creation.</span>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}

export default ProposalBuilderPage;
