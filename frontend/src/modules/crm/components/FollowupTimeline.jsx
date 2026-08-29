import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useFollowups, useCreateFollowup, useCompleteFollowup } from "../hooks/useFollowups";
import crmApi from "../services/crmApi";
import { Clock, CheckSquare, Plus, Loader2, StickyNote, Calendar, AlertCircle } from "lucide-react";

export function FollowupTimeline({ leadId }) {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [activeCompleteId, setActiveCompleteId] = useState(null);
  const [completionNotes, setCompletionNotes] = useState("");
  const [formData, setFormData] = useState({
    followup_type_id: "",
    scheduled_date: "",
    notes: "",
  });

  // Queries and mutations
  const { data: followupsResponse, isLoading } = useFollowups(leadId);
  const { data: typesLookup } = useQuery({
    queryKey: ["lookups", "followup_types"],
    queryFn: () => crmApi.getLookups("followup_types"),
  });
  const createFollowupMutation = useCreateFollowup(leadId);
  const completeFollowupMutation = useCompleteFollowup(leadId);

  const followups = followupsResponse?.data || [];
  const followupTypes = typesLookup?.data || [];

  const handleInputChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!formData.followup_type_id || !formData.scheduled_date) {
      alert("Please select followup type and scheduled time.");
      return;
    }

    const payload = {
      ...formData,
      // Format scheduled_date to standard ISO UTC string
      scheduled_date: new Date(formData.scheduled_date).toISOString(),
      notes: formData.notes || null,
    };

    createFollowupMutation.mutate(payload, {
      onSuccess: () => {
        setIsFormOpen(false);
        setFormData({
          followup_type_id: "",
          scheduled_date: "",
          notes: "",
        });
      },
    });
  };

  const handleComplete = (followupId) => {
    const payload = {
      completion_notes: completionNotes || "Follow-up executed successfully.",
    };

    completeFollowupMutation.mutate(
      { followupId, payload },
      {
        onSuccess: () => {
          setActiveCompleteId(null);
          setCompletionNotes("");
        },
      }
    );
  };

  const getFollowupStatus = (item) => {
    if (item.is_completed) return "completed";
    
    const schedDate = new Date(item.scheduled_date);
    const today = new Date();

    // Reset times to compare dates only
    const schedDateTrunc = new Date(schedDate.getFullYear(), schedDate.getMonth(), schedDate.getDate());
    const todayTrunc = new Date(today.getFullYear(), today.getMonth(), today.getDate());

    if (schedDateTrunc < todayTrunc) return "overdue";
    if (schedDateTrunc.getTime() === todayTrunc.getTime()) return "today";
    return "pending";
  };

  const getStatusClasses = (status) => {
    switch (status) {
      case "completed":
        return "bg-emerald-50 border-emerald-200 text-emerald-700";
      case "overdue":
        return "bg-rose-50 border-rose-200 text-rose-700";
      case "today":
        return "bg-amber-50 border-amber-200 text-amber-700";
      default:
        return "bg-blue-50 border-blue-200 text-blue-700";
    }
  };

  return (
    <div className="space-y-6 select-none">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-800">Scheduled Follow-ups</h3>
        {!isFormOpen && (
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center space-x-1 px-3 py-1.5 border border-slate-200 hover:border-slate-300 rounded-lg text-xs font-semibold text-slate-700 bg-white shadow-sm transition-colors focus:outline-none"
          >
            <Plus size={14} />
            <span>Schedule Follow-up</span>
          </button>
        )}
      </div>

      {/* Expandable scheduler form */}
      {isFormOpen && (
        <form onSubmit={handleFormSubmit} className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-4 animate-in slide-in-from-top-3 duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <span className="text-xs font-bold text-slate-700">Schedule New Reminder</span>
            <button
              type="button"
              onClick={() => setIsFormOpen(false)}
              className="text-xs font-semibold text-slate-400 hover:text-slate-600 focus:outline-none"
            >
              Cancel
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Followup Method *</label>
              <select
                value={formData.followup_type_id}
                onChange={(e) => handleInputChange("followup_type_id", e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none"
              >
                <option value="">Select type</option>
                {followupTypes.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Scheduled Date & Time *</label>
              <input
                type="datetime-local"
                value={formData.scheduled_date}
                onChange={(e) => handleInputChange("scheduled_date", e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Context Notes</label>
            <textarea
              rows="2"
              placeholder="Provide instructions: e.g. Call client to verify passport name listings..."
              value={formData.notes}
              onChange={(e) => handleInputChange("notes", e.target.value)}
              className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white focus:outline-none"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setIsFormOpen(false)}
              className="px-3 py-1.5 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 focus:outline-none"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createFollowupMutation.isPending}
              className="px-4 py-1.5 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 flex items-center shadow-sm"
            >
              {createFollowupMutation.isPending ? (
                <Loader2 className="animate-spin mr-1.5" size={12} />
              ) : null}
              <span>Save Reminder</span>
            </button>
          </div>
        </form>
      )}

      {/* Grid listing */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          {Array.from({ length: 2 }).map((_, idx) => (
            <div key={idx} className="h-28 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : followups.length === 0 ? (
        <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
          <Clock className="mx-auto text-slate-400 mb-2" size={24} />
          <p className="text-xs font-semibold text-slate-800">No scheduled reminders</p>
          <p className="text-[10px] text-slate-400 mt-0.5">Click "Schedule Follow-up" to schedule tasks and reminder prompts.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          {followups.map((item) => {
            const status = getFollowupStatus(item);
            const statusStyle = getStatusClasses(status);
            const isCompletingThis = activeCompleteId === item.id;

            return (
              <div
                key={item.id}
                className={`border rounded-xl p-4 shadow-sm flex flex-col justify-between space-y-3 bg-white transition-all hover:shadow-md`}
              >
                
                {/* Header detail */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">
                      {item.followup_type?.name || "Follow-up"}
                    </span>
                    <span className={`px-2 py-0.5 rounded-[4px] text-[9px] font-bold uppercase border ${statusStyle}`}>
                      {status}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 flex items-center font-semibold mt-1">
                    <Clock size={10} className="mr-1 shrink-0" />
                    {item.scheduled_date ? new Date(item.scheduled_date).toLocaleString("en-IN") : ""}
                  </p>
                </div>

                {/* Notes context */}
                <p className="text-xs text-slate-600 leading-relaxed font-semibold italic flex-1">
                  "{item.notes || "No context instructions provided."}"
                </p>

                {/* Completion detail or CTA actions */}
                <div className="pt-2 border-t border-slate-100 shrink-0">
                  {item.is_completed ? (
                    <div className="text-[10px] text-slate-500 font-semibold space-y-0.5">
                      <p className="text-[9px] text-emerald-600 font-bold uppercase flex items-center">
                        <CheckSquare size={10} className="mr-1" />
                        Completed
                      </p>
                      <p className="truncate">"{item.completion_notes || "Executed."}"</p>
                      <p className="text-[9px] text-slate-400">
                        at {item.completed_at ? new Date(item.completed_at).toLocaleString("en-IN") : ""}
                      </p>
                    </div>
                  ) : isCompletingThis ? (
                    // Expandable complete logger input inside card
                    <div className="space-y-2 animate-in fade-in duration-150">
                      <input
                        type="text"
                        placeholder="Log execution details..."
                        value={completionNotes}
                        onChange={(e) => setCompletionNotes(e.target.value)}
                        className="w-full px-2 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none text-slate-700"
                        autoFocus
                      />
                      <div className="flex items-center justify-end space-x-1">
                        <button
                          onClick={() => setActiveCompleteId(null)}
                          className="px-2 py-1 rounded text-[10px] font-bold text-slate-500 hover:bg-slate-100"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleComplete(item.id)}
                          disabled={completeFollowupMutation.isPending}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-[10px] font-bold shadow-sm flex items-center"
                        >
                          {completeFollowupMutation.isPending ? (
                            <Loader2 className="animate-spin mr-1" size={10} />
                          ) : null}
                          <span>Mark Done</span>
                        </button>
                      </div>
                    </div>
                  ) : (
                    // Trigger actions
                    <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
                      {status === "overdue" && (
                        <span className="text-rose-600 font-semibold flex items-center text-[9px]">
                          <AlertCircle size={10} className="mr-1" />
                          Requires Action
                        </span>
                      )}
                      <button
                        onClick={() => setActiveCompleteId(item.id)}
                        className="ml-auto flex items-center space-x-1 px-2.5 py-1 border border-emerald-200 hover:border-emerald-300 text-emerald-700 bg-emerald-50 hover:bg-emerald-100/60 rounded text-[10px] font-bold shadow-sm transition-all focus:outline-none"
                      >
                        <CheckSquare size={10} />
                        <span>Log Execution</span>
                      </button>
                    </div>
                  )}
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}

export default FollowupTimeline;
