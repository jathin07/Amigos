import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useProposalDetail, useFinalizeProposal } from "../hooks/useProposal";
import { useProposalVersions } from "../hooks/useProposalVersions";
import proposalApi from "../services/proposalApi";
import ProposalStatusBadge from "../components/ProposalStatusBadge";
import FinalizeProposalModal from "../modals/FinalizeProposalModal";
import { 
  ArrowLeft, 
  ChevronRight, 
  Calendar, 
  MapPin, 
  DollarSign, 
  FileCheck, 
  FileText, 
  Clock, 
  Settings, 
  Edit2, 
  Compass, 
  AlertTriangle,
  History,
  Plane,
  Home as HomeIcon,
  Coffee,
  Plus,
  Share2,
  Copy,
  Check
} from "lucide-react";

export function ProposalDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isFinalizeOpen, setIsFinalizeOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("itinerary");
  const [copied, setCopied] = useState(false);

  const handleCopySummary = () => {
    if (!proposal) return;
    const daysSummary = (proposal.structured_itinerary?.days || []).map((d, i) => 
      `Day ${i + 1}: ${d.title || 'Sightseeing'}${d.hotelName ? ` | Stay: ${d.hotelName}` : ''}`
    ).join('\n');

    const shareText = `📋 *${proposal.proposal_title || 'Travel Quotation'}*
PR Reference: PR-${proposal.id.slice(0, 8)}
Selling Price: INR ${proposal.total_amount ? Number(proposal.total_amount).toLocaleString('en-IN') : 'Flexible'}
Price / Person: INR ${proposal.price_per_person ? Number(proposal.price_per_person).toLocaleString('en-IN') : 'Flexible'}
Valid Until: ${proposal.valid_until ? new Date(proposal.valid_until).toLocaleDateString('en-IN') : 'Flexible'}

*Itinerary Highlights:*
${daysSummary || 'Custom day-by-day travel plan'}

Shared via Amigos Tourism ERP`;

    navigator.clipboard.writeText(shareText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  // Queries
  const { data: proposalResponse, isLoading, error } = useProposalDetail(id);
  const proposal = proposalResponse?.data;

  const { data: versionsResponse } = useProposalVersions(proposal?.lead_id);
  const versions = versionsResponse?.data || [];

  const { data: teamLookup } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => proposalApi.getTeamMembers(),
    enabled: !!proposal,
  });
  const teamMembers = teamLookup?.data?.items || [];

  // Mutations
  const finalizeMutation = useFinalizeProposal(id);

  const handleFinalize = async (payload, callback) => {
    try {
      let currentVersion = proposal.row_version;
      if (proposal.status?.code !== "APPROVED") {
        const statusesRes = await proposalApi.getProposalStatuses();
        const approvedStatus = statusesRes?.data?.find((s) => s.code === "APPROVED");
        if (approvedStatus) {
          const updateRes = await proposalApi.updateProposal(id, {
            row_version: currentVersion,
            status_id: approvedStatus.id,
          });
          if (updateRes?.data?.row_version) {
            currentVersion = updateRes.data.row_version;
          }
        }
      }
      finalizeMutation.mutate({
        ...payload,
        row_version: currentVersion,
      }, {
        onSuccess: () => {
          callback();
          setIsFinalizeOpen(false);
        },
      });
    } catch (err) {
      alert(err?.response?.data?.message || "Failed to approve and finalize proposal.");
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4">
        <Compass className="animate-spin text-blue-600" size={40} />
        <p className="text-xs font-semibold text-slate-600">Loading proposal file...</p>
      </div>
    );
  }

  if (error || !proposal) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4 select-none">
        <AlertTriangle className="text-rose-500" size={40} />
        <p className="text-sm font-semibold text-slate-800">Proposal File Not Found</p>
        <p className="text-xs text-slate-400">The requested quotation is invalid or does not exist.</p>
        <button
          onClick={() => navigate("/admin/proposals")}
          className="px-4 py-2 border border-slate-200 rounded-lg text-xs font-bold text-slate-700 bg-white hover:bg-slate-50 transition-colors"
        >
          Return to Proposals
        </button>
      </div>
    );
  }

  const manager = teamMembers.find((m) => m.id === proposal.approved_by_team_member_id);

  // If structured itinerary exists, extract it. Otherwise fallback to destinations table.
  const structuredDays = proposal.structured_itinerary?.days || [];
  const destinations = proposal.destinations || [];

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* 1. Header Toolbar */}
      <div className="flex items-start justify-between flex-wrap gap-4 shrink-0 pb-4 border-b border-slate-100">
        <div className="space-y-2">
          {/* Breadcrumbs */}
          <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1.5">
            <button onClick={() => navigate("/admin/proposals")} className="hover:text-slate-600 transition-colors">
              Proposals
            </button>
            <ChevronRight size={10} className="text-slate-300" />
            <span className="text-slate-500 font-bold">PR-{proposal.id.slice(0, 8)}</span>
          </div>

          <div className="flex items-center space-x-3 flex-wrap gap-2">
            <h1 className="text-xl font-bold text-slate-800 tracking-tight">
              {proposal.proposal_title || "Untitled Trip Itinerary"}
            </h1>
            <ProposalStatusBadge status={proposal.status} />
            {proposal.is_final && (
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-50 border border-emerald-100 text-emerald-700">
                Finalized
              </span>
            )}
          </div>

          <p className="text-[10px] text-slate-400 font-semibold">
            Version revision: <span className="text-slate-600 font-bold">v{proposal.version}</span> • Valid until:{" "}
            {proposal.valid_until ? new Date(proposal.valid_until).toLocaleDateString("en-IN") : "Flexible Date"}
          </p>
        </div>

        {/* Global Actions */}
        <div className="flex items-center space-x-2 flex-wrap gap-2">
          <button
            onClick={handleCopySummary}
            className="flex items-center space-x-1.5 px-3 py-2 border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-bold text-slate-700 transition-all focus:outline-none"
            title="Copy formatted quotation for WhatsApp or Email"
          >
            {copied ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} className="text-blue-600" />}
            <span>{copied ? "Copied to Clipboard!" : "Copy Quotation Text"}</span>
          </button>

          {!proposal.is_final && (
            <>
              <button
                onClick={() => navigate(`/admin/proposals/${proposal.id}/edit`)}
                className="flex items-center space-x-1.5 px-3.5 py-2 border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-bold text-slate-700 transition-all focus:outline-none"
              >
                <Edit2 size={14} />
                <span>Edit Itinerary</span>
              </button>
              <button
                onClick={() => setIsFinalizeOpen(true)}
                className="flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-md shadow-emerald-500/10 transition-colors focus:outline-none"
              >
                <FileCheck size={14} />
                <span>Finalize & Lock</span>
              </button>
            </>
          )}
          {proposal.is_final && (
            <button
              onClick={() => window.print()}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-md shadow-blue-500/10 transition-colors focus:outline-none"
            >
              <FileText size={14} />
              <span>Print Quotation</span>
            </button>
          )}
        </div>
      </div>

      {/* 2. Selling Price & Stats overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 shrink-0">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-blue-50 border border-blue-100 text-blue-600 rounded-xl">
            <DollarSign size={20} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Selling Price</p>
            <p className="text-base font-black text-slate-800 mt-0.5">
              {proposal.total_amount ? `INR ${parseFloat(proposal.total_amount).toLocaleString("en-IN")}` : "Flexible Price"}
            </p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-xl">
            <DollarSign size={20} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Price per Person (PP)</p>
            <p className="text-base font-black text-slate-800 mt-0.5">
              {proposal.price_per_person ? `INR ${parseFloat(proposal.price_per_person).toLocaleString("en-IN")}` : "Flexible Price"}
            </p>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-slate-50 border border-slate-150 text-slate-600 rounded-xl">
            <Calendar size={20} />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Quotation Validity</p>
            <p className="text-sm font-bold text-slate-800 mt-1">
              {proposal.valid_until ? `Until ${new Date(proposal.valid_until).toLocaleDateString("en-IN")}` : "No expiry date"}
            </p>
          </div>
        </div>
      </div>

      {/* 3. Main Workspace split */}
      <div className="flex-1 flex flex-col min-h-0 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200 bg-slate-50 shrink-0">
          {[
            { id: "itinerary", name: "Day-by-Day Itinerary", icon: Compass },
            { id: "destinations", name: "Travel Routes", icon: MapPin },
            { id: "versions", name: "Revision History", icon: History },
          ].map((tab) => {
            const Icon = tab.icon;
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

        {/* Tab Body */}
        <div className="flex-1 overflow-y-auto p-6 min-h-0 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
          
          {/* Itinerary Tab */}
          {activeTab === "itinerary" && (
            <div className="space-y-6">
              {structuredDays.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
                  <Compass className="mx-auto text-slate-400 mb-2" size={24} />
                  <p className="text-xs font-semibold text-slate-800">No day schedules logged</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">Edit this proposal to add day plans, activities, and hotels.</p>
                </div>
              ) : (
                structuredDays.map((day, idx) => (
                  <div key={idx} className="bg-slate-50/50 border border-slate-200 rounded-xl p-5 space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-200 flex-wrap gap-2">
                      <h4 className="text-xs font-bold text-slate-800 flex items-center">
                        <span className="bg-blue-600 text-white w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-black mr-2">
                          {idx + 1}
                        </span>
                        {day.title || `Day ${idx + 1}`}
                      </h4>
                      {day.overnightStay && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 border border-amber-100 text-amber-700 flex items-center">
                          <HomeIcon size={10} className="mr-1" />
                          Overnight Stay
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-semibold text-slate-600">
                      {/* Hotel */}
                      {day.hotel && (
                        <div className="flex items-start space-x-2 bg-white border border-slate-200 rounded-lg p-2.5">
                          <HomeIcon size={14} className="text-blue-500 shrink-0 mt-0.5" />
                          <div>
                            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Accommodation</p>
                            <p className="text-slate-800 mt-0.5">{day.hotel.name || day.hotel}</p>
                          </div>
                        </div>
                      )}

                      {/* Transport */}
                      {day.transport && (
                        <div className="flex items-start space-x-2 bg-white border border-slate-200 rounded-lg p-2.5">
                          <Plane size={14} className="text-purple-500 shrink-0 mt-0.5" />
                          <div>
                            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Transfer Mode</p>
                            <p className="text-slate-800 mt-0.5">{day.transport.name || day.transport}</p>
                          </div>
                        </div>
                      )}

                      {/* Meals */}
                      {day.meals && (
                        <div className="flex items-start space-x-2 bg-white border border-slate-200 rounded-lg p-2.5">
                          <Coffee size={14} className="text-emerald-500 shrink-0 mt-0.5" />
                          <div>
                            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Meal Inclusion</p>
                            <p className="text-slate-800 mt-0.5">{day.meals.join(", ") || day.meals}</p>
                          </div>
                        </div>
                      )}
                    </div>

                    {day.activities && (
                      <div className="text-xs space-y-1.5 font-semibold text-slate-600 pl-1">
                        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Sightseeing / Activities</p>
                        <p className="text-slate-800 leading-relaxed">{day.activities}</p>
                      </div>
                    )}

                    {day.notes && (
                      <div className="text-xs space-y-1 bg-white border border-slate-200 rounded-lg p-3 font-semibold text-slate-500 italic">
                        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider not-italic">Coordinators Notes</p>
                        <p className="leading-relaxed">"{day.notes}"</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Destinations Routes Tab */}
          {activeTab === "destinations" && (
            <div className="space-y-4">
              {destinations.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
                  <MapPin className="mx-auto text-slate-400 mb-2" size={24} />
                  <p className="text-xs font-semibold text-slate-800">No destinations mapped</p>
                </div>
              ) : (
                <div className="relative pl-6 border-l border-slate-200 space-y-6 pt-2 select-none text-xs">
                  {destinations.map((d, index) => (
                    <div key={d.id} className="relative">
                      {/* Node Icon */}
                      <div className="absolute -left-[35px] top-0 w-7 h-7 rounded-full border border-blue-200 bg-blue-50 flex items-center justify-center text-blue-700 font-black">
                        {index + 1}
                      </div>

                      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800 text-sm">
                            {d.destination_name || "Destination"}
                          </span>
                          {d.overnight_stay && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-50 border border-amber-100 text-amber-700 uppercase">
                              Overnight stay
                            </span>
                          )}
                        </div>

                        {d.day_title && <p className="font-bold text-slate-600 mt-1">{d.day_title}</p>}
                        
                        {(d.travel_mode || d.distance) && (
                          <div className="flex items-center space-x-3 text-slate-400 text-[10px] font-semibold mt-1">
                            {d.travel_mode && <span>Mode: {d.travel_mode}</span>}
                            {d.travel_time && <span>Time: {d.travel_time}</span>}
                            {d.distance && <span>Dist: {d.distance} km</span>}
                          </div>
                        )}

                        {d.notes && <p className="text-slate-500 font-semibold italic mt-2">"{d.notes}"</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Revision Versions history Tab */}
          {activeTab === "versions" && (
            <div className="space-y-4">
              {versions.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
                  <History className="mx-auto text-slate-400 mb-2" size={24} />
                  <p className="text-xs font-semibold text-slate-800">No revisions logged</p>
                </div>
              ) : (
                <div className="border border-slate-200 rounded-xl overflow-hidden shadow-sm text-xs select-none">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px]">
                      <tr>
                        <th className="px-4 py-3">Version</th>
                        <th className="px-4 py-3">Proposal Title</th>
                        <th className="px-4 py-3">Total Amount</th>
                        <th className="px-4 py-3">Created Date</th>
                        <th className="px-4 py-3">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-semibold text-slate-600 bg-white">
                      {versions.map((ver) => (
                        <tr key={ver.id} className="hover:bg-slate-50/70 transition-colors">
                          <td className="px-4 py-3.5">
                            <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 font-bold">
                              v{ver.version}
                            </span>
                          </td>
                          <td className="px-4 py-3.5 text-slate-800 font-bold">{ver.proposal_title}</td>
                          <td className="px-4 py-3.5">
                            {ver.total_amount ? `INR ${parseFloat(ver.total_amount).toLocaleString("en-IN")}` : "—"}
                          </td>
                          <td className="px-4 py-3.5">
                            {ver.created_at ? new Date(ver.created_at).toLocaleDateString("en-IN") : ""}
                          </td>
                          <td className="px-4 py-3.5">
                            <button
                              onClick={() => navigate(`/admin/proposals/${ver.id}`)}
                              className="text-blue-600 hover:text-blue-800"
                              disabled={ver.id === proposal.id}
                            >
                              {ver.id === proposal.id ? "Viewing Now" : "View revision"}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

        </div>

      </div>

      {/* Freeze & Finalize Modal */}
      <FinalizeProposalModal
        isOpen={isFinalizeOpen}
        onClose={() => setIsFinalizeOpen(false)}
        onFinalize={handleFinalize}
        isSubmitting={finalizeMutation.isPending}
        rowVersion={proposal.row_version}
      />

    </div>
  );
}

export default ProposalDetailPage;
