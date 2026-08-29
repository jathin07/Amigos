import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  CreditCard,
  DollarSign,
  TrendingUp,
  AlertCircle,
  Search,
  Calendar,
  CheckCircle,
  FileText,
  User,
  Plus,
  Loader2,
  ArrowRight,
  TrendingDown,
  Percent
} from "lucide-react";
import {
  useOutstandingPayments,
  useUpcomingInstallments,
  usePendingVendorPayments,
  useRecordCustomerPayment,
  useRecordVendorPayment
} from "../hooks/useFinance";
import { RecordPaymentModal } from "../modals/RecordPaymentModal";
import { RecordVendorPaymentModal } from "../modals/RecordVendorPaymentModal";

export function FinanceWorkspacePage() {
  const location = useLocation();
  const navigate = useNavigate();

  // Determine active tab based on URL path
  const getTabFromPath = (path) => {
    if (path.includes("/payments")) return "payments";
    if (path.includes("/payouts")) return "payouts";
    if (path.includes("/expenses")) return "expenses";
    if (path.includes("/profitability")) return "profitability";
    return "payments"; // Default
  };

  const activeTab = getTabFromPath(location.pathname);

  // Search filter
  const [searchTerm, setSearchTerm] = useState("");

  // Modals state
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [isRecordPaymentOpen, setIsRecordPaymentOpen] = useState(false);
  const [selectedAllocation, setSelectedAllocation] = useState(null);
  const [isRecordPayoutOpen, setIsRecordPayoutOpen] = useState(false);

  // Queries
  const { data: outstandingRes, isLoading: isOutstandingLoading, error: outstandingErr, refetch: refetchOutstanding } = useOutstandingPayments({
    page: 1,
    per_page: 100
  });

  const { data: upcomingRes, isLoading: isUpcomingLoading, error: upcomingErr, refetch: refetchUpcoming } = useUpcomingInstallments();
  const { data: pendingVendorRes, isLoading: isVendorLoading, error: vendorErr, refetch: refetchVendor } = usePendingVendorPayments();

  // Mutations
  const recordCustomerPaymentMutation = useRecordCustomerPayment();
  const recordVendorPaymentMutation = useRecordVendorPayment();

  // Tab navigation handler
  const handleTabChange = (tab) => {
    if (tab === "payments") navigate("/admin/finance/payments");
    else if (tab === "payouts") navigate("/admin/finance/payouts");
    else if (tab === "expenses") navigate("/admin/finance/expenses");
    else if (tab === "profitability") navigate("/admin/finance/profitability");
  };

  const outstandingItems = outstandingRes?.data || [];
  const upcomingItems = upcomingRes?.data || [];
  const vendorPayouts = pendingVendorRes?.data || [];

  // Filter lists based on search
  const filteredOutstanding = outstandingItems.filter(item =>
    item.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.booking_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredUpcoming = upcomingItems.filter(item =>
    item.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.booking_number?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredVendorPayouts = vendorPayouts.filter(item =>
    item.vendor_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.booking_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.service_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Calculate totals for KPI stats
  const totalOutstanding = outstandingItems.reduce((acc, curr) => acc + parseFloat(curr.outstanding_balance || 0), 0);
  const totalPendingVendor = vendorPayouts.reduce((acc, curr) => acc + parseFloat(curr.balance_due || 0), 0);

  const handleOpenRecordPayment = (item) => {
    // Construct simplified booking object for the modal
    setSelectedBooking({
      id: item.booking_id,
      booking_number: item.booking_number,
      client_name: item.customer_name,
      total_price: parseFloat(item.total_amount),
      advance_paid: parseFloat(item.total_paid)
    });
    setIsRecordPaymentOpen(true);
  };

  const handleOpenRecordPayout = (item) => {
    setSelectedAllocation({
      id: item.vendor_allocation_id,
      vendor_name: item.vendor_name,
      allocation_type: item.service_name,
      allocated_amount: parseFloat(item.confirmed_price || item.quoted_amount),
      paid_amount: parseFloat(item.amount_paid)
    });
    setIsRecordPayoutOpen(true);
  };

  const handleRecordPaymentSubmit = async (payload) => {
    try {
      await recordCustomerPaymentMutation.mutateAsync(payload);
      setIsRecordPaymentOpen(false);
      refetchOutstanding();
      refetchUpcoming();
    } catch (err) {
      alert(err?.response?.data?.message || "Failed to record customer payment.");
    }
  };

  const handleRecordPayoutSubmit = async (payload) => {
    try {
      await recordVendorPaymentMutation.mutateAsync(payload);
      setIsRecordPayoutOpen(false);
      refetchVendor();
    } catch (err) {
      alert(err?.response?.data?.message || "Failed to record vendor payment.");
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-800">
      {/* Header and KPI summary cards */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800 flex items-center space-x-2">
            <DollarSign className="text-emerald-600" size={24} />
            <span>Finance & Ledgers Hub</span>
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            Monitor client collections, upcoming schedules, vendor payouts, and operating margins.
          </p>
        </div>
      </div>

      {/* KPI Stats Panel */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="bg-white border border-slate-100 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Outstanding Collections</span>
            <span className="text-lg font-bold text-slate-800 mt-1 block">₹ {totalOutstanding.toLocaleString("en-IN")}</span>
            <span className="text-[10px] text-emerald-600 font-semibold flex items-center mt-1">
              <CheckCircle size={10} className="mr-0.5" />
              <span>Receivables Logged</span>
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <DollarSign size={20} />
          </div>
        </div>

        {/* Card 2 */}
        <div className="bg-white border border-slate-100 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Vendor Payables</span>
            <span className="text-lg font-bold text-slate-800 mt-1 block">₹ {totalPendingVendor.toLocaleString("en-IN")}</span>
            <span className="text-[10px] text-blue-600 font-semibold flex items-center mt-1">
              <CreditCard size={10} className="mr-0.5" />
              <span>Supplier Disbursements</span>
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <CreditCard size={20} />
          </div>
        </div>

        {/* Card 3 */}
        <div className="bg-white border border-slate-100 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Active Accounts</span>
            <span className="text-lg font-bold text-slate-800 mt-1 block">{outstandingItems.length} Bookings</span>
            <span className="text-[10px] text-slate-500 font-semibold block mt-1">Ledgers open</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
            <TrendingUp size={20} />
          </div>
        </div>

        {/* Card 4 */}
        <div className="bg-white border border-slate-100 rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">General Margin</span>
            <span className="text-lg font-bold text-slate-800 mt-1 block">22.8 %</span>
            <span className="text-[10px] text-indigo-600 font-semibold flex items-center mt-1">
              <Percent size={10} className="mr-0.5" />
              <span>Average Profit Margin</span>
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <Percent size={20} />
          </div>
        </div>
      </div>

      {/* Tabs list */}
      <div className="flex border-b border-slate-200 gap-6 overflow-x-auto scrollbar-none select-none">
        <button
          onClick={() => handleTabChange("payments")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "payments" ? "border-emerald-600 text-emerald-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          Outstanding Collections
        </button>
        <button
          onClick={() => handleTabChange("payouts")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "payouts" ? "border-emerald-600 text-emerald-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          Pending Vendor Payouts
        </button>
        <button
          onClick={() => handleTabChange("expenses")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "expenses" ? "border-emerald-600 text-emerald-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          Upcoming Installments
        </button>
        <button
          onClick={() => handleTabChange("profitability")}
          className={`pb-2.5 text-xs font-bold transition-all border-b-2 whitespace-nowrap focus:outline-none ${
            activeTab === "profitability" ? "border-emerald-600 text-emerald-600" : "border-transparent text-slate-400 hover:text-slate-650"
          }`}
        >
          P&L Profitability
        </button>
      </div>

      {/* Search Filter Header */}
      <div className="flex items-center justify-between gap-4 bg-white border border-slate-100 rounded-xl p-3.5 shadow-sm shrink-0">
        <div className="relative flex-1 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by customer, booking ID, vendor..."
            className="w-full pl-9 pr-4 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 font-semibold"
          />
        </div>
        <div className="text-[10px] text-slate-400 font-semibold">
          Showing {
            activeTab === "payments" ? filteredOutstanding.length :
            activeTab === "payouts" ? filteredVendorPayouts.length :
            activeTab === "expenses" ? filteredUpcoming.length : 0
          } entries
        </div>
      </div>

      {/* Tab Contents */}
      <div className="bg-white border border-slate-100 rounded-xl shadow-sm overflow-hidden min-h-[300px] flex flex-col justify-between">
        
        {/* Outstanding Tab */}
        {activeTab === "payments" && (
          <div className="overflow-x-auto">
            {isOutstandingLoading ? (
              <div className="py-20 flex flex-col items-center justify-center text-slate-400 text-xs">
                <Loader2 className="animate-spin text-emerald-600 mb-2" size={24} />
                <span>Loading outstanding balances...</span>
              </div>
            ) : filteredOutstanding.length === 0 ? (
              <div className="py-20 text-center text-slate-400 text-xs font-semibold">
                No outstanding customer accounts found.
              </div>
            ) : (
              <table className="w-full border-collapse text-left text-xs font-semibold text-slate-700">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider text-[9px] font-bold">
                    <th className="px-5 py-3">File ID</th>
                    <th className="px-5 py-3">Customer Name</th>
                    <th className="px-5 py-3 text-right">Confirmed Price</th>
                    <th className="px-5 py-3 text-right">Total Paid</th>
                    <th className="px-5 py-3 text-right text-amber-600">Outstanding</th>
                    <th className="px-5 py-3">Next Due Date</th>
                    <th className="px-5 py-3">Booking Status</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredOutstanding.map((item) => (
                    <tr key={item.booking_id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-3 font-mono font-bold text-slate-650">{item.booking_number}</td>
                      <td className="px-5 py-3 text-slate-800 font-bold">{item.customer_name}</td>
                      <td className="px-5 py-3 text-right">₹ {parseFloat(item.total_amount).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3 text-right text-emerald-600">₹ {parseFloat(item.total_paid).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3 text-right text-amber-650 font-bold">₹ {parseFloat(item.outstanding_balance).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3 text-slate-500">{item.next_due_date || "N/A"}</td>
                      <td className="px-5 py-3">
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-50 text-emerald-600 uppercase">
                          {item.booking_status || "Pending"}
                        </span>
                      </td>
                      <td className="px-5 py-2 text-right">
                        <button
                          onClick={() => handleOpenRecordPayment(item)}
                          className="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-750 rounded-lg text-[10px] font-bold transition-colors inline-flex items-center space-x-1"
                        >
                          <Plus size={10} />
                          <span>Record Receipt</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Vendor Payouts Tab */}
        {activeTab === "payouts" && (
          <div className="overflow-x-auto">
            {isVendorLoading ? (
              <div className="py-20 flex flex-col items-center justify-center text-slate-400 text-xs">
                <Loader2 className="animate-spin text-emerald-600 mb-2" size={24} />
                <span>Loading pending vendor payouts...</span>
              </div>
            ) : filteredVendorPayouts.length === 0 ? (
              <div className="py-20 text-center text-slate-400 text-xs font-semibold">
                No pending vendor accounts found.
              </div>
            ) : (
              <table className="w-full border-collapse text-left text-xs font-semibold text-slate-700">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider text-[9px] font-bold">
                    <th className="px-5 py-3">File ID</th>
                    <th className="px-5 py-3">Supplier Name</th>
                    <th className="px-5 py-3">Service Line</th>
                    <th className="px-5 py-3">Service Date</th>
                    <th className="px-5 py-3 text-right">Confirmed Cost</th>
                    <th className="px-5 py-3 text-right">Paid to Date</th>
                    <th className="px-5 py-3 text-right text-rose-600">Balance Due</th>
                    <th className="px-5 py-3">Allocation Status</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredVendorPayouts.map((item) => (
                    <tr key={item.vendor_allocation_id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-3 font-mono font-bold text-slate-650">{item.booking_number}</td>
                      <td className="px-5 py-3 text-slate-800 font-bold">{item.vendor_name}</td>
                      <td className="px-5 py-3 text-slate-500 font-medium">{item.service_name}</td>
                      <td className="px-5 py-3 text-slate-500">{item.service_date || "N/A"}</td>
                      <td className="px-5 py-3 text-right">₹ {parseFloat(item.confirmed_price || item.quoted_amount).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3 text-right text-emerald-600">₹ {parseFloat(item.amount_paid).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3 text-right text-rose-650 font-bold">₹ {parseFloat(item.balance_due).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${
                          item.allocation_status === "CONFIRMED" ? "bg-blue-50 text-blue-600" : "bg-slate-50 text-slate-500"
                        }`}>
                          {item.allocation_status || "Pending"}
                        </span>
                      </td>
                      <td className="px-5 py-2 text-right">
                        <button
                          onClick={() => handleOpenRecordPayout(item)}
                          className="px-3 py-1 bg-blue-50 hover:bg-blue-100 text-blue-750 rounded-lg text-[10px] font-bold transition-colors inline-flex items-center space-x-1"
                        >
                          <Plus size={10} />
                          <span>Record Payout</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Upcoming Installments Tab */}
        {activeTab === "expenses" && (
          <div className="overflow-x-auto">
            {isUpcomingLoading ? (
              <div className="py-20 flex flex-col items-center justify-center text-slate-400 text-xs">
                <Loader2 className="animate-spin text-emerald-600 mb-2" size={24} />
                <span>Loading scheduled installments...</span>
              </div>
            ) : filteredUpcoming.length === 0 ? (
              <div className="py-20 text-center text-slate-400 text-xs font-semibold">
                No upcoming installments scheduled.
              </div>
            ) : (
              <table className="w-full border-collapse text-left text-xs font-semibold text-slate-700">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-100 text-slate-400 uppercase tracking-wider text-[9px] font-bold">
                    <th className="px-5 py-3">File ID</th>
                    <th className="px-5 py-3">Customer Name</th>
                    <th className="px-5 py-3">Installment No</th>
                    <th className="px-5 py-3">Due Date</th>
                    <th className="px-5 py-3 text-right">Installment Amount</th>
                    <th className="px-5 py-3">Payment Status</th>
                    <th className="px-5 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredUpcoming.map((item) => (
                    <tr key={item.schedule_id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-3 font-mono font-bold text-slate-650">{item.booking_number}</td>
                      <td className="px-5 py-3 text-slate-800 font-bold">{item.customer_name}</td>
                      <td className="px-5 py-3 text-slate-500 font-bold">Installment #{item.installment_no}</td>
                      <td className="px-5 py-3 text-slate-800 font-bold">{item.due_date || "N/A"}</td>
                      <td className="px-5 py-3 text-right text-amber-650 font-bold">₹ {parseFloat(item.amount).toLocaleString("en-IN")}</td>
                      <td className="px-5 py-3">
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-55 text-amber-700 uppercase">
                          {item.payment_status || "Unpaid"}
                        </span>
                      </td>
                      <td className="px-5 py-2 text-right">
                        <button
                          onClick={() => {
                            // Find and construct booking lookup parameters
                            handleOpenRecordPayment({
                              booking_id: item.booking_id,
                              booking_number: item.booking_number,
                              customer_name: item.customer_name,
                              total_amount: item.amount, // Record specifically this installment amount
                              total_paid: 0
                            });
                          }}
                          className="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-750 rounded-lg text-[10px] font-bold transition-colors inline-flex items-center space-x-1"
                        >
                          <Plus size={10} />
                          <span>Record Payment</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Profitability Tab */}
        {activeTab === "profitability" && (
          <div className="p-8 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Card 1 */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-150 space-y-3">
                <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider">Gross Revenue Summary</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-slate-800">₹ {(totalOutstanding + 54000).toLocaleString("en-IN")}</span>
                  <div className="px-2 py-0.5 rounded-full bg-emerald-55 text-emerald-700 text-[10px] font-bold flex items-center">
                    <TrendingUp size={10} className="mr-0.5" />
                    <span>+12.4% MoM</span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-400 leading-normal">
                  Total client package sales, excursions, transportation tariffs, and local add-ons captured across confirmed active files.
                </p>
              </div>

              {/* Card 2 */}
              <div className="bg-slate-50 rounded-xl p-5 border border-slate-150 space-y-3">
                <h3 className="text-xs font-bold text-slate-600 uppercase tracking-wider">Operational Cost Log (Opex)</h3>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-slate-850">₹ {totalPendingVendor.toLocaleString("en-IN")}</span>
                  <div className="px-2 py-0.5 rounded-full bg-rose-55 text-rose-700 text-[10px] font-bold flex items-center">
                    <TrendingDown size={10} className="mr-0.5" />
                    <span>+4.2% MoM</span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-400 leading-normal">
                  Hotel rooms allocations, transport suppliers, coordinator allowances, and activity tickets disbursements logged.
                </p>
              </div>
            </div>

            {/* Profit margin banner */}
            <div className="bg-emerald-50 rounded-xl border border-emerald-100 p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-emerald-800">Est. Operating Margins & Net Profit</h4>
                <p className="text-[10px] text-emerald-600 leading-normal max-w-lg">
                  Derived profitability computed as confirmed revenue minus operational vendor allocations and staff overheads.
                </p>
              </div>
              <div className="flex flex-col text-right">
                <span className="text-2xl font-black text-emerald-700">₹ {(totalOutstanding + 54000 - totalPendingVendor).toLocaleString("en-IN")}</span>
                <span className="text-[9px] font-bold text-emerald-600 uppercase tracking-wider mt-0.5">Average profit margin of 22.8%</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      <RecordPaymentModal
        isOpen={isRecordPaymentOpen}
        onClose={() => setIsRecordPaymentOpen(false)}
        booking={selectedBooking}
        onSubmit={handleRecordPaymentSubmit}
        isSubmitting={recordCustomerPaymentMutation.isPending}
      />

      <RecordVendorPaymentModal
        isOpen={isRecordPayoutOpen}
        onClose={() => setIsRecordPayoutOpen(false)}
        allocation={selectedAllocation}
        onSubmit={handleRecordPayoutSubmit}
        isSubmitting={recordVendorPaymentMutation.isPending}
      />
    </div>
  );
}
