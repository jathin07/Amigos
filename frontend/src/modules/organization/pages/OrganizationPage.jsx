import React, { useState, useEffect } from "react";
import {
  Building,
  Plus,
  Search,
  RefreshCw,
  Edit2,
  Trash2,
  Phone,
  Mail,
  Globe,
  MapPin,
  ShieldAlert,
  Loader2
} from "lucide-react";
import {
  useOrganizations,
  useCreateOrganization,
  useUpdateOrganization,
  useDeleteOrganization,
  useOrganizationTypes
} from "../hooks/useOrganization";
import OrganizationFormModal from "../components/OrganizationFormModal";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import PageHeader from "../../../components/ui/PageHeader";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export function OrganizationPage() {
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
    is_active: undefined,
  });

  const [searchInput, setSearchInput] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [deleteTargetItem, setDeleteTargetItem] = useState(null);

  // Queries & Mutations
  const { data: orgsRes, isLoading, isFetching, refetch } = useOrganizations(filters);
  const { data: typesRes } = useOrganizationTypes();
  const createMutation = useCreateOrganization();
  const deleteMutation = useDeleteOrganization();

  const orgTypes = typesRes?.data || [];
  const orgs = orgsRes?.data?.items || [];
  const meta = orgsRes?.data?.pagination || { page: 1, page_size: 10, total_records: 0 };

  // Sync debounced search
  useEffect(() => {
    const handler = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const handleCreateNew = () => {
    setEditingItem(null);
    setModalOpen(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setModalOpen(true);
  };

  const confirmDelete = () => {
    if (deleteTargetItem) {
      deleteMutation.mutate(deleteTargetItem.id, {
        onSettled: () => setDeleteTargetItem(null),
      });
    }
  };

  // Custom mutation instantiation because updateMutation requires the specific org ID in hook args
  const updateMutationHook = useUpdateOrganization(editingItem?.id);

  const handleFormSubmit = (payload) => {
    if (editingItem) {
      updateMutationHook.mutate(payload, {
        onSuccess: () => {
          setModalOpen(false);
          setEditingItem(null);
          refetch();
        },
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: () => {
          setModalOpen(false);
          refetch();
        },
      });
    }
  };

  const columns = [
    {
      header: "Organization Name",
      accessorKey: "organization_name",
      render: (row) => {
        const typeObj = orgTypes.find((t) => t.id === row.organization_type_id);
        return (
          <div className="space-y-1">
            <span className="font-bold text-slate-800 text-xs block">{row.organization_name}</span>
            <div className="flex items-center space-x-1.5 flex-wrap gap-y-1">
              {typeObj && (
                <span className="px-2 py-0.5 text-[9px] font-bold text-blue-700 bg-blue-50 border border-blue-100 rounded-md">
                  {typeObj.name}
                </span>
              )}
              {(row.city || row.state) && (
                <span className="text-[10px] text-slate-400 font-semibold flex items-center">
                  <MapPin size={9} className="mr-0.5 text-slate-400" />
                  {row.city}{row.state ? `, ${row.state}` : ""}
                </span>
              )}
            </div>
          </div>
        );
      },
    },
    {
      header: "Divisions & Batches",
      render: (row) => {
        const divs = row.divisions || [];
        if (divs.length === 0) {
          return <span className="text-[10px] text-slate-400 italic">No divisions setup</span>;
        }
        return (
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-600 bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded">
              {divs.length} division{divs.length > 1 ? "s" : ""}
            </span>
            <div className="flex flex-wrap gap-1 max-w-xs">
              {divs.slice(0, 2).map((d, i) => (
                <span key={i} className="text-[9px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-100 px-1.5 py-0.5 rounded">
                  {d.course ? `${d.course} ` : ""}{d.department ? `(${d.department})` : ""}{d.batch ? ` '${d.batch.slice(-2)}` : ""}
                </span>
              ))}
              {divs.length > 2 && (
                <span className="text-[9px] font-bold text-slate-400">+{divs.length - 2} more</span>
              )}
            </div>
          </div>
        );
      },
    },
    {
      header: "Contact Info",
      render: (row) => (
        <div className="space-y-0.5 text-[10px] text-slate-500 font-semibold">
          {row.phone && (
            <div className="flex items-center">
              <Phone size={10} className="mr-1 text-slate-400" />
              <span>{row.phone}</span>
            </div>
          )}
          {row.email && (
            <div className="flex items-center">
              <Mail size={10} className="mr-1 text-slate-400" />
              <span>{row.email}</span>
            </div>
          )}
          {row.website && (
            <div className="flex items-center text-blue-600 font-mono text-[9px]">
              <Globe size={10} className="mr-1 text-slate-400" />
              <span>{row.website}</span>
            </div>
          )}
        </div>
      ),
    },
    {
      header: "Contact Managers",
      render: (row) => {
        const contacts = row.contact_persons || [];
        const primary = contacts.find((c) => c.is_primary) || contacts[0];
        if (!primary) {
          return <span className="text-[10px] text-slate-400 italic">Unassigned</span>;
        }
        return (
          <div className="space-y-0.5">
            <span className="text-slate-800 text-xs font-bold block leading-tight">
              {primary.name} {contacts.length > 1 && <span className="text-[9px] text-blue-600 font-semibold">({contacts.length} total)</span>}
            </span>
            {primary.designation && (
              <span className="text-[10px] text-slate-400 font-semibold block leading-tight">
                {primary.designation}
              </span>
            )}
            {primary.phone && (
              <span className="text-[9px] text-slate-500 font-mono block">
                {primary.phone}
              </span>
            )}
          </div>
        );
      },
    },
    {
      header: "Actions",
      className: "text-right",
      render: (row) => (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => handleEdit(row)}
            className="p-1.5 rounded text-slate-500 hover:text-blue-600 hover:bg-slate-100 transition-colors"
            title="Edit Organization Details"
          >
            <Edit2 size={13} />
          </button>
          <button
            onClick={() => setDeleteTargetItem(row)}
            className="p-1.5 rounded text-slate-500 hover:text-rose-600 hover:bg-slate-100 transition-colors"
            title="Delete Organization"
          >
            <Trash2 size={13} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5 flex flex-col h-full select-none">
      
      {/* 1. Standardized Header */}
      <PageHeader
        breadcrumbs={[
          { label: "Administration", href: "/admin/settings/organization" },
          { label: "Organization Settings" },
        ]}
        title="Customer Organizations Directory"
        description="Registry of colleges, universities, corporate offices, and institutions for group tours and IV bookings."
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
              <span>Add Organization</span>
            </button>
          </>
        }
      />

      {/* 2. Filter / Search Toolbar */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm shrink-0 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative flex-1 w-full">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={16} />
          </span>
          <input
            type="search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search organizations by name, email or website..."
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
            <option value="true">Active Only</option>
            <option value="false">Inactive Only</option>
          </select>
        </div>
      </div>

      {/* 3. Enterprise DataTable */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={orgs}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total_records}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle="No client organizations registered"
          emptyStateDescription="Register customer companies, colleges or offices to map group leads and industrial visits."
        />
      </div>

      {/* 4. Edit Form Modal */}
      <OrganizationFormModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingItem(null);
        }}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending || updateMutationHook.isPending}
        editingItem={editingItem}
      />

      {/* 5. Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTargetItem}
        onClose={() => setDeleteTargetItem(null)}
        onConfirm={confirmDelete}
        title="Delete Customer Organization?"
        message={`Are you sure you want to delete "${deleteTargetItem?.organization_name}"?`}
        confirmLabel="Delete Organization"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />

    </div>
  );
}
export default OrganizationPage;
