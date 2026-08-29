import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { X, Loader2, CreditCard, Calendar, FileText, CheckCircle2 } from "lucide-react";
import financeApi from "../services/financeApi";

export function RecordVendorPaymentModal({ isOpen, onClose, allocation, onSubmit, isSubmitting }) {
  const [amount, setAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split("T")[0]);
  const [paymentMethodId, setPaymentMethodId] = useState("");
  const [transactionRef, setTransactionRef] = useState("");
  const [notes, setNotes] = useState("");

  // Get lookups
  const { data: methodsLookup, isLoading: isMethodsLoading } = useQuery({
    queryKey: ["lookups", "payment-methods"],
    queryFn: () => financeApi.getPaymentMethods(),
    enabled: isOpen,
  });

  const paymentMethods = methodsLookup?.data || [];

  // Reset state on open
  useEffect(() => {
    if (isOpen && allocation) {
      // Prefill amount with outstanding if available, else default empty
      const outstanding = allocation.allocated_amount - (allocation.paid_amount || 0);
      setAmount(outstanding > 0 ? outstanding.toString() : "");
      setPaymentDate(new Date().toISOString().split("T")[0]);
      setPaymentMethodId("");
      setTransactionRef("");
      setNotes("");
    }
  }, [isOpen, allocation]);

  if (!isOpen) return null;

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!allocation) return;

    const payload = {
      vendor_allocation_id: allocation.id,
      amount: parseFloat(amount),
      payment_date: paymentDate,
      payment_method_id: paymentMethodId,
      transaction_reference: transactionRef || null,
      internal_notes: notes || null,
    };

    onSubmit(payload);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 select-none">
      <div className="w-full max-w-md bg-white border border-slate-100 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2 text-slate-800">
            <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
              <CreditCard size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold">Record Vendor Payout</h2>
              <p className="text-[10px] text-slate-400 font-medium">Record disbursement to supplier/vendor</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleFormSubmit} className="flex-1 overflow-y-auto p-5 space-y-4">
          {allocation && (
            <div className="bg-slate-50 border border-slate-150 rounded-xl p-3.5 space-y-1.5 text-xs font-semibold text-slate-600">
              <div className="flex justify-between">
                <span className="text-slate-400">Supplier:</span>
                <span className="text-slate-800 font-bold">{allocation.vendor_name || allocation.vendor?.vendor_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Allocation Area:</span>
                <span className="text-slate-800 font-bold">{allocation.allocation_type || allocation.category}</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-200">
                <span className="text-slate-400">Allocated Amount:</span>
                <span className="text-slate-800 font-bold">INR {parseFloat(allocation.allocated_amount || 0).toLocaleString("en-IN")}</span>
              </div>
            </div>
          )}

          {/* Amount field */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Disbursed Amount (INR) *</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-slate-400 font-bold text-xs">
                ₹
              </div>
              <input
                type="number"
                step="0.01"
                min="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                className="w-full pl-7 pr-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-bold text-slate-800"
              />
            </div>
          </div>

          {/* Payment Date */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Payment Date *</label>
            <input
              type="date"
              required
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none text-xs font-semibold text-slate-700"
            />
          </div>

          {/* Payment Method */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Payment Channel / Method *</label>
            {isMethodsLoading ? (
              <div className="h-9 border border-slate-200 rounded-lg flex items-center justify-center bg-slate-50">
                <Loader2 className="animate-spin text-blue-600" size={14} />
              </div>
            ) : (
              <select
                required
                value={paymentMethodId}
                onChange={(e) => setPaymentMethodId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none text-xs font-semibold text-slate-700"
              >
                <option value="">Select Payment Channel</option>
                {paymentMethods.map((method) => (
                  <option key={method.id} value={method.id}>
                    {method.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Reference code */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Transaction Ref / Reference Code</label>
            <input
              type="text"
              value={transactionRef}
              onChange={(e) => setTransactionRef(e.target.value)}
              placeholder="e.g. Bank Ref Code, IMPS, UTR Number"
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-slate-800"
            />
          </div>

          {/* Remarks */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Internal Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record notes on opex voucher, supplier receipt verification..."
              rows={2}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            />
          </div>

          {/* Action CTAs */}
          <div className="pt-2 flex items-center justify-end space-x-2 shrink-0 border-t border-slate-100 mt-5">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-500 text-xs font-bold rounded-lg transition-colors focus:outline-none disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-450 text-white text-xs font-bold rounded-lg shadow-md shadow-blue-500/10 transition-colors focus:outline-none disabled:opacity-80"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin" size={14} />
                  <span>Logging Payout...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 size={14} />
                  <span>Record Payout</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
