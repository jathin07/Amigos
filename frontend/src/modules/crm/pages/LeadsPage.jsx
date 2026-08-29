import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Eye, Edit2, CheckCircle2, Trash2, CalendarDays, RefreshCw } from "lucide-react";
import { useLeads, useCreateLead } from "../hooks/useLeads";
import { useDeleteLead } from "../hooks/useLeadDetail";
import LeadFilters from "../components/LeadFilters";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import CreateLeadModal from "../modals/CreateLeadModal";
import { LeadStatusBadge, LeadPriorityBadge } from "../components/LeadStatusBadge";
import PageHeader from "../../../components/ui/PageHeader";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export function LeadsPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
    status_id: "",
    priority_id: "",
    owner_id: "",
  });

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);

  // Queries and mutations
  const { data: leadsResponse, isLoading, isFetching, refetch } = useLeads(filters);
  const createLeadMutation = useCreateLead();
  const deleteLeadMutation = useDeleteLead();

  const leads = leadsResponse?.data || [];
  const meta = leadsResponse?.meta || { page: 1, page_size: 10, total_records: 0 };

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const handleFiltersChange = (nextFilters) => {
    setFilters(nextFilters);
  };

  const handleClearFilters = () => {
    setFilters({
      page: 1,
      page_size: filters.page_size,
      search: "",
      status_id: "",
      priority_id: "",
      owner_id: "",
    });
  };

  const handleCreateLead = (payload, callback) => {
    createLeadMutation.mutate(payload, {
      onSuccess: () => {
        callback();
      },
    });
  };

  const confirmDeleteLead = () => {
    if (deleteTargetId) {
      deleteLeadMutation.mutate(deleteTargetId, {
        onSettled: () => setDeleteTargetId(null),
      });
    }
  };

  const columns = [
    {
      header: "Lead No.",
      accessorKey: "lead_number",
      render: (row, val) => (
        <button
          onClick={() => navigate(`/admin/crm/leads/${row.id}`)}
          className="text-blue-600 hover:text-blue-800 hover:underline font-bold text-xs"
        >
          {val}
        </button>
      ),
    },
    {
      header: "Customer",
      render: (row) => (
        <div>
          <p className="font-semibold text-slate-800">{row.contact_person?.name || "—"}</p>
          <p className="text-[10px] text-slate-400 mt-0.5">{row.contact_person?.phone || "—"}</p>
        </div>
      ),
    },
    {
      header: "Travel Plan",
      render: (row) => (
        <div>
          <p className="font-semibold text-slate-700">
            {row.traveler_count ? `${row.traveler_count} Traveler${row.traveler_count > 1 ? 's' : ''}` : "—"}
          </p>
          <p className="text-[10px] text-slate-400 flex items-center mt-0.5">
            <CalendarDays size={10} className="mr-1 text-slate-400" />
            {row.travel_start_date ? `${row.travel_start_date} to ${row.travel_end_date}` : "Flexible Dates"}
          </p>
        </div>
      ),
    },
    {
      header: "Source",
      render: (row) => row.lead_source?.name || "—",
    },
    {
      header: "Status",
      render: (row) => <LeadStatusBadge status={row.current_status} />,
    },
    {
      header: "Priority",
      render: (row) => <LeadPriorityBadge priority={row.priority} />,
    },
    {
      header: "Expected Value",
      render: (row) => row.budget ? `INR ${parseFloat(row.budget).toLocaleString()}` : "—",
    },
    {
      header: "Created Date",
      render: (row) => {
        if (!row.created_at) return "—";
        const date = new Date(row.created_at);
        return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
      },
    },
    {
      header: "Actions",
      className: "text-right",
      render: (row) => (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => navigate(`/admin/crm/leads/${row.id}`)}
            className="p-1 rounded text-slate-500 hover:text-blue-600 hover:bg-slate-100 transition-colors"
            title="View Details"
          >
            <Eye size={14} />
          </button>
          {row.current_status?.code !== "WON" && row.current_status?.code !== "LOST" && (
            <button
              onClick={() => navigate(`/admin/crm/leads/${row.id}`)}
              className="p-1 rounded text-slate-500 hover:text-emerald-600 hover:bg-slate-100 transition-colors"
              title="Convert Lead"
            >
              <CheckCircle2 size={14} />
            </button>
          )}
          <button
            onClick={() => setDeleteTargetId(row.id)}
            className="p-1 rounded text-slate-500 hover:text-red-600 hover:bg-slate-100 transition-colors"
            title="Delete Lead"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5 flex flex-col h-full select-none">
      
      {/* Standardized Page Header */}
      <PageHeader
        breadcrumbs={[
          { label: "CRM Workspace", href: "/admin/crm/leads" },
          { label: "Leads Directory" },
        ]}
        title="Customer Sales Leads"
        description="Manage customer enquiries, travel plans, status updates, and booking conversions."
        actions={
          <>
            <button
              onClick={() => refetch()}
              className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 focus:outline-none transition-colors"
              title="Refresh leads list"
            >
              <RefreshCw size={14} className={isFetching ? "animate-spin text-blue-600" : ""} />
            </button>
            <button
              onClick={() => setIsCreateOpen(true)}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors focus:outline-none"
            >
              <Plus size={14} />
              <span>Intake New Lead</span>
            </button>
          </>
        }
      />

      {/* Filtering Panel */}
      <LeadFilters
        activeFilters={filters}
        onChange={handleFiltersChange}
        onClearAll={handleClearFilters}
      />

      {/* Main Table view */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={leads}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total_records}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle="No sales leads on file"
          emptyStateDescription="Enquiries logged via website, Instagram, and walk-ins will list here."
          emptyStateAction={
            <button
              onClick={() => setIsCreateOpen(true)}
              className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow-sm"
            >
              Log First Lead
            </button>
          }
        />
      </div>

      {/* Intake Lead Modal */}
      <CreateLeadModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateLead}
        isSubmitting={createLeadMutation.isPending}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={!!deleteTargetId}
        onClose={() => setDeleteTargetId(null)}
        onConfirm={confirmDeleteLead}
        title="Delete Sales Lead?"
        message="Are you sure you want to remove this lead record? Pending follow-ups will be cancelled."
        confirmLabel="Delete Lead"
        variant="danger"
        isLoading={deleteLeadMutation.isPending}
      />

    </div>
  );
}

export default LeadsPage;
