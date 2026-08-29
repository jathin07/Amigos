import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { X, Loader2, DollarSign, Calendar, FileText, CheckCircle2 } from "lucide-react";
import financeApi from "../services/financeApi";

export function RecordPaymentModal({ isOpen, onClose, booking, onSubmit, isSubmitting }) {
  const [amount, setAmount] = useState("");
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split("T")[0]);
  const [paymentMethodId, setPaymentMethodId] = useState("");
  const [paymentTypeId, setPaymentTypeId] = useState("");
  const [transactionRef, setTransactionRef] = useState("");
  const [remarks, setRemarks] = useState("");

  // Get lookups
  const { data: methodsLookup, isLoading: isMethodsLoading } = useQuery({
    queryKey: ["lookups", "payment-methods"],
    queryFn: () => financeApi.getPaymentMethods(),
    enabled: isOpen,
  });

  const { data: typesLookup, isLoading: isTypesLoading } = useQuery({
    queryKey: ["lookups", "payment-types"],
    queryFn: () => financeApi.getPaymentTypes(),
    enabled: isOpen,
  });

  const paymentMethods = methodsLookup?.data || [];
  const paymentTypes = typesLookup?.data?.items || [];

  // Reset state on open
  useEffect(() => {
    if (isOpen && booking) {
      // Prefill amount with outstanding if available, else default empty
      const outstanding = booking.total_price - (booking.advance_paid || 0);
      setAmount(outstanding > 0 ? outstanding.toString() : "");
      setPaymentDate(new Date().toISOString().split("T")[0]);
      setPaymentMethodId("");
      setPaymentTypeId("");
      setTransactionRef("");
      setRemarks("");
    }
  }, [isOpen, booking]);

  if (!isOpen) return null;

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!booking) return;

    const payload = {
      booking_id: booking.id,
      amount: parseFloat(amount),
      payment_date: paymentDate,
      payment_method_id: paymentMethodId,
      payment_type_id: paymentTypeId,
      transaction_reference: transactionRef || null,
      remarks: remarks || null,
    };

    onSubmit(payload);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 select-none">
      <div className="w-full max-w-md bg-white border border-slate-100 rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2 text-slate-800">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
              <DollarSign size={18} />
            </div>
            <div>
              <h2 className="text-sm font-bold">Record Customer Payment</h2>
              <p className="text-[10px] text-slate-400 font-medium">Record client payment receipt</p>
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
          {booking && (
            <div className="bg-slate-50 border border-slate-150 rounded-xl p-3.5 space-y-1.5 text-xs font-semibold text-slate-600">
              <div className="flex justify-between">
                <span className="text-slate-400">File ID:</span>
                <span className="text-slate-850 font-mono font-bold">{booking.booking_number || booking.file_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Primary Client:</span>
                <span className="text-slate-800 font-bold">{booking.contact_person_snapshot?.name || booking.client_name}</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-slate-200">
                <span className="text-slate-400">Total Booking Value:</span>
                <span className="text-slate-800 font-bold">INR {parseFloat(booking.total_price || booking.confirmed_total_price || 0).toLocaleString("en-IN")}</span>
              </div>
            </div>
          )}

          {/* Amount field */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Receipt Amount (INR) *</label>
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
                className="w-full pl-7 pr-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 font-bold text-slate-800"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
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

            {/* Payment Type */}
            <div>
              <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Payment Type *</label>
              {isTypesLoading ? (
                <div className="h-9 border border-slate-200 rounded-lg flex items-center justify-center bg-slate-50">
                  <Loader2 className="animate-spin text-emerald-600" size={14} />
                </div>
              ) : (
                <select
                  required
                  value={paymentTypeId}
                  onChange={(e) => setPaymentTypeId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg bg-slate-50 focus:bg-white focus:outline-none text-xs font-semibold text-slate-700"
                >
                  <option value="">Select Type</option>
                  {paymentTypes.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* Payment Method */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Payment Channel / Method *</label>
            {isMethodsLoading ? (
              <div className="h-9 border border-slate-200 rounded-lg flex items-center justify-center bg-slate-50">
                <Loader2 className="animate-spin text-emerald-600" size={14} />
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
              placeholder="e.g. TXN998822001, Bank Ref Code, UPI ID"
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 font-mono text-slate-800"
            />
          </div>

          {/* Remarks */}
          <div>
            <label className="block text-[10px] font-bold text-slate-600 uppercase mb-1">Receipt Remarks</label>
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Record notes on cashier counter, cheques clearing, bank logs..."
              rows={2}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-700"
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
              className="flex items-center space-x-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-450 text-white text-xs font-bold rounded-lg shadow-md shadow-emerald-500/10 transition-colors focus:outline-none disabled:opacity-80"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="animate-spin" size={14} />
                  <span>Logging Receipt...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 size={14} />
                  <span>Record Payment</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
