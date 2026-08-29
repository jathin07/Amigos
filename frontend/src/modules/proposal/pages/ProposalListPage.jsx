import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useProposals, useDeleteProposal } from "../hooks/useProposal";
import proposalApi from "../services/proposalApi";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import ProposalStatusBadge from "../components/ProposalStatusBadge";
import { Eye, Edit2, Trash2, CalendarDays, User, Plus, Search, Filter, X } from "lucide-react";

export function ProposalListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
    status: "",
  });

  const [searchInput, setSearchInput] = useState("");

  // Sync debounced search input
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  // Queries
  const { data: proposalsResponse, isLoading, isFetching } = useProposals(filters);
  const { data: statusLookup } = useQuery({
    queryKey: ["proposal-lookups", "statuses"],
    queryFn: () => proposalApi.getProposalStatuses(),
  });
  const deleteProposalMutation = useDeleteProposal();

  const proposals = proposalsResponse?.data || [];
  const meta = proposalsResponse?.meta || { page: 1, page_size: 10, total_records: 0 };
  const statuses = statusLookup?.data || [];

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const handleStatusChange = (statusVal) => {
    setFilters((prev) => ({ ...prev, status: statusVal || "", page: 1 }));
  };

  const handleResetFilters = () => {
    setSearchInput("");
    setFilters({
      page: 1,
      page_size: filters.page_size,
      search: "",
      status: "",
    });
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to archive this proposal?")) {
      deleteProposalMutation.mutate(id);
    }
  };

  const columns = [
    {
      header: "Proposal No.",
      accessorKey: "id",
      render: (row) => (
        <button
          onClick={() => navigate(`/admin/proposals/${row.id}`)}
          className="text-blue-600 hover:text-blue-800 hover:underline font-bold text-xs"
        >
          {row.proposal_title ? `${row.proposal_title.slice(0, 18)} (v${row.version})` : `PR-${row.id.slice(0, 8)}`}
        </button>
      ),
    },
    {
      header: "Lead Reference",
      render: (row) => (
        <button
          onClick={() => navigate(`/admin/crm/leads/${row.lead_id}`)}
          className="text-left group"
        >
          <span className="block text-blue-600 group-hover:underline text-xs font-bold">
            {row.lead_number || `Lead-${row.lead_id.slice(0, 8)}`}
          </span>
          {row.customer_name && (
            <span className="block text-[10px] text-slate-400 font-medium">
              {row.customer_name}
            </span>
          )}
        </button>
      ),
    },
    {
      header: "Selling Price",
      render: (row) => (
        <span className="font-bold text-slate-800">
          {row.total_amount ? `INR ${parseFloat(row.total_amount).toLocaleString("en-IN")}` : "—"}
        </span>
      ),
    },
    {
      header: "Per Person",
      render: (row) => (
        <span className="text-slate-600 font-semibold">
          {row.price_per_person ? `INR ${parseFloat(row.price_per_person).toLocaleString("en-IN")}` : "—"}
        </span>
      ),
    },
    {
      header: "Validity",
      render: (row) => {
        if (!row.valid_until) return "Flexible";
        const date = new Date(row.valid_until);
        return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
      },
    },
    {
      header: "Status",
      render: (row) => <ProposalStatusBadge status={row.status} />,
    },
    {
      header: "Revision Details",
      render: (row) => (
        <div>
          <span className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 text-[10px] font-bold">
            Ver: {row.version}
          </span>
          {row.is_final && (
            <span className="ml-1 px-1.5 py-0.5 rounded bg-emerald-50 border border-emerald-100 text-emerald-700 text-[10px] font-bold">
              Finalized
            </span>
          )}
        </div>
      ),
    },
    {
      header: "Actions",
      className: "text-right",
      render: (row) => (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => navigate(`/admin/proposals/${row.id}`)}
            className="p-1 rounded text-slate-500 hover:text-blue-600 hover:bg-slate-100 transition-colors"
            title="View Details"
          >
            <Eye size={14} />
          </button>
          {!row.is_final && (
            <button
              onClick={() => navigate(`/admin/proposals/${row.id}/edit`)}
              className="p-1 rounded text-slate-500 hover:text-emerald-600 hover:bg-slate-100 transition-colors"
              title="Edit Proposal"
            >
              <Edit2 size={14} />
            </button>
          )}
          <button
            onClick={() => handleDelete(row.id)}
            className="p-1 rounded text-slate-500 hover:text-red-600 hover:bg-slate-100 transition-colors"
            title="Delete Proposal"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ),
    },
  ];

  const hasActiveFilters = searchInput !== "" || filters.status !== "";

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 shrink-0">
        <div>
          <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
            <span>Quotations Workspace</span>
            <span>/</span>
            <span className="text-slate-500">Proposal list</span>
          </div>
          <h1 className="text-xl font-bold text-slate-800 tracking-tight mt-1">Quotations Directory</h1>
        </div>
        <button
          onClick={() => navigate("/admin/crm/leads")}
          className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-md shadow-blue-500/10 transition-colors focus:outline-none"
        >
          <Plus size={14} />
          <span>New Proposal (via Lead File)</span>
        </button>
      </div>

      {/* Filter panel */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3 shrink-0">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
              <Search size={16} />
            </span>
            <input
              type="search"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search proposal title, lead UUID reference..."
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-slate-700 font-semibold"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Filter size={14} className="text-slate-400" />
            <select
              value={filters.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none font-semibold"
            >
              <option value="">All Statuses</option>
              {statuses.map((s) => (
                <option key={s.id} value={s.code}>
                  {s.name}
                </option>
              ))}
            </select>

            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                className="text-blue-600 hover:text-blue-800 transition-colors flex items-center space-x-1 py-1 text-xs font-semibold"
              >
                <X size={14} />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Table view */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={proposals}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total_records}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle="No proposals registered"
          emptyStateDescription="Travel price sheets and day-by-day itineraries are designed and finalized here."
        />
      </div>

    </div>
  );
}

export default ProposalListPage;
