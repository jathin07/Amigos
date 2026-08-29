import React from "react";
import { CreditCard, Calendar, DollarSign } from "lucide-react";

export function PaymentScheduleTab({ booking }) {
  const schedule = booking?.payment_schedule || [];
  const totalAmount = Number(booking?.total_amount || 0);

  const getStatusBadgeClass = (status) => {
    switch (status?.toUpperCase()) {
      case "PAID":
        return "bg-emerald-50 border-emerald-200 text-emerald-700";
      case "PARTIAL":
        return "bg-amber-50 border-amber-200 text-amber-700";
      case "UNPAID":
      default:
        return "bg-rose-50 border-rose-200 text-rose-700";
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Financial Snapshot Summary Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
            <DollarSign size={20} />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Total Confirmed Price</span>
            <span className="text-base font-extrabold text-slate-800 font-mono">
              INR {totalAmount.toLocaleString("en-IN")}
            </span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
            <CreditCard size={20} />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-bold">Installment Milestones</span>
            <span className="text-sm font-bold text-slate-800">
              {schedule.length} Scheduled Payments
            </span>
          </div>
        </div>
      </div>

      {/* Roster Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Client Payment Milestones</h3>
            <p className="text-[10px] text-slate-400 font-semibold mt-0.5">Payment receipts are matched to schedules in the Finance registry</p>
          </div>
        </div>

        {schedule.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-xs font-semibold">
            No payment milestones scheduled.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-5">Installment #</th>
                  <th className="py-3 px-5">Due Date</th>
                  <th className="py-3 px-5 text-right">Percentage</th>
                  <th className="py-3 px-5 text-right">Amount</th>
                  <th className="py-3 px-5 text-center">Status</th>
                  <th className="py-3 px-5">Remarks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs font-semibold text-slate-700">
                {schedule.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3.5 px-5 font-bold text-slate-800">
                      Installment {item.installment_no}
                    </td>
                    <td className="py-3.5 px-5">
                      <span className="flex items-center text-slate-600">
                        <Calendar size={12} className="mr-1.5 text-slate-400" />
                        {new Date(item.due_date).toLocaleDateString("en-IN")}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-right font-mono text-slate-600">
                      {item.percentage}%
                    </td>
                    <td className="py-3.5 px-5 text-right font-mono font-bold text-slate-900">
                      ₹{Number(item.amount).toLocaleString("en-IN")}
                    </td>
                    <td className="py-3.5 px-5 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded text-[9px] font-extrabold uppercase border ${getStatusBadgeClass(item.status)}`}>
                        {item.status || "UNPAID"}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-slate-400 font-medium">
                      {item.remarks || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}

export default PaymentScheduleTab;
