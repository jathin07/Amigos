import React from "react";
import { useFinanceSummary } from "../hooks/useDashboard";
import WidgetCard from "../widgets/WidgetCard";
import { Landmark, ArrowUpRight, ArrowDownRight, Wallet, Percent } from "lucide-react";

const formatCurrency = (val) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(val || 0);
};

export function FinanceSummary() {
  const { data, isLoading, error, refetch, isEnabled } = useFinanceSummary();

  // If query is disabled (no finance.read permission), return null so widget is omitted completely.
  if (!isLoading && !data && !error) {
    return null;
  }

  const fin = data?.data || {};

  return (
    <WidgetCard
      title="Financial Performance Ledger"
      description="Gross margin and operational cashflows overview"
      onRefresh={refetch}
      isRefreshing={isLoading}
      error={error}
    >
      <div className="flex-1 flex flex-col justify-between py-1 space-y-4">
        
        {/* Net Profit & Margin */}
        <div className="flex items-center justify-between p-4 bg-emerald-50/50 border border-emerald-100 rounded-xl">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Net Margin Profit</span>
            <span className="text-xl font-bold text-emerald-800">{formatCurrency(fin.net_profit)}</span>
          </div>
          <div className="flex items-center space-x-1 text-xs font-semibold text-emerald-700 bg-white px-2 py-1 rounded-lg border border-emerald-100 shadow-sm">
            <Percent size={14} />
            <span>{fin.gross_margin_percentage?.toFixed(1) || "0.0"}%</span>
          </div>
        </div>

        {/* Breakdown Items */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-0.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Billed Collected</span>
            <span className="text-sm font-semibold text-slate-800 flex items-center">
              <ArrowUpRight size={14} className="text-emerald-500 mr-1 shrink-0" />
              {formatCurrency(fin.collected)}
            </span>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Outstanding Collections</span>
            <span className="text-sm font-semibold text-slate-800 flex items-center">
              <Landmark size={14} className="text-amber-500 mr-1 shrink-0" />
              {formatCurrency(fin.outstanding)}
            </span>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Vendor Disbursements Due</span>
            <span className="text-sm font-semibold text-slate-800 flex items-center">
              <Wallet size={14} className="text-blue-500 mr-1 shrink-0" />
              {formatCurrency(fin.vendor_due)}
            </span>
          </div>

          <div className="space-y-0.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Operational Expenses</span>
            <span className="text-sm font-semibold text-slate-800 flex items-center">
              <ArrowDownRight size={14} className="text-red-500 mr-1 shrink-0" />
              {formatCurrency(fin.expenses)}
            </span>
          </div>
        </div>

        {fin.refunds > 0 && (
          <div className="text-xs text-red-600 bg-red-50/50 border border-red-100 rounded-lg p-2 flex justify-between items-center">
            <span>Customer Refunds Issued</span>
            <span className="font-semibold">{formatCurrency(fin.refunds)}</span>
          </div>
        )}

      </div>
    </WidgetCard>
  );
}
export default FinanceSummary;
