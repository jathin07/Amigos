import React from "react";
import { User, Phone, Mail, MapPin, Calendar, Users, DollarSign, Share2, Shield, CalendarDays } from "lucide-react";
import { LeadStatusBadge, LeadPriorityBadge } from "./LeadStatusBadge";

export function LeadOverview({ lead, teamMembers = [] }) {
  const owner = teamMembers.find((m) => m.id === lead.owner_team_member_id);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 select-none">
      
      {/* 1. Customer Information Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-100 flex items-center">
          <User size={12} className="mr-1.5 text-blue-500" />
          Customer Contact
        </h3>

        <div className="space-y-3 text-xs">
          <div>
            <p className="text-slate-400 font-semibold uppercase text-[9px] mb-0.5">Primary Contact</p>
            <p className="font-bold text-slate-800 text-sm">{lead.contact_person?.name || "—"}</p>
            {lead.contact_person?.designation && (
              <p className="text-[10px] text-slate-400 italic mt-0.5">{lead.contact_person.designation}</p>
            )}
          </div>

          <div className="flex items-center space-x-2 text-slate-600">
            <Phone size={14} className="text-slate-400 shrink-0" />
            <span className="font-semibold">{lead.contact_person?.phone || "—"}</span>
          </div>

          {lead.contact_person?.alternate_phone && (
            <div className="flex items-center space-x-2 text-slate-600 pl-5 text-[11px]">
              <span className="text-slate-400">Alt:</span>
              <span className="font-semibold">{lead.contact_person.alternate_phone}</span>
            </div>
          )}

          <div className="flex items-center space-x-2 text-slate-600">
            <Mail size={14} className="text-slate-400 shrink-0" />
            <span className="font-semibold truncate">{lead.contact_person?.email || "—"}</span>
          </div>

          {lead.contact_person?.preferred_contact_method && (
            <div className="pt-2 border-t border-slate-100 text-[10px] text-slate-500 font-semibold">
              <span className="text-slate-400 mr-1.5">Contact Preference:</span>
              <span className="px-2 py-0.5 rounded bg-slate-50 border border-slate-100 text-slate-700">
                {lead.contact_person.preferred_contact_method}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Travel Requirements Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-100 flex items-center">
          <MapPin size={12} className="mr-1.5 text-blue-500" />
          Requirements
        </h3>

        <div className="space-y-3 text-xs">
          <div>
            <p className="text-slate-400 font-semibold uppercase text-[9px] mb-0.5">Destinations</p>
            <div className="flex flex-wrap gap-1 mt-1">
              {lead.destinations?.length > 0 ? (
                lead.destinations.map((d) => (
                  <span
                    key={d.id}
                    className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 border border-blue-100 text-blue-700"
                  >
                    {d.name}
                  </span>
                ))
              ) : (
                <span className="text-slate-500 font-medium">No destinations linked</span>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2 text-slate-600">
            <Calendar size={14} className="text-slate-400 shrink-0" />
            <div>
              <p className="font-semibold">
                {lead.travel_start_date ? `${lead.travel_start_date} to ${lead.travel_end_date}` : (lead.estimated_trip_days ? `${lead.estimated_trip_days} Days Trip (Flexible)` : "Flexible Travel Date")}
              </p>
              {lead.expected_travel_date && !lead.travel_start_date && (
                <p className="text-[10px] text-slate-400 italic mt-0.5">Expected: {lead.expected_travel_date}</p>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2 text-slate-600">
            <Users size={14} className="text-slate-400 shrink-0" />
            <span className="font-semibold">
              {lead.traveler_count || 1} Travelers
              {lead.male_count || lead.female_count || lead.faculty_count ? (
                <span className="text-[10px] text-slate-400 font-medium ml-1.5">
                  ({lead.male_count || 0}M / {lead.female_count || 0}F / {lead.faculty_count || 0}Fac)
                </span>
              ) : null}
            </span>
          </div>

          <div className="flex items-center space-x-2 text-slate-600">
            <DollarSign size={14} className="text-slate-400 shrink-0" />
            <span className="font-bold text-slate-800">
              {lead.budget ? `INR ${parseFloat(lead.budget).toLocaleString("en-IN")}` : "Flexible Budget"}
            </span>
          </div>

          {lead.package && (
            <div className="pt-2 border-t border-slate-100 text-[10px] text-slate-500 font-semibold">
              <span className="text-slate-400 mr-1.5">Selected Package:</span>
              <span className="text-slate-700 font-bold">{lead.package.title}</span>
            </div>
          )}

          {lead.notes && (
            <div className="pt-2 border-t border-slate-100">
              <p className="text-slate-400 font-semibold uppercase text-[9px] mb-1">Notes & Requests</p>
              <p className="text-[11px] text-slate-600 leading-relaxed whitespace-pre-wrap">{lead.notes}</p>
            </div>
          )}
        </div>
      </div>

      {/* 3. Lead Ownership & Metadata Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider pb-2 border-b border-slate-100 flex items-center">
          <Shield size={12} className="mr-1.5 text-blue-500" />
          Lead Metadata
        </h3>

        <div className="space-y-3 text-xs">
          <div>
            <p className="text-slate-400 font-semibold uppercase text-[9px] mb-1">Ownership Handler</p>
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-500 text-[10px]">
                {owner ? owner.display_name.split(" ").map(p => p[0]).join("").toUpperCase().slice(0, 2) : "UN"}
              </div>
              <div>
                <p className="font-bold text-slate-800">{owner?.display_name || "Unassigned"}</p>
                <p className="text-[10px] text-slate-400 mt-0.5">{owner?.official_email || "Not allocated yet"}</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-slate-600">
            <Share2 size={14} className="text-slate-400 shrink-0" />
            <div>
              <p className="text-slate-400 font-semibold uppercase text-[9px] mb-0.5">Enquiry Source</p>
              <p className="font-semibold text-slate-800">{lead.lead_source?.name || "—"}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-100">
            <div>
              <p className="text-slate-400 font-semibold uppercase text-[9px] mb-1">Status</p>
              <LeadStatusBadge status={lead.current_status} />
            </div>

            <div>
              <p className="text-slate-400 font-semibold uppercase text-[9px] mb-1">Priority</p>
              <LeadPriorityBadge priority={lead.priority} />
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

export default LeadOverview;
