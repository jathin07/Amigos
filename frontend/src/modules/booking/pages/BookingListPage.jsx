import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useBookings } from "../hooks/useBooking";
import bookingApi from "../services/bookingApi";
import EnterpriseDataTable from "../../../shared/components/EnterpriseDataTable";
import BookingStatusBadge from "../components/BookingStatusBadge";
import { Luggage, Search, RefreshCw, Eye, Calendar } from "lucide-react";

export function BookingListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    search: "",
    status: undefined,
  });

  const [searchInput, setSearchInput] = useState("");

  const { data: statusesResponse } = useQuery({
    queryKey: ["lookups", "booking-statuses"],
    queryFn: () => bookingApi.getStatuses(),
  });
  const statuses = statusesResponse?.data || [];

  // Debounced search
  useEffect(() => {
    const handler = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchInput, page: 1 }));
    }, 300);
    return () => clearTimeout(handler);
  }, [searchInput]);

  const { data: bookingsResponse, isLoading, isFetching, refetch } = useBookings(filters);

  // Envelope mapping: bookingsResponse is { success: true, data: [...], meta: { page, limit, total, pages } }
  const bookings = bookingsResponse?.data || [];
  const meta = bookingsResponse?.meta || { page: 1, limit: 10, total: 0 };

  const handlePageChange = (nextPage) => {
    setFilters((prev) => ({ ...prev, page: nextPage }));
  };

  const handlePageSizeChange = (nextSize) => {
    setFilters((prev) => ({ ...prev, page_size: nextSize, page: 1 }));
  };

  const columns = [
    {
      header: "Booking Ref #",
      accessorKey: "booking_number",
      render: (row) => (
        <button
          onClick={() => navigate(`/admin/bookings/${row.id}`)}
          className="font-mono font-bold text-blue-600 hover:underline text-xs"
        >
          {row.booking_number || `AM-BK-${row.id.slice(0, 8).toUpperCase()}`}
        </button>
      ),
    },
    {
      header: "Customer / Group",
      render: (row) => (
        <div className="space-y-0.5">
          <span className="font-bold text-slate-800 text-xs block">
            {row.contact_person_snapshot || "Client File"}
          </span>
          {row.group_name && (
            <span className="text-[10px] text-slate-400 font-semibold block">
              Group: {row.group_name}
            </span>
          )}
        </div>
      ),
    },
    {
      header: "Travel Schedule",
      render: (row) => {
        const start = row.trip_start_date;
        const end = row.trip_end_date;
        return (
          <span className="text-xs font-semibold text-slate-600 flex items-center">
            <Calendar size={12} className="mr-1.5 text-slate-400" />
            {start ? `${new Date(start).toLocaleDateString("en-IN")} - ${end ? new Date(end).toLocaleDateString("en-IN") : "TBD"}` : "Flexible Dates"}
          </span>
        );
      },
    },
    {
      header: "Travelers",
      render: (row) => (
        <span className="text-xs font-bold text-slate-700">
          {row.total_travelers ?? 0} pax
        </span>
      ),
    },
    {
      header: "Confirmed Total",
      render: (row) => (
        <span className="text-xs font-extrabold text-slate-800 font-mono">
          INR {Number(row.total_amount || 0).toLocaleString("en-IN")}
        </span>
      ),
    },
    {
      header: "Trip Coordinator",
      render: (row) => (
        <span className="text-xs font-semibold text-slate-600">
          {row.trip_coordinator?.display_name || "Unassigned"}
        </span>
      ),
    },
    {
      header: "Status",
      render: (row) => <BookingStatusBadge status={row.status} />,
    },
    {
      header: "Actions",
      className: "text-right",
      render: (row) => (
        <div className="flex items-center justify-end space-x-2">
          <button
            onClick={() => navigate(`/admin/bookings/${row.id}`)}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-blue-600 hover:bg-slate-50 transition-colors text-xs font-bold flex items-center space-x-1"
            title="Open Booking File Workspace"
          >
            <Eye size={14} />
            <span>Workspace</span>
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6 flex flex-col h-full select-none">
      
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4 shrink-0">
        <div>
          <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1">
            <span>Operations</span>
            <span>/</span>
            <span className="text-slate-500 font-bold">Bookings Workspace</span>
          </div>
          <h1 className="text-xl font-bold text-slate-800 tracking-tight mt-1 flex items-center">
            <Luggage className="mr-2 text-blue-600" size={20} />
            Active Bookings Registry
          </h1>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => refetch()}
            className="p-2 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-lg text-xs font-bold transition-all focus:outline-none"
            title="Refresh registry"
          >
            <RefreshCw size={14} className={isFetching ? "animate-spin text-blue-600" : ""} />
          </button>
        </div>
      </div>

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
            placeholder="Search booking ref #, customer name..."
            className="w-full pl-9 pr-4 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700 font-semibold"
          />
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <select
            value={filters.status || ""}
            onChange={(e) => {
              const val = e.target.value;
              setFilters((prev) => ({
                ...prev,
                status: val || undefined,
                page: 1,
              }));
            }}
            className="px-3 py-1.5 border border-slate-200 rounded-lg text-xs bg-white text-slate-600 focus:outline-none font-semibold"
          >
            <option value="">All Statuses</option>
            {statuses.map((st) => (
              <option key={st.id} value={st.id}>
                {st.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Enterprise Data Table */}
      <div className="flex-1 min-h-0 min-w-0">
        <EnterpriseDataTable
          columns={columns}
          data={bookings}
          isLoading={isLoading || isFetching}
          pageIndex={filters.page - 1}
          pageSize={filters.page_size}
          totalCount={meta.total}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          emptyStateTitle="No bookings registered yet"
          emptyStateDescription="Convert qualified CRM leads to active bookings to view operational files here."
        />
      </div>

    </div>
  );
}

export default BookingListPage;

