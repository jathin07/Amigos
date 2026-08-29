import React from "react";
import { Users, FileText, CheckCircle2, TrendingUp, Landmark, ShieldAlert, Award, Compass } from "lucide-react";
import { useSummaryCards } from "../hooks/useDashboard";

const formatCurrency = (val) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(val || 0);
};

export function SummaryCards() {
  const { data, isLoading, error, refetch } = useSummaryCards();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm animate-pulse space-y-3">
            <div className="h-4 bg-slate-100 rounded w-1/3"></div>
            <div className="h-6 bg-slate-200 rounded w-1/2"></div>
            <div className="h-3 bg-slate-100 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-700 text-sm flex justify-between items-center">
        <span>Failed to load KPI summary cards: {error.message}</span>
        <button onClick={refetch} className="px-3 py-1 bg-white border border-red-200 text-xs font-semibold rounded-lg hover:bg-red-50">Retry</button>
      </div>
    );
  }

  const kpi = data?.data || {};

  const cards = [
    {
      label: "Active Leads",
      value: kpi.active_leads || 0,
      icon: Users,
      color: "text-blue-600 bg-blue-50 border-blue-100",
      description: "Leads in sales pipeline",
    },
    {
      label: "Open Proposals",
      value: kpi.open_proposals || 0,
      icon: FileText,
      color: "text-cyan-600 bg-cyan-50 border-cyan-100",
      description: "Itineraries sent to clients",
    },
    {
      label: "Confirmed Bookings",
      value: kpi.confirmed_bookings || 0,
      icon: CheckCircle2,
      color: "text-emerald-600 bg-emerald-50 border-emerald-100",
      description: "Booked tours & stays",
    },
    {
      label: "Revenue (Month)",
      value: formatCurrency(kpi.revenue_this_month),
      icon: TrendingUp,
      color: "text-purple-600 bg-purple-50 border-purple-100",
      description: "Collected billing this month",
    },
  ];

  return (
    <div className="space-y-6">
      {/* 4 Primary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-start justify-between hover:shadow-md transition-shadow duration-200"
            >
              <div className="space-y-1">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{card.label}</span>
                <div className="text-2xl font-bold text-slate-900">{card.value}</div>
                <span className="text-xs text-slate-400 font-normal block">{card.description}</span>
              </div>
              <div className={`p-3 rounded-xl border ${card.color}`}>
                <Icon size={20} className="stroke-[2]" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Secondary cards / alerts row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white px-5 py-4 rounded-xl border border-slate-100 flex items-center space-x-3.5">
          <div className="p-2.5 rounded-lg bg-orange-50 border border-orange-100 text-orange-600">
            <Landmark size={18} />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Outstanding Collections</span>
            <span className="text-sm font-semibold text-slate-800">{formatCurrency(kpi.outstanding_payments)}</span>
          </div>
        </div>

        <div className="bg-white px-5 py-4 rounded-xl border border-slate-100 flex items-center space-x-3.5">
          <div className="p-2.5 rounded-lg bg-red-50 border border-red-100 text-red-600">
            <ShieldAlert size={18} />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Pending Vendor Payouts</span>
            <span className="text-sm font-semibold text-slate-800">{formatCurrency(kpi.pending_vendor_payments)}</span>
          </div>
        </div>

        <div className="bg-white px-5 py-4 rounded-xl border border-slate-100 flex items-center space-x-3.5">
          <div className="p-2.5 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600">
            <Compass size={18} />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Trips Running Today</span>
            <span className="text-sm font-semibold text-slate-800">{kpi.trips_today || 0} active tours</span>
          </div>
        </div>
      </div>
    </div>
  );
}
export default SummaryCards;
