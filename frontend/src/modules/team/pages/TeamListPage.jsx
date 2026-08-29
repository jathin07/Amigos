import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTeamMembers, useCreateTeamMember, useUpdateTeamMember, useDeleteTeamMember } from "../hooks/useTeam";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import TeamStatusBadge from "../components/TeamStatusBadge";
import CreateTeamMemberModal from "../modals/CreateTeamMemberModal";
import { Users, Plus, Search, Filter, RefreshCw, Eye, Edit2, Trash2, Mail, Phone, UserCheck, X } from "lucide-react";
import PageHeader from "../../../components/ui/PageHeader";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export function TeamListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
    is_active: undefined,
  });

  const [searchInput, setSearchInput] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [deleteTargetMember, setDeleteTargetMember] = useState(null);

  // Debounced search
  useEffect(() => {
    const handler = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  // Queries & Mutations
  const { data: teamResponse, isLoading, isFetching, refetch } = useTeamMembers(filters);
  const createMutation = useCreateTeamMember();
  const updateMutation = useUpdateTeamMember(editingMember?.id);
  const deleteMutation = useDeleteTeamMember();

  const members = teamResponse?.data?.items || [];
  const meta = teamResponse?.data?.pagination || { page: 1, page_size: 10, total_records: 0 };

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const handleCreateNew = () => {
    setEditingMember(null);
    setModalOpen(true);
  };

  const handleEdit = (member) => {
    setEditingMember(member);
    setModalOpen(true);
  };

  const confirmDeleteMember = () => {
    if (deleteTargetMember) {
      deleteMutation.mutate(deleteTargetMember.id, {
        onSettled: () => setDeleteTargetMember(null),
      });
    }
  };

  const handleFormSubmit = (payload, callback) => {
    if (editingMember) {
      updateMutation.mutate({
        ...payload,
        version: editingMember.version,
      }, {
        onSuccess: () => {
          callback();
          setModalOpen(false);
        },
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: () => {
          callback();
          setModalOpen(false);
        },
      });
    }
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

  const columns = [
    {
      header: "Staff Member",
      accessorKey: "display_name",
      render: (row) => (
        <div className="flex items-center space-x-3">
          {row.avatar_url ? (
            <img src={row.avatar_url} alt={row.display_name} className="w-8 h-8 rounded-full object-cover border border-slate-200" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
              {getInitials(row.display_name)}
            </div>
          )}
          <div>
            <button
              onClick={() => navigate(`/admin/team/${row.id}`)}
              className="font-bold text-slate-800 hover:text-blue-600 hover:underline text-xs block text-left"
            >
              {row.display_name}
            </button>
            <span className="text-[10px] text-slate-400 font-semibold">{row.designation || "Staff Member"}</span>
          </div>
        </div>
      ),
    },
    {
      header: "Employee ID",
      accessorKey: "employee_code",
      render: (row) => (
        <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 font-mono text-[10px] font-bold">
          {row.employee_code}
        </span>
      ),
    },
    {
      header: "Official Email",
      accessorKey: "official_email",
      render: (row) => (
        <a href={`mailto:${row.official_email}`} className="text-xs text-slate-600 hover:text-blue-600 font-semibold flex items-center">
          <Mail size={12} className="mr-1.5 text-slate-400" />
          {row.official_email}
        </a>
      ),
    },
    {
      header: "Phone",
      accessorKey: "phone",
      render: (row) => (
        <span className="text-xs text-slate-600 font-semibold flex items-center">
          <Phone size={12} className="mr-1.5 text-slate-400" />
          {row.phone}
        </span>
      ),
    },
    {
      header: "Status",
      render: (row) => <TeamStatusBadge isActive={row.is_active} employmentStatus={row.employment_status} />,
    },
    {
      header: "Actions",
      className: "text-right",
      render: (row) => (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => navigate(`/admin/team/${row.id}`)}
            className="p-1 rounded text-slate-500 hover:text-blue-600 hover:bg-slate-100 transition-colors"
            title="View Profile Workspace"
          >
            <Eye size={14} />
          </button>
          <button
            onClick={() => handleEdit(row)}
            className="p-1 rounded text-slate-500 hover:text-emerald-600 hover:bg-slate-100 transition-colors"
            title="Edit Staff Member"
          >
            <Edit2 size={14} />
          </button>
          <button
            onClick={() => setDeleteTargetMember(row)}
            className="p-1 rounded text-slate-500 hover:text-rose-600 hover:bg-slate-100 transition-colors"
            title="Deactivate Staff Member"
          >
            <Trash2 size={14} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5 flex flex-col h-full select-none">
      
      {/* Standardized Header */}
      <PageHeader
        breadcrumbs={[
          { label: "Administration", href: "/admin/settings/team" },
          { label: "Team Members" },
        ]}
        title="Team & Staff Directory"
        description="Manage internal staff profiles, designations, department roles, and operational assignments."
        actions={
          <>
            <button
              onClick={() => refetch()}
              className="p-2 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-lg text-xs font-semibold transition-all focus:outline-none"
              title="Refresh list"
            >
              <RefreshCw size={14} className={isFetching ? "animate-spin text-blue-600" : ""} />
            </button>
            <button
              onClick={handleCreateNew}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm transition-colors focus:outline-none"
            >
              <Plus size={14} />
              <span>Add Staff Member</span>
            </button>
          </>
        }
      />

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm shrink-0 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative flex-1 w-full">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={16} />
          </span>
          <input
            type="search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search staff by display name, employee code, email, or phone..."
            className="w-full pl-9 pr-4 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 font-semibold"
          />
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <select
            value={filters.is_active === undefined ? "" : String(filters.is_active)}
            onChange={(e) => {
              const val = e.target.value;
              setFilters((prev) => ({
                ...prev,
                is_active: val === "" ? undefined : val === "true",
                page: 1,
              }));
            }}
            className="px-3 py-1.5 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none font-semibold"
          >
            <option value="">All Statuses</option>
            <option value="true">Active Staff</option>
            <option value="false">Inactive Staff</option>
          </select>
        </div>
      </div>

      {/* Enterprise Data Table */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={members}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total_records}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle="No staff members found"
          emptyStateDescription="Get started by registering employees and operational staff."
        />
      </div>

      {/* Create / Edit Modal */}
      <CreateTeamMemberModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        editingMember={editingMember}
      />

      {/* Deactivate Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTargetMember}
        onClose={() => setDeleteTargetMember(null)}
        onConfirm={confirmDeleteMember}
        title="Deactivate Staff Member?"
        message={`Are you sure you want to deactivate "${deleteTargetMember?.display_name}"?`}
        confirmLabel="Deactivate"
        variant="warning"
        isLoading={deleteMutation.isPending}
      />

    </div>
  );
}

export default TeamListPage;
