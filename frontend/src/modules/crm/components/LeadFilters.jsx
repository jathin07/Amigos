import React, { useState, useEffect } from "react";
import { Search, X, Filter } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import crmApi from "../services/crmApi";

export function LeadFilters({ activeFilters, onChange, onClearAll }) {
  const [search, setSearch] = useState(activeFilters.search || "");

  // Debounce search input changes by 300ms
  useEffect(() => {
    const handler = setTimeout(() => {
      if (search !== activeFilters.search) {
        onChange({ ...activeFilters, search, page: 1 });
      }
    }, 300);
    return () => clearTimeout(handler);
  }, [search, activeFilters.search, onChange]);

  // Sync internal search state with external prop changes
  useEffect(() => {
    setSearch(activeFilters.search || "");
  }, [activeFilters.search]);

  // Queries for lookup filter dropdown options
  const { data: statusLookup } = useQuery({
    queryKey: ["lookups", "statuses"],
    queryFn: () => crmApi.getLookups("statuses"),
    staleTime: 24 * 60 * 60 * 1000, // Caches statuses for 24h
  });

  const { data: priorityLookup } = useQuery({
    queryKey: ["lookups", "priorities"],
    queryFn: () => crmApi.getLookups("priorities"),
    staleTime: 24 * 60 * 60 * 1000,
  });

  const { data: teamLookup } = useQuery({
    queryKey: ["team-members"],
    queryFn: () => crmApi.getTeamMembers(),
    staleTime: 10 * 60 * 1000, // Caches team for 10 minutes
  });

  const statuses = statusLookup?.data || [];
  const priorities = priorityLookup?.data || [];
  const teamMembers = teamLookup?.data?.items || [];

  const handleSelectChange = (key, value) => {
    onChange({
      ...activeFilters,
      [key]: value || undefined,
      page: 1, // Reset page index on filter change
    });
  };

  const handleQuickFilter = (type) => {
    // Toggle quick filters
    const nextFilters = { ...activeFilters, page: 1 };
    
    // Clear other mutually exclusive quick parameters
    delete nextFilters.my_leads;
    delete nextFilters.today;
    delete nextFilters.overdue_followups;

    if (type) {
      nextFilters[type] = "true";
    }

    onChange(nextFilters);
  };

  const hasActiveFilters = Object.keys(activeFilters).some(
    (k) => k !== "page" && k !== "page_size" && activeFilters[k] !== undefined && activeFilters[k] !== ""
  );

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-4 shrink-0 select-none">
      
      {/* Primary filters row */}
      <div className="flex flex-col md:flex-row gap-3">
        {/* Debounced search bar */}
        <div className="relative flex-1">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={16} />
          </span>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search customer name, phone, lead number..."
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-slate-700 font-medium"
          />
        </div>

        {/* Dropdowns filters grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 md:w-auto">
          {/* Status Select */}
          <select
            value={activeFilters.status_id || ""}
            onChange={(e) => handleSelectChange("status_id", e.target.value)}
            className="px-2.5 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
          >
            <option value="">All Statuses</option>
            {statuses.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>

          {/* Priority Select */}
          <select
            value={activeFilters.priority_id || ""}
            onChange={(e) => handleSelectChange("priority_id", e.target.value)}
            className="px-2.5 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold"
          >
            <option value="">All Priorities</option>
            {priorities.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          {/* Owner/Team Member Select */}
          <select
            value={activeFilters.owner_id || ""}
            onChange={(e) => handleSelectChange("owner_id", e.target.value)}
            className="px-2.5 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 font-semibold col-span-2 sm:col-span-1"
          >
            <option value="">All Owners</option>
            {teamMembers.map((m) => (
              <option key={m.id} value={m.id}>
                {m.display_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Clear Filters CTA */}
      {hasActiveFilters && (
        <div className="flex items-center justify-end pt-2 border-t border-slate-100 text-xs font-semibold">
          <button
            onClick={onClearAll}
            className="text-blue-600 hover:text-blue-800 transition-colors flex items-center space-x-1 py-1"
          >
            <X size={14} />
            <span>Reset Filters</span>
          </button>
        </div>
      )}

    </div>
  );
}

export default LeadFilters;
