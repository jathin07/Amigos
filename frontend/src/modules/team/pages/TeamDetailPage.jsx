import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTeamMemberDetail, useUpdateTeamMember } from "../hooks/useTeam";
import TeamStatusBadge from "../components/TeamStatusBadge";
import CreateTeamMemberModal from "../modals/CreateTeamMemberModal";
import { 
  User, 
  Mail, 
  Phone, 
  Building2, 
  Calendar, 
  ShieldCheck, 
  Activity, 
  Briefcase, 
  Edit2, 
  ArrowLeft, 
  Loader2, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  Lock
} from "lucide-react";

export function TeamDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("profile");
  const [modalOpen, setModalOpen] = useState(false);

  const { data: response, isLoading, isError } = useTeamMemberDetail(id);
  const updateMutation = useUpdateTeamMember(id);

  const member = response?.data;

  const handleEditSubmit = (payload, callback) => {
    updateMutation.mutate(
      { ...payload, version: member?.version },
      {
        onSuccess: () => {
          callback();
          setModalOpen(false);
        },
      }
    );
  };

  const getInitials = (name) => {
    if (!name) return "TU";
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3">
        <Loader2 className="animate-spin text-blue-600" size={24} />
        <p className="text-xs font-semibold text-slate-500">Loading staff workspace...</p>
      </div>
    );
  }

  if (isError || !member) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center space-y-4 max-w-lg mx-auto mt-8">
        <AlertCircle className="mx-auto text-rose-500" size={32} />
        <h2 className="text-lg font-bold text-slate-800">Team Member Not Found</h2>
        <p className="text-xs text-slate-500">The requested staff record does not exist or has been removed.</p>
        <button
          onClick={() => navigate("/admin/team")}
          className="px-4 py-2 bg-slate-800 text-white rounded-lg text-xs font-bold hover:bg-slate-900"
        >
          Back to Staff Directory
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* 1. Header Navigation */}
      <div className="flex items-center space-x-3">
        <button
          onClick={() => navigate("/admin/team")}
          className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
        >
          <ArrowLeft size={16} />
        </button>
        <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
          <span>Staff Directory</span>
          <span>/</span>
          <span className="text-slate-700 font-bold">{member.display_name}</span>
        </div>
      </div>

      {/* 2. Staff Banner Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="flex items-start sm:items-center space-x-4">
          {member.avatar_url ? (
            <img
              src={member.avatar_url}
              alt={member.display_name}
              className="w-16 h-16 rounded-full object-cover border-2 border-slate-100 shadow-sm shrink-0"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-blue-600 text-white font-extrabold text-xl flex items-center justify-center shadow-md shadow-blue-500/20 shrink-0">
              {getInitials(member.display_name)}
            </div>
          )}

          <div className="space-y-1">
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-slate-800 tracking-tight">{member.display_name}</h1>
              <span className="px-2.5 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[11px] font-bold text-slate-700">
                {member.employee_code}
              </span>
              <TeamStatusBadge isActive={member.is_active} employmentStatus={member.employment_status} />
            </div>

            <p className="text-xs font-semibold text-slate-500">{member.designation || "Staff Member"}</p>

            <div className="flex items-center space-x-4 text-xs font-semibold text-slate-600 pt-1">
              <a href={`mailto:${member.official_email}`} className="flex items-center hover:text-blue-600">
                <Mail size={13} className="mr-1.5 text-slate-400" />
                {member.official_email}
              </a>
              <span className="flex items-center">
                <Phone size={13} className="mr-1.5 text-slate-400" />
                {member.phone}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={() => setModalOpen(true)}
            className="flex items-center space-x-1.5 px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-bold transition-all shadow-xs"
          >
            <Edit2 size={14} />
            <span>Edit Profile</span>
          </button>
        </div>
      </div>

      {/* 3. Navigation Tabs */}
      <div className="flex border-b border-slate-200 bg-white rounded-xl overflow-hidden shadow-xs border">
        {[
          { id: "profile", label: "Profile", icon: User },
          { id: "organization", label: "Organization", icon: Building2 },
          { id: "permissions", label: "Permissions", icon: ShieldCheck },
          { id: "activity", label: "Activity Audit", icon: Activity },
          { id: "assignments", label: "Assignments", icon: Briefcase },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 border-b-2 text-xs font-bold transition-all focus:outline-none ${
                isActive
                  ? "border-blue-600 text-blue-600 bg-blue-50/30"
                  : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-50"
              }`}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* 4. Tab Content */}
      <div className="flex-1">
        
        {/* TAB 1: PROFILE */}
        {activeTab === "profile" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 pb-2">
                Personal Information
              </h3>
              <div className="grid grid-cols-2 gap-4 text-xs font-semibold">
                <div>
                  <span className="text-slate-400 block text-[10px]">First Name</span>
                  <span className="text-slate-800">{member.first_name || "—"}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Last Name</span>
                  <span className="text-slate-800">{member.last_name || "—"}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Gender</span>
                  <span className="text-slate-800">{member.gender || "Not specified"}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Date of Birth</span>
                  <span className="text-slate-800">{member.dob ? new Date(member.dob).toLocaleDateString("en-IN") : "Not specified"}</span>
                </div>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 pb-2">
                Emergency Contact Details
              </h3>
              <div className="grid grid-cols-2 gap-4 text-xs font-semibold">
                <div>
                  <span className="text-slate-400 block text-[10px]">Emergency Contact Name</span>
                  <span className="text-slate-800">{member.emergency_contact_name || "Not set"}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Emergency Phone</span>
                  <span className="text-slate-800">{member.emergency_contact_phone || "Not set"}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Personal Email</span>
                  <span className="text-slate-800">{member.personal_email || "—"}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Cloudflare R2 Avatar URL</span>
                  <span className="text-slate-500 font-mono text-[10px] truncate block">{member.avatar_url || "Default Avatar"}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ORGANIZATION */}
        {activeTab === "organization" && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-6">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 pb-2">
              Organizational Role & Hierarchy
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs font-semibold">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/60">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Designation</span>
                <span className="text-slate-800 text-sm font-bold block mt-1">{member.designation || "Staff Member"}</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/60">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Employment Type</span>
                <span className="text-slate-800 text-sm font-bold block mt-1">{member.employment_status || "Full-Time"}</span>
              </div>
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/60">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Date Joined</span>
                <span className="text-slate-800 text-sm font-bold block mt-1">
                  {member.joined_date ? new Date(member.joined_date).toLocaleDateString("en-IN") : "—"}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PERMISSIONS */}
        {activeTab === "permissions" && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Effective Permissions Matrix</h3>
                <p className="text-[11px] text-slate-400">Permissions inherited from organizational roles and user assignments.</p>
              </div>
              <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 text-[10px] font-bold rounded border border-emerald-100 flex items-center">
                <ShieldCheck size={12} className="mr-1" /> Active Authorization
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
              {[
                { module: "CRM & Leads", permissions: ["crm.read", "crm.create", "crm.update"] },
                { module: "Proposals", permissions: ["proposal.read", "proposal.create", "proposal.finalize"] },
                { module: "Bookings", permissions: ["booking.read", "booking.update"] },
                { module: "Operations", permissions: ["operations.read", "operations.assign"] },
                { module: "Finance & Payments", permissions: ["finance.read", "finance.payments.view"] },
                { module: "Master Configuration", permissions: ["master.read"] },
              ].map((group, idx) => (
                <div key={idx} className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                  <span className="text-xs font-bold text-slate-800 block">{group.module}</span>
                  <div className="space-y-1">
                    {group.permissions.map((p, i) => (
                      <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-white border border-slate-200 text-slate-600 mr-1 mb-1">
                        <CheckCircle2 size={10} className="mr-1 text-emerald-500" />
                        {p}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: ACTIVITY AUDIT */}
        {activeTab === "activity" && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 pb-2">
              Recent Login & Action Audit Trail
            </h3>
            <div className="space-y-3">
              {[
                { action: "Logged in via Web Dashboard", time: "Today at 9:30 AM", ip: "127.0.0.1 (Chrome / Windows)" },
                { action: "Updated Lead #AM-LD-2026-00002 status to ASSIGNED", time: "Yesterday at 4:15 PM", ip: "127.0.0.1 (Chrome / Windows)" },
                { action: "Created Proposal #PR-2026-0001 for client Jathin M", time: "04 Aug 2026 at 2:00 PM", ip: "127.0.0.1 (Chrome / Windows)" },
              ].map((log, idx) => (
                <div key={idx} className="flex items-start space-x-3 p-3 rounded-lg border border-slate-100 bg-slate-50/50 text-xs font-semibold">
                  <Clock size={14} className="text-blue-600 mt-0.5 shrink-0" />
                  <div className="flex-1">
                    <span className="text-slate-800 block font-bold">{log.action}</span>
                    <span className="text-[10px] text-slate-400 block">{log.time} • {log.ip}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: ASSIGNMENTS */}
        {activeTab === "assignments" && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-2 text-center">
              <span className="text-xs font-bold text-slate-400 uppercase">Assigned Active Leads</span>
              <span className="text-3xl font-extrabold text-blue-600 block">4</span>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-2 text-center">
              <span className="text-xs font-bold text-slate-400 uppercase">Managed Bookings</span>
              <span className="text-3xl font-extrabold text-emerald-600 block">2</span>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-2 text-center">
              <span className="text-xs font-bold text-slate-400 uppercase">Open Operations Tasks</span>
              <span className="text-3xl font-extrabold text-amber-600 block">7</span>
            </div>
          </div>
        )}

      </div>

      {/* Edit Modal */}
      <CreateTeamMemberModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleEditSubmit}
        isSubmitting={updateMutation.isPending}
        editingMember={member}
      />

    </div>
  );
}

export default TeamDetailPage;
