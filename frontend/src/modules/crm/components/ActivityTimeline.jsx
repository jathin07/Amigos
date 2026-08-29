import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useActivities, useCreateActivity } from "../hooks/useActivities";
import crmApi from "../services/crmApi";
import { Phone, Mail, Users, MessageSquare, StickyNote, Plus, Loader2, Calendar } from "lucide-react";

export function ActivityTimeline({ leadId }) {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formData, setFormData] = useState({
    activity_type_id: "",
    discussion_summary: "",
    outcome: "",
    next_action: "",
    next_followup_date: "",
  });

  // Queries and mutations
  const { data: activitiesResponse, isLoading } = useActivities(leadId);
  const { data: typesLookup } = useQuery({
    queryKey: ["lookups", "activity_types"],
    queryFn: () => crmApi.getLookups("activity_types"),
  });
  const createActivityMutation = useCreateActivity(leadId);

  const activities = activitiesResponse?.data || [];
  const activityTypes = typesLookup?.data || [];

  const handleInputChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!formData.activity_type_id || !formData.discussion_summary) {
      alert("Please select activity type and fill discussion summary.");
      return;
    }

    const payload = {
      ...formData,
      next_followup_date: formData.next_followup_date || null,
      outcome: formData.outcome || null,
      next_action: formData.next_action || null,
    };

    createActivityMutation.mutate(payload, {
      onSuccess: () => {
        setIsFormOpen(false);
        setFormData({
          activity_type_id: "",
          discussion_summary: "",
          outcome: "",
          next_action: "",
          next_followup_date: "",
        });
      },
    });
  };

  const getActivityIcon = (code) => {
    switch (code?.toUpperCase()) {
      case "CALL":
        return <Phone size={14} className="text-blue-600" />;
      case "EMAIL":
        return <Mail size={14} className="text-purple-600" />;
      case "MEETING":
        return <Users size={14} className="text-emerald-600" />;
      case "WHATSAPP":
        return <MessageSquare size={14} className="text-green-600" />;
      default:
        return <StickyNote size={14} className="text-slate-600" />;
    }
  };

  const getActivityBg = (code) => {
    switch (code?.toUpperCase()) {
      case "CALL":
        return "bg-blue-50 border-blue-200";
      case "EMAIL":
        return "bg-purple-50 border-purple-200";
      case "MEETING":
        return "bg-emerald-50 border-emerald-200";
      case "WHATSAPP":
        return "bg-green-50 border-green-200";
      default:
        return "bg-slate-50 border-slate-200";
    }
  };

  return (
    <div className="space-y-6 select-none">
      
      {/* Logger header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-800">Interaction History</h3>
        {!isFormOpen && (
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center space-x-1 px-3 py-1.5 border border-slate-200 hover:border-slate-300 rounded-lg text-xs font-semibold text-slate-700 bg-white shadow-sm transition-colors focus:outline-none"
          >
            <Plus size={14} />
            <span>Log Discussion</span>
          </button>
        )}
      </div>

      {/* Expandable activity form */}
      {isFormOpen && (
        <form onSubmit={handleFormSubmit} className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-4 animate-in slide-in-from-top-3 duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <span className="text-xs font-bold text-slate-700">Record Client Contact</span>
            <button
              type="button"
              onClick={() => setIsFormOpen(false)}
              className="text-xs font-semibold text-slate-400 hover:text-slate-600 focus:outline-none"
            >
              Cancel
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Activity Type *</label>
              <select
                value={formData.activity_type_id}
                onChange={(e) => handleInputChange("activity_type_id", e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none"
              >
                <option value="">Select type</option>
                {activityTypes.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Discussion Outcome</label>
              <input
                type="text"
                placeholder="e.g. Budget increased, trip postponed"
                value={formData.outcome}
                onChange={(e) => handleInputChange("outcome", e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Follow-up schedule</label>
              <input
                type="date"
                value={formData.next_followup_date}
                onChange={(e) => handleInputChange("next_followup_date", e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Discussion Summary *</label>
            <textarea
              rows="2"
              placeholder="Summary of hotel choices, package changes, or special traveler requirements..."
              value={formData.discussion_summary}
              onChange={(e) => handleInputChange("discussion_summary", e.target.value)}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Next Action Agreed</label>
              <input
                type="text"
                placeholder="e.g. Email updated custom itinerary"
                value={formData.next_action}
                onChange={(e) => handleInputChange("next_action", e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none"
              />
            </div>
            
            <div className="flex items-end justify-end space-x-2">
              <button
                type="button"
                onClick={() => setIsFormOpen(false)}
                className="px-3 py-1.5 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 focus:outline-none"
              >
                Dismiss
              </button>
              <button
                type="submit"
                disabled={createActivityMutation.isPending}
                className="px-4 py-1.5 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 flex items-center shadow-sm"
              >
                {createActivityMutation.isPending ? (
                  <Loader2 className="animate-spin mr-1.5" size={12} />
                ) : null}
                <span>Log Contact</span>
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Timeline display */}
      {isLoading ? (
        <div className="space-y-4 animate-pulse pt-2">
          {Array.from({ length: 3 }).map((_, idx) => (
            <div key={idx} className="flex space-x-3">
              <div className="w-8 h-8 rounded-full bg-slate-100 shrink-0" />
              <div className="flex-1 space-y-2 py-1">
                <div className="h-3 bg-slate-100 rounded w-1/4" />
                <div className="h-3 bg-slate-100 rounded w-full" />
              </div>
            </div>
          ))}
        </div>
      ) : activities.length === 0 ? (
        <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
          <StickyNote className="mx-auto text-slate-400 mb-2" size={24} />
          <p className="text-xs font-semibold text-slate-800">No client contact logged</p>
          <p className="text-[10px] text-slate-400 mt-0.5">Click "Log Discussion" to record emails, phone calls, or WhatsApp logs.</p>
        </div>
      ) : (
        <div className="relative pl-6 border-l border-slate-200 space-y-6 pt-2">
          {activities.map((act) => (
            <div key={act.id} className="relative">
              
              {/* Timeline Icon Node */}
              <div className={`absolute -left-[35px] top-0 w-7 h-7 rounded-full border flex items-center justify-center bg-white ${
                getActivityBg(act.activity_type?.code)
              }`}>
                {getActivityIcon(act.activity_type?.code)}
              </div>

              {/* Activity Card */}
              <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-sm space-y-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-xs font-bold text-slate-800 flex items-center">
                    {act.activity_type?.name || "Client Contact"}
                    {act.outcome && (
                      <span className="ml-2 px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-50 border border-amber-100 text-amber-700">
                        {act.outcome}
                      </span>
                    )}
                  </span>
                  <span className="text-[10px] text-slate-400 font-semibold">
                    {act.activity_date ? new Date(act.activity_date).toLocaleString("en-IN") : ""}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed font-semibold">
                  {act.discussion_summary}
                </p>

                {act.next_action && (
                  <div className="mt-2 pt-2 border-t border-slate-100 flex items-center space-x-2 text-[10px] font-semibold text-slate-500">
                    <span className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-bold uppercase text-[8px]">
                      Next Action
                    </span>
                    <span>{act.next_action}</span>
                    {act.next_followup_date && (
                      <span className="text-[10px] text-slate-400 flex items-center">
                        <Calendar size={10} className="ml-2 mr-1" />
                        by {act.next_followup_date}
                      </span>
                    )}
                  </div>
                )}
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}

export default ActivityTimeline;
