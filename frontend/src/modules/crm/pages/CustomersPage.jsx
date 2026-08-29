import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useCustomers } from "../hooks/useLeads";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import { User, Search, Mail, Phone, Calendar, Landmark, RefreshCw } from "lucide-react";
import PageHeader from "../../../components/ui/PageHeader";

export function CustomersPage() {
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
  });

  const [searchInput, setSearchInput] = useState("");

  // Debounced search trigger
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  // Queries
  const { data: customersResponse, isLoading, isFetching, refetch } = useCustomers(filters);

  const customers = customersResponse?.data || [];
  const meta = customersResponse?.meta || { page: 1, page_size: 10, total_records: 0 };

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const columns = [
    {
      header: "Customer Name",
      accessorKey: "name",
      render: (row, val) => (
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-bold text-slate-500 text-[10px]">
            {val ? val.split(" ").map(p => p[0]).join("").toUpperCase().slice(0, 2) : "CU"}
          </div>
          <div>
            <p className="font-bold text-slate-800">{val || "—"}</p>
            {row.designation && (
              <p className="text-[9px] text-slate-400 italic mt-0.5">{row.designation}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      header: "Contact Channels",
      render: (row) => (
        <div className="space-y-0.5 text-[11px] font-semibold text-slate-600">
          <p className="flex items-center">
            <Phone size={10} className="mr-1 text-slate-400 shrink-0" />
            {row.phone || "—"}
          </p>
          <p className="flex items-center">
            <Mail size={10} className="mr-1 text-slate-400 shrink-0" />
            {row.email || "—"}
          </p>
        </div>
      ),
    },
    {
      header: "Location",
      render: (row) => row.city || row.notes?.split("\n")?.[0]?.slice(0, 20) || "—",
    },
    {
      header: "Bookings",
      render: (row) => (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 border border-blue-100 text-blue-700">
          {row.total_bookings ?? 0} files
        </span>
      ),
    },
    {
      header: "Lifetime Value (LTV)",
      render: (row) => (
        <span className="font-bold text-slate-800">
          {row.lifetime_value ? `INR ${parseFloat(row.lifetime_value).toLocaleString("en-IN")}` : "INR 0.00"}
        </span>
      ),
    },
    {
      header: "Last Activity",
      render: (row) => {
        if (!row.last_contact_date) return "—";
        const date = new Date(row.last_contact_date);
        return date.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
      },
    },
    {
      header: "Status",
      render: (row) => {
        const hasBookings = (row.total_bookings ?? 0) > 0;
        return (
          <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold border ${
            hasBookings
              ? "bg-emerald-50 border-emerald-100 text-emerald-700"
              : "bg-slate-50 border-slate-200 text-slate-500"
          }`}>
            {hasBookings ? "Active Customer" : "Qualified Lead"}
          </span>
        );
      },
    },
  ];

  return (
    <div className="space-y-5 flex flex-col h-full select-none">
      
      {/* Page Header */}
      <PageHeader
        breadcrumbs={[
          { label: "CRM Workspace", href: "/admin/crm/leads" },
          { label: "Customers Directory" },
        ]}
        title="Customer Accounts Directory"
        description="Registry of customer accounts, contact details, lifetime value, and past trip bookings."
        actions={
          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 focus:outline-none transition-colors"
            title="Refresh directory"
          >
            <RefreshCw size={14} className={isFetching ? "animate-spin text-blue-600" : ""} />
          </button>
        }
      />

      {/* Filter search bar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm shrink-0">
        <div className="relative">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search size={16} />
          </span>
          <input
            type="search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search account name, phone number, email address..."
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-slate-700 font-semibold"
          />
        </div>
      </div>

      {/* Grid listing */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={customers}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total_records}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle="No customer contacts logged"
          emptyStateDescription="Customer account profiles are automatically generated when leads are converted to active bookings."
        />
      </div>

    </div>
  );
}

export default CustomersPage;
