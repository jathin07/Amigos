import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3,
  Calendar,
  Download,
  DollarSign,
  Users,
  Luggage,
  TrendingUp,
  Loader2,
  TrendingDown,
  Percent,
  Compass,
  ArrowRight,
  Filter
} from "lucide-react";
import reportsApi from "../services/reportsApi";

export function ReportsPage() {
  // Set default dates
  const todayStr = new Date().toISOString().split("T")[0];
  const janFirstStr = `${new Date().getFullYear()}-01-01`;

  const [dateFrom, setDateFrom] = useState(janFirstStr);
  const [dateTo, setDateTo] = useState(todayStr);
  const [activeTab, setActiveTab] = useState("finance");

  const queryParams = {
    date_from: dateFrom,
    date_to: dateTo,
    format: "json"
  };

  // Queries
  const { data: financeRes, isLoading: isFinanceLoading, error: financeErr } = useQuery({
    queryKey: ["reports", "finance", queryParams],
    queryFn: () => reportsApi.getFinanceReport(queryParams),
    enabled: activeTab === "finance",
  });

  const { data: crmRes, isLoading: isCrmLoading, error: crmErr } = useQuery({
    queryKey: ["reports", "crm", queryParams],
    queryFn: () => reportsApi.getCrmReport(queryParams),
    enabled: activeTab === "crm",
  });

  const { data: bookingRes, isLoading: isBookingLoading, error: bookingErr } = useQuery({
    queryKey: ["reports", "booking", queryParams],
    queryFn: () => reportsApi.getBookingReport(queryParams),
    enabled: activeTab === "booking",
  });

  const { data: opsRes, isLoading: isOpsLoading, error: opsErr } = useQuery({
    queryKey: ["reports", "operations", queryParams],
    queryFn: () => reportsApi.getOperationsReport(queryParams),
    enabled: activeTab === "operations",
  });

  const financeData = financeRes?.data || {};
  const crmData = crmRes?.data || {};
  const bookingData = bookingRes?.data || {};
  const opsData = opsRes?.data || {};

  // Export CSV handler
  const handleExportCsv = () => {
    // Generate browser download link for the CSV
    const token = localStorage.getItem("token"); // or appropriate auth token key
    const url = `${import.meta.env.VITE_API_URL || "/api/v1"}/reports/${activeTab}?date_from=${dateFrom}&date_to=${dateTo}&format=csv`;
    
    // Create hidden anchor and download
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${activeTab}_report_${dateFrom}_to_${dateTo}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-800 select-none">
      {/* Header and top selectors */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-850 flex items-center space-x-2">
            <BarChart3 className="text-blue-650" size={24} />
            <span>Analytical Reports Hub</span>
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            Analyze agency sales metrics, conversion performance, traveler operations and payouts ledger.
          </p>
        </div>

        {/* Date Filters Form */}
        <div className="flex flex-wrap items-center gap-3 bg-white border border-slate-100 p-2.5 rounded-xl shadow-sm text-xs font-semibold">
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">From:</span>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="px-2.5 py-1 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
            />
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-400">To:</span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="px-2.5 py-1 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none"
            />
          </div>
          <button
            onClick={handleExportCsv}
            className="flex items-center space-x-1 px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-bold transition-colors"
            title="Download CSV spreadsheet"
          >
            <Download size={12} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Tabs selectors */}
      <div className="flex border-b border-slate-200 gap-6 overflow-x-auto scrollbar-none select-none">
        <button
          onClick={() => setActiveTab("finance")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "finance" ? "border-blue-600 text-blue-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          Financial Profitability
        </button>
        <button
          onClick={() => setActiveTab("crm")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "crm" ? "border-blue-600 text-blue-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          CRM & Conversion
        </button>
        <button
          onClick={() => setActiveTab("booking")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "booking" ? "border-blue-600 text-blue-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          Booking Analysis
        </button>
        <button
          onClick={() => setActiveTab("operations")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "operations" ? "border-blue-600 text-blue-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          Operations & Trips
        </button>
      </div>

      {/* Report View Panel */}
      <div className="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm min-h-[400px] flex flex-col justify-between">
        
        {/* FINANCE REPORT VIEW */}
        {activeTab === "finance" && (
          isFinanceLoading ? (
            <div className="py-24 flex flex-col items-center justify-center text-slate-400 text-xs">
              <Loader2 className="animate-spin text-blue-600 mb-2" size={28} />
              <span>Compiling financial logs...</span>
            </div>
          ) : financeErr ? (
            <div className="py-24 text-center text-rose-500 text-xs font-bold">
              Failed to load financial report data. Please check date range filter.
            </div>
          ) : (
            <div className="space-y-6">
              {/* Financial stats overview */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Gross Revenue</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">
                    ₹ {parseFloat(financeData.total_revenue || 0).toLocaleString("en-IN")}
                  </span>
                </div>
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Total Cost of Goods Sold</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">
                    ₹ {parseFloat(financeData.total_cost || 0).toLocaleString("en-IN")}
                  </span>
                </div>
                <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4">
                  <span className="text-[10px] text-emerald-700 uppercase tracking-wider block font-bold">Net Profit Margin</span>
                  <span className="text-xl font-black text-emerald-800 mt-1 block">
                    ₹ {parseFloat(financeData.total_profit || 0).toLocaleString("en-IN")}
                  </span>
                </div>
              </div>

              {/* Profit Loss Breakdown Table */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-800">Booking Profitability Ledgers</h3>
                <div className="overflow-x-auto border border-slate-100 rounded-xl">
                  <table className="w-full border-collapse text-left text-xs font-semibold text-slate-700">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase text-[9px] font-bold">
                        <th className="px-4 py-2.5">File ID</th>
                        <th className="px-4 py-2.5">Client</th>
                        <th className="px-4 py-2.5 text-right">Confirmed Revenue</th>
                        <th className="px-4 py-2.5 text-right">Hotel Cost</th>
                        <th className="px-4 py-2.5 text-right">Transport Cost</th>
                        <th className="px-4 py-2.5 text-right">Other Opex</th>
                        <th className="px-4 py-2.5 text-right text-emerald-700">Net Profit</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {(financeData.booking_breakdown || []).map((booking) => (
                        <tr key={booking.booking_id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-2.5 font-mono font-bold text-slate-600">{booking.booking_number}</td>
                          <td className="px-4 py-2.5 text-slate-850 font-bold">{booking.customer_name}</td>
                          <td className="px-4 py-2.5 text-right">₹ {parseFloat(booking.revenue || 0).toLocaleString("en-IN")}</td>
                          <td className="px-4 py-2.5 text-right">₹ {parseFloat(booking.hotel_cost || 0).toLocaleString("en-IN")}</td>
                          <td className="px-4 py-2.5 text-right">₹ {parseFloat(booking.transport_cost || 0).toLocaleString("en-IN")}</td>
                          <td className="px-4 py-2.5 text-right">₹ {parseFloat(booking.other_cost || 0).toLocaleString("en-IN")}</td>
                          <td className="px-4 py-2.5 text-right text-emerald-750 font-bold">₹ {parseFloat(booking.profit || 0).toLocaleString("en-IN")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )
        )}

        {/* CRM REPORT VIEW */}
        {activeTab === "crm" && (
          isCrmLoading ? (
            <div className="py-24 flex flex-col items-center justify-center text-slate-400 text-xs">
              <Loader2 className="animate-spin text-blue-600 mb-2" size={28} />
              <span>Processing pipeline conversion metrics...</span>
            </div>
          ) : crmErr ? (
            <div className="py-24 text-center text-rose-500 text-xs font-bold">
              Failed to load CRM conversion report.
            </div>
          ) : (
            <div className="space-y-6">
              {/* CRM conversion summary card */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Total Inquiries</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">{crmData.total_leads || 0} Leads</span>
                </div>
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Closed Won</span>
                  <span className="text-xl font-bold text-slate-850 mt-1 block">{crmData.won_count || 0} Bookings</span>
                </div>
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Closed Lost</span>
                  <span className="text-xl font-bold text-slate-700 mt-1 block">{crmData.lost_count || 0} Leads</span>
                </div>
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                  <span className="text-[10px] text-blue-700 uppercase tracking-wider block font-bold">Conversion Rate</span>
                  <span className="text-xl font-black text-blue-800 mt-1 block">{(crmData.conversion_rate || 0.0).toFixed(1)} %</span>
                </div>
              </div>

              {/* Volume by Source breakdown lists */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-slate-800">Inquiry Volume by Channels</h3>
                  <div className="bg-slate-55 border border-slate-150 rounded-xl p-4 space-y-3 text-xs">
                    {(crmData.leads_by_source || []).map((source) => (
                      <div key={source.source} className="flex justify-between items-center font-semibold text-slate-650">
                        <span>{source.source_name || source.source}</span>
                        <span className="text-slate-800 font-bold">{source.count} leads</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-slate-800">Lost Leads Reason Breakdown</h3>
                  <div className="bg-slate-55 border border-slate-150 rounded-xl p-4 space-y-3 text-xs">
                    {(crmData.lost_by_reason || []).map((item) => (
                      <div key={item.reason} className="flex justify-between items-center font-semibold text-slate-650">
                        <span>{item.reason_name || item.reason}</span>
                        <span className="text-slate-700 font-bold">{item.count} leads</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )
        )}

        {/* BOOKING REPORT VIEW */}
        {activeTab === "booking" && (
          isBookingLoading ? (
            <div className="py-24 flex flex-col items-center justify-center text-slate-400 text-xs">
              <Loader2 className="animate-spin text-blue-600 mb-2" size={28} />
              <span>Analyzing booking database...</span>
            </div>
          ) : bookingErr ? (
            <div className="py-24 text-center text-rose-500 text-xs font-bold">
              Failed to load Booking report data.
            </div>
          ) : (
            <div className="space-y-6">
              {/* Booking stats overview */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Confirmed Bookings</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">{bookingData.confirmed_bookings || 0} Files</span>
                </div>
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Total Travelers Accommodated</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">{bookingData.total_travelers || 0} PAX</span>
                </div>
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                  <span className="text-[10px] text-blue-700 uppercase tracking-wider block font-bold">Average Order Value</span>
                  <span className="text-xl font-black text-blue-800 mt-1 block">
                    ₹ {parseFloat(bookingData.average_order_value || 0).toLocaleString("en-IN")}
                  </span>
                </div>
              </div>

              {/* Bookings table */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-800">Confirmed Booking Log</h3>
                <div className="overflow-x-auto border border-slate-100 rounded-xl">
                  <table className="w-full border-collapse text-left text-xs font-semibold text-slate-700">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase text-[9px] font-bold">
                        <th className="px-4 py-2.5">File ID</th>
                        <th className="px-4 py-2.5">Customer Name</th>
                        <th className="px-4 py-2.5">Travel Dates</th>
                        <th className="px-4 py-2.5 text-right">No. of Travelers</th>
                        <th className="px-4 py-2.5 text-right">Order Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {(bookingData.bookings_list || []).map((b) => (
                        <tr key={b.booking_id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-2.5 font-mono font-bold text-slate-650">{b.booking_number}</td>
                          <td className="px-4 py-2.5 text-slate-800 font-bold">{b.customer_name}</td>
                          <td className="px-4 py-2.5 text-slate-500 font-medium">{b.travel_dates || "N/A"}</td>
                          <td className="px-4 py-2.5 text-right">{b.pax_count} PAX</td>
                          <td className="px-4 py-2.5 text-right font-bold text-slate-800">₹ {parseFloat(b.total_price || 0).toLocaleString("en-IN")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )
        )}

        {/* OPERATIONS REPORT VIEW */}
        {activeTab === "operations" && (
          isOpsLoading ? (
            <div className="py-24 flex flex-col items-center justify-center text-slate-400 text-xs">
              <Loader2 className="animate-spin text-blue-600 mb-2" size={28} />
              <span>Analyzing operations performance metrics...</span>
            </div>
          ) : opsErr ? (
            <div className="py-24 text-center text-rose-500 text-xs font-bold">
              Failed to load Operations report.
            </div>
          ) : (
            <div className="space-y-6">
              {/* Operations overview */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Trips Dispatched</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">{opsData.total_trips || 0} Tours</span>
                </div>
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Onward Active</span>
                  <span className="text-xl font-bold text-slate-800 mt-1 block">{opsData.active_trips || 0} Tours</span>
                </div>
                <div className="bg-slate-50 border border-slate-150 rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-bold">Completed Trips</span>
                  <span className="text-xl font-bold text-slate-850 mt-1 block">{opsData.completed_trips || 0} Tours</span>
                </div>
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                  <span className="text-[10px] text-blue-700 uppercase tracking-wider block font-bold">Checklist Completion</span>
                  <span className="text-xl font-black text-blue-800 mt-1 block">{(opsData.checklist_rate || 0.0).toFixed(1)} %</span>
                </div>
              </div>

              {/* Task list summary */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-800">Operational Task Completion Breakdown</h3>
                <div className="overflow-x-auto border border-slate-100 rounded-xl">
                  <table className="w-full border-collapse text-left text-xs font-semibold text-slate-700">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase text-[9px] font-bold">
                        <th className="px-4 py-2.5">Task Category</th>
                        <th className="px-4 py-2.5 text-right">Total Tasks Assigned</th>
                        <th className="px-4 py-2.5 text-right text-emerald-650">Completed</th>
                        <th className="px-4 py-2.5 text-right text-amber-600">Pending</th>
                        <th className="px-4 py-2.5 text-right">Completion %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {(opsData.tasks_breakdown || []).map((t) => (
                        <tr key={t.category} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-2.5 text-slate-800 font-bold">{t.category}</td>
                          <td className="px-4 py-2.5 text-right">{t.total}</td>
                          <td className="px-4 py-2.5 text-right text-emerald-600">{t.completed}</td>
                          <td className="px-4 py-2.5 text-right text-amber-650">{t.pending}</td>
                          <td className="px-4 py-2.5 text-right font-black text-slate-800">{parseFloat(t.rate || 0).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
export default ReportsPage;
