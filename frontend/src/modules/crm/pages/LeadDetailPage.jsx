import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useLeadDetail, useUpdateLead, useConvertLead, useDeleteLead } from "../hooks/useLeadDetail";
import crmApi from "../services/crmApi";
import LeadOverview from "../components/LeadOverview";
import ActivityTimeline from "../components/ActivityTimeline";
import FollowupTimeline from "../components/FollowupTimeline";
import ConvertLeadModal from "../modals/ConvertLeadModal";
import MarkLeadLostModal from "../modals/MarkLeadLostModal";
import EditLeadDrawer from "../modals/EditLeadDrawer";
import { LeadStatusBadge, LeadPriorityBadge } from "../components/LeadStatusBadge";

const STATUS_TRANSITIONS = {
  "NEW": ["ASSIGNED", "LOST"],
  "ASSIGNED": ["CONTACTED", "LOST"],
  "CONTACTED": ["REQUIREMENT_GATHERING", "LOST"],
  "REQUIREMENT_GATHERING": ["PROPOSAL_SENT", "LOST"],
  "PROPOSAL_SENT": ["NEGOTIATION", "WON", "LOST"],
  "NEGOTIATION": ["WON", "LOST"],
  "WON": [],
  "LOST": []
};

import {
  ArrowLeft,
  ChevronRight,
  User,
  Settings,
  RefreshCw,
  Trash2,
  FileText,
  Clock,
  Compass,
  FileCheck,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  Plus,
  Edit2
} from "lucide-react";

