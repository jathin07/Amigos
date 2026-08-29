import React, { useState, useEffect } from "react";
import { 
  useMasterItems, 
  useCreateMasterItem, 
  useUpdateMasterItem, 
  useDeleteMasterItem 
} from "../hooks/useMaster";
import MasterTabs, { MASTER_CATEGORIES } from "../components/MasterTabs";
import MasterStatusBadge from "../components/MasterStatusBadge";
import MasterEditDrawer from "../modals/MasterEditDrawer";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import { Plus, Search, Filter, RefreshCw, Edit2, Trash2, ShieldCheck, Database, X } from "lucide-react";
import PageHeader from "../../../components/ui/PageHeader";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export function MasterDataHubPage() {
  const [activeCategory, setActiveCategory] = useState("geography");
  const [activeEntitySlug, setActiveEntitySlug] = useState("countries");

  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
    is_active: undefined,
  });

  const [searchInput, setSearchInput] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [deleteTargetItem, setDeleteTargetItem] = useState(null);

  // Find active entity label
  const category = MASTER_CATEGORIES.find((c) => c.id === activeCategory) || MASTER_CATEGORIES[0];
  const entityConfig = category.entities.find((e) => e.id === activeEntitySlug) || category.entities[0];

  // Sync debounced search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  // Reset pagination on entity change
  useEffect(() => {
    setSearchInput("");
    setFilters({
      page: 1,
      page_size: 10,
      search: "",
      is_active: undefined,
    });
  }, [activeEntitySlug]);

  // Queries & Mutations
  const { data: itemsResponse, isLoading, isFetching, refetch } = useMasterItems(activeEntitySlug, filters);
  const createMutation = useCreateMasterItem(activeEntitySlug);
  const updateMutation = useUpdateMasterItem(activeEntitySlug, editingItem?.id);
  const deleteMutation = useDeleteMasterItem(activeEntitySlug);

  const rawData = itemsResponse?.data;
  const items = Array.isArray(rawData) ? rawData : rawData?.items || [];
  const meta = rawData?.pagination || { page: 1, page_size: 10, total_records: items.length };

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const handleCreateNew = () => {
    setEditingItem(null);
    setDrawerOpen(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setDrawerOpen(true);
  };

  const confirmDelete = () => {
    if (deleteTargetItem) {
      deleteMutation.mutate(deleteTargetItem.id, {
        onSettled: () => setDeleteTargetItem(null),
      });
    }
  };

  const handleFormSubmit = (payload, callback) => {
    if (editingItem) {
      updateMutation.mutate(payload, {
        onSuccess: () => {
          callback();
          setDrawerOpen(false);
        },
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: () => {
          callback();
          setDrawerOpen(false);
        },
      });
    }
  };

  const columns = [
    {
      header: "Name",
      accessorKey: "name",
      render: (row) => (
        <div className="space-y-0.5">
          <span className="font-bold text-slate-800 text-xs block">{row.name}</span>
          {/* Countries */}
          {row.phone_code && (
            <span className="text-[10px] text-blue-600 font-semibold block">Phone Code: {row.phone_code}</span>
          )}
          {/* States */}
          {row.country_name && (
            <span className="text-[10px] text-slate-500 font-semibold block">Country: {row.country_name}</span>
          )}
          {/* Districts */}
          {row.state_name && (
            <span className="text-[10px] text-slate-500 font-semibold block">State: {row.state_name}</span>
          )}
          {/* Cities */}
          {row.district_name && (
            <span className="text-[10px] text-slate-500 font-semibold block">District: {row.district_name}</span>
          )}
          {/* Destinations */}
          {row.slug && (
            <span className="text-[10px] text-indigo-650 font-mono font-bold block">Slug: {row.slug}</span>
          )}
          {/* Currencies */}
          {row.symbol && (
            <span className="text-[10px] text-blue-600 font-semibold block">Symbol: {row.symbol} {row.is_default ? " (Default)" : ""}</span>
          )}
          {/* Cancellation Policies */}
          {row.refund_percentage !== undefined && row.refund_percentage !== null && (
            <span className="text-[10px] text-amber-600 font-semibold block">
              Refund: {row.refund_percentage}% | Days Prior: {row.days_before_travel}
            </span>
          )}
          {/* Tax Configurations */}
          {row.tax_rate !== undefined && row.tax_rate !== null && (
            <span className="text-[10px] text-indigo-600 font-semibold block">
              Tax Rate: {row.tax_rate}% ({row.tax_type})
            </span>
          )}
        </div>
      ),
    },
    {
      header: "Code",
      accessorKey: "code",
      render: (row) => (
        <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 font-mono text-[10px] font-bold">
          {row.code}
        </span>
      ),
    },
    {
      header: "Description",
      accessorKey: "description",
      render: (row) => (
        <span className="text-slate-500 text-xs line-clamp-1">
          {row.description || "—"}
        </span>
      ),
    },
    {
      header: "Status",
      render: (row) => <MasterStatusBadge isActive={row.is_active} />,
    },
    {
      header: "Created Date",
      render: (row) => {
        const d = row.created_at || row.audit_info?.created_at;
        return d ? new Date(d).toLocaleDateString("en-IN") : "—";
      },
    },
    {
      header: "Actions",
      className: "text-right",
      render: (row) => (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => handleEdit(row)}
            className="p-1 rounded text-slate-500 hover:text-blue-600 hover:bg-slate-100 transition-colors"
            title="Edit Master Record"
          >
            <Edit2 size={14} />
          </button>
          <button
            onClick={() => setDeleteTargetItem(row)}
            className="p-1 rounded text-slate-500 hover:text-rose-600 hover:bg-slate-100 transition-colors"
            title="Deactivate Master Record"
          >
            <Trash2 size={14} />
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
          { label: "Administration", href: "/admin/settings/masters" },
          { label: "Master Data Hub" },
        ]}
        title="Master Reference Hub"
        description="Centralized taxonomy for destinations, trip types, lead channels, activity categories, and operational parameters."
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
              <span>Add {entityConfig.label}</span>
            </button>
          </>
        }
      />

      {/* 2. Category Tabs */}
      <MasterTabs
        activeCategoryId={activeCategory}
        onCategoryChange={setActiveCategory}
        activeEntitySlug={activeEntitySlug}
        onEntityChange={setActiveEntitySlug}
      />

      {/* 3. Toolbar & Filters */}
      <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-sm shrink-0 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative flex-1 w-full">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={16} />
          </span>
          <input
            type="search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder={`Search ${entityConfig.name} by name or code...`}
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

      {/* 4. Enterprise Table */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={items}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total_records}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle={`No ${entityConfig.name} registered`}
          emptyStateDescription={`Get started by adding reference records for ${entityConfig.name}.`}
        />
      </div>

      {/* 5. Master Edit Drawer */}
      <MasterEditDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        editingItem={editingItem}
        entityLabel={entityConfig.label}
        entitySlug={activeEntitySlug}
      />

      {/* 6. Deactivate Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTargetItem}
        onClose={() => setDeleteTargetItem(null)}
        onConfirm={confirmDelete}
        title="Deactivate Master Record?"
        message={`Are you sure you want to deactivate "${deleteTargetItem?.name}"?`}
        confirmLabel="Deactivate"
        variant="warning"
        isLoading={deleteMutation.isPending}
      />

    </div>
  );
}

export default MasterDataHubPage;