export function LeadDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");
  const [isConvertOpen, setIsConvertOpen] = useState(false);
  const [isLostOpen, setIsLostOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);

  // Queries
  const { data: leadResponse, isLoading: isLeadLoading, error } = useLeadDetail(id);
  const { data: teamLookup } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => crmApi.getTeamMembers(),
  });
  const { data: statusLookup } = useQuery({
    queryKey: ["lookups", "statuses"],
    queryFn: () => crmApi.getLookups("statuses"),
  });

  const lead = leadResponse?.data;
  const teamMembers = teamLookup?.data?.items || [];
  const statuses = statusLookup?.data || [];

  // Mutations
  const updateLeadMutation = useUpdateLead(id);
  const convertLeadMutation = useConvertLead(id);
  const deleteLeadMutation = useDeleteLead();

  const handleStatusChange = (statusId) => {
    if (!lead) return;
    updateLeadMutation.mutate({
      version: lead.version,
      current_status_id: statusId,
    });
  };

  const handleOwnerChange = (ownerId) => {
    if (!lead) return;
    
    const payload = {
      version: lead.version,
      owner_team_member_id: ownerId || null,
      assignment_reason: "Manual owner allocation from detail header",
    };

    // Auto-advance status from NEW to ASSIGNED if owner is assigned
    if (lead.current_status?.code?.toUpperCase() === "NEW" && ownerId) {
      const assignedStatus = statuses.find((s) => s.code?.toUpperCase() === "ASSIGNED");
      if (assignedStatus) {
        payload.current_status_id = assignedStatus.id;
      }
    }

    updateLeadMutation.mutate(payload);
  };

  const handleConvertLead = (payload, callback) => {
    convertLeadMutation.mutate(payload, {
      onSuccess: (response) => {
        callback();
        // Redirect to booking detail (standard booking module path prefix: /admin/bookings/:id)
        const bookingId = response.data?.booking_id || response.data?.id;
        if (bookingId) {
          navigate(`/admin/bookings/${bookingId}`);
        } else {
          navigate("/admin/bookings");
        }
      },
    });
  };

  const handleDeleteLead = () => {
    if (window.confirm("Are you sure you want to delete this lead? This will cancel all pending follow-ups.")) {
      deleteLeadMutation.mutate(lead.id, {
        onSuccess: () => {
          navigate("/admin/crm/leads");
        },
      });
    }
  };

  const handleMarkLost = (lostPayload, callback) => {
    const lostStatus = statuses.find((s) => s.code?.toUpperCase() === "LOST");
    if (!lostStatus) return;

    updateLeadMutation.mutate(
      {
        version: lead.version,
        current_status_id: lostStatus.id,
        lost_reason_id: lostPayload.lost_reason_id,
        lost_date: lostPayload.lost_date,
      },
      {
        onSuccess: () => {
          callback();
          setIsLostOpen(false);
        },
      }
    );
  };

  const handleEditLead = (editPayload, callback) => {
    updateLeadMutation.mutate(editPayload, {
      onSuccess: () => {
        callback();
        setIsEditOpen(false);
      },
    });
  };

  if (isLeadLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4">
        <Compass className="animate-spin text-blue-600" size={40} />
        <p className="text-xs font-semibold text-slate-600">Hydrating lead file...</p>
      </div>
    );
  }

  if (error || !lead) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4 select-none">
        <AlertTriangle className="text-rose-500" size={40} />
        <p className="text-sm font-semibold text-slate-800">Lead File Not Found</p>
        <p className="text-xs text-slate-400">The requested lead record does not exist or has been deleted.</p>
        <button
          onClick={() => navigate("/admin/crm/leads")}
          className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 transition-colors"
        >
          Return to Leads list
        </button>
      </div>
    );
  }

  const owner = teamMembers.find((m) => m.id === lead.owner_team_member_id);

  // Status Stepper lifecycle flow
  const stepperStates = [
    { code: "NEW", name: "New" },
    { code: "ASSIGNED", name: "Assigned" },
    { code: "CONTACTED", name: "Contacted" },
    { code: "REQUIREMENT_GATHERING", name: "Intake" },
    { code: "PROPOSAL_SENT", name: "Proposal" },
    { code: "NEGOTIATION", name: "Negotiation" },
    { code: "WON", name: "Won" },
  ];

  const currentStatusCode = lead.current_status?.code?.toUpperCase();

  const handleStepClick = (stepCode) => {
    if (stepCode === "WON" || stepCode === "LOST") {
      if (stepCode === "WON") setIsConvertOpen(true);
      if (stepCode === "LOST") setIsLostOpen(true);
      return;
    }
    const matchingStatus = statuses.find((s) => s.code?.toUpperCase() === stepCode);
    if (matchingStatus) {
      handleStatusChange(matchingStatus.id);
    }
  };

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* 1. Header Toolbar */}
      <div className="flex items-start justify-between flex-wrap gap-4 shrink-0 pb-4 border-b border-slate-100">
        <div className="space-y-2">
          {/* Breadcrumb navigation */}
          <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1.5">
            <button onClick={() => navigate("/admin/crm/leads")} className="hover:text-slate-600 transition-colors">
              Leads
            </button>
            <ChevronRight size={10} className="text-slate-300" />
            <span className="text-slate-500 font-bold">{lead.lead_number}</span>
          </div>

          <div className="flex items-center space-x-3 flex-wrap gap-2">
            <h1 className="text-xl font-bold text-slate-800 tracking-tight">
              {lead.contact_person?.name || "Unidentified Lead"}
            </h1>
            <LeadStatusBadge status={lead.current_status} />
            <LeadPriorityBadge priority={lead.priority} />
          </div>

          <p className="text-[10px] text-slate-400 font-semibold">
            Logged by {lead.audit_info?.created_by_team_member_id ? "Sales Handler" : "Web Intake"} on{" "}
            {lead.audit_info?.created_at ? new Date(lead.audit_info.created_at).toLocaleString("en-IN") : "—"}
          </p>
        </div>

        {/* Global Action CTAs */}
        <div className="flex items-center space-x-2">
          {currentStatusCode !== "WON" && currentStatusCode !== "LOST" && (
            <>
              <button
                onClick={() => setIsEditOpen(true)}
                className="flex items-center space-x-1.5 px-3 py-2 border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-bold transition-all focus:outline-none"
              >
                <Edit2 size={14} />
                <span>Edit Lead</span>
              </button>
              <button
                onClick={() => navigate(`/admin/proposals/new?lead_id=${lead.id}`)}
                className="flex items-center space-x-1.5 px-3 py-2 border border-blue-200 text-blue-700 hover:bg-blue-50 rounded-lg text-xs font-bold transition-all focus:outline-none"
              >
                <Plus size={14} />
                <span>Create Proposal</span>
              </button>
              <button
                onClick={() => setIsConvertOpen(true)}
                className="flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-500/10 transition-colors focus:outline-none"
              >
                <CheckCircle2 size={14} />
                <span>Convert to Booking</span>
              </button>
              <button
                onClick={() => setIsLostOpen(true)}
                className="flex items-center space-x-1.5 px-3 py-2 border border-red-200 text-red-700 hover:bg-red-50 rounded-lg text-xs font-bold transition-all focus:outline-none"
              >
                <AlertTriangle size={14} className="text-red-500" />
                <span>Mark as Lost</span>
              </button>
            </>
          )}
          <button
            onClick={handleDeleteLead}
            className="flex items-center space-x-1.5 px-3 py-2 border border-rose-200 text-rose-700 hover:bg-rose-50 rounded-lg text-xs font-bold transition-all focus:outline-none"
          >
            <Trash2 size={14} />
            <span>Cancel Lead</span>
          </button>
        </div>
      </div>

      {/* 2. Interactive Status Stepper */}
      {currentStatusCode !== "LOST" && (
        <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm shrink-0">
          <div className="flex items-center justify-between overflow-x-auto gap-2 pb-1 scrollbar-thin scrollbar-thumb-slate-100 scrollbar-track-transparent">
            {stepperStates.map((step, idx) => {
              const matchingStatus = statuses.find((s) => s.code?.toUpperCase() === step.code);
              const isActive = currentStatusCode === step.code;
              const isFuture = stepperStates.findIndex(s => s.code === currentStatusCode) < idx;

              const allowed = STATUS_TRANSITIONS[currentStatusCode] || [];
              const isTransitionable = allowed.includes(step.code);

              return (
                <React.Fragment key={step.code}>
                  <button
                    onClick={() => handleStepClick(step.code)}
                    disabled={isActive || updateLeadMutation.isPending || (!isTransitionable && !isActive)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 focus:outline-none ${
                      isActive
                        ? "bg-blue-600 text-white shadow-sm shadow-blue-500/10"
                        : isFuture
                        ? "bg-slate-50 border border-slate-200 text-slate-400 hover:bg-slate-100/60"
                        : "bg-blue-50 border border-blue-100 text-blue-700 hover:bg-blue-100/40"
                    }`}
                  >
                    {step.name}
                  </button>
                  {idx < stepperStates.length - 1 && (
                    <ChevronRight size={14} className="text-slate-300 shrink-0" />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}

      {/* 3. Owner Allocations toolbar */}
      <div className="bg-slate-100/50 border border-slate-200 rounded-xl p-3 shadow-sm flex items-center justify-between flex-wrap gap-3 text-xs font-semibold text-slate-500 shrink-0 select-none">
        <div className="flex items-center space-x-2">
          <User size={14} className="text-slate-400" />
          <span>Sales Owner:</span>
          <select
            value={lead.owner_team_member_id || ""}
            onChange={(e) => handleOwnerChange(e.target.value)}
            disabled={updateLeadMutation.isPending}
            className="bg-white border border-slate-200 rounded px-2.5 py-1 text-slate-700 font-bold focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Unassigned</option>
            {teamMembers.map((m) => (
              <option key={m.id} value={m.id}>
                {m.display_name}
              </option>
            ))}
          </select>
        </div>

        {updateLeadMutation.isPending && (
          <div className="flex items-center space-x-1.5 text-blue-600">
            <Loader2 className="animate-spin" size={12} />
            <span>Syncing lifecycle...</span>
          </div>
        )}
      </div>

      {/* 4. Modular Tabbed view */}
      <div className="flex-1 flex flex-col min-h-0 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        
        {/* Navigation tabs */}
        <div className="flex border-b border-slate-200 bg-slate-50 shrink-0 overflow-x-auto scrollbar-none">
          {[
            { id: "overview", name: "File Overview", icon: FileText },
            { id: "activities", name: "Contact Log", icon: Clock },
            { id: "followups", name: "Schedule Tasks", icon: clockIconPlaceholder },
          ].map((tab) => {
            const Icon = tab.icon === clockIconPlaceholder ? Clock : tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-5 py-3.5 border-b-2 text-xs font-bold tracking-tight select-none focus:outline-none transition-all ${
                  activeTab === tab.id
                    ? "border-blue-600 text-blue-600 bg-white"
                    : "border-transparent text-slate-400 hover:text-slate-700 hover:bg-slate-100/40"
                }`}
              >
                <Icon size={14} />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </div>

        {/* Tab content view */}
        <div className="flex-1 overflow-y-auto p-6 min-h-0 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
          {activeTab === "overview" && (
            <LeadOverview lead={lead} teamMembers={teamMembers} />
          )}
          {activeTab === "activities" && (
            <ActivityTimeline leadId={lead.id} />
          )}
          {activeTab === "followups" && (
            <FollowupTimeline leadId={lead.id} />
          )}
        </div>

      </div>

      {/* Convert Lead modal */}
      <ConvertLeadModal
        isOpen={isConvertOpen}
        onClose={() => setIsConvertOpen(false)}
        onConvert={handleConvertLead}
        isSubmitting={convertLeadMutation.isPending}
        defaultValues={lead}
      />

      {/* Mark Lead Lost Modal */}
      <MarkLeadLostModal
        isOpen={isLostOpen}
        onClose={() => setIsLostOpen(false)}
        onConfirm={handleMarkLost}
        isSubmitting={updateLeadMutation.isPending}
      />

      {/* Edit Lead Drawer */}
      <EditLeadDrawer
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        lead={lead}
        onSubmit={handleEditLead}
        isSubmitting={updateLeadMutation.isPending}
      />

    </div>
  );
}

// Clock placeholder to prevent import name shadowing inside array loops
const clockIconPlaceholder = "CLOCK_PLACEHOLDER";

export default LeadDetailPage;
