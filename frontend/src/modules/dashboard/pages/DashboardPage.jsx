import React, { useState } from "react";
import { useAuth } from "../../auth";
import SummaryCards from "../components/SummaryCards";
import LeadPipeline from "../components/LeadPipeline";
import BookingPipeline from "../components/BookingPipeline";
import FinanceSummary from "../components/FinanceSummary";
import RevenueTrend from "../components/RevenueTrend";
import UpcomingTrips from "../components/UpcomingTrips";
import OperationsOverview from "../components/OperationsOverview";
import MyWorkPanel from "../components/MyWorkPanel";
import QuickActions from "../components/QuickActions";
import ChangePasswordModal from "../../auth/components/ChangePasswordModal";
import { LogOut, Key, User, Compass } from "lucide-react";

export function DashboardPage() {
  const { user, logout } = useAuth();
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50/50 p-4 sm:p-6 lg:p-8 font-sans">
      <div className="mx-auto max-w-7xl space-y-8">
        
        {/* Header Block */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 sm:p-8 relative overflow-hidden transition-all duration-300">
          <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between relative z-10">
            <div className="space-y-1">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                Dashboard Overview
              </h1>
              <p className="text-sm font-medium text-slate-500 flex items-center">
                <User size={14} className="mr-1.5 text-blue-500 shrink-0" />
                Welcome back, <span className="font-semibold text-slate-700 ml-1">{user?.name || "Test User"}</span>
                <span className="text-slate-300 mx-2">•</span>
                <span className="text-slate-400 italic">{user?.designation || "Executive"}</span>
              </p>
            </div>
            
            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => setIsPasswordModalOpen(true)}
                className="flex items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs sm:text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
              >
                <Key size={14} className="mr-1.5 opacity-70" />
                Change Password
              </button>
              <button
                onClick={logout}
                className="flex items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 px-4 py-2 text-xs sm:text-sm font-semibold text-white hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md shadow-blue-100"
              >
                <LogOut size={14} className="mr-1.5 opacity-90" />
                Logout
              </button>
            </div>
          </div>
        </div>

        {/* My Work Queue & Quick Shortcuts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <MyWorkPanel />
          </div>
          <div>
            <QuickActions />
          </div>
        </div>

        {/* Primary Metrics Aggregations */}
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-slate-800 tracking-tight">Key Performance Indicators</h2>
          <SummaryCards />
        </div>

        {/* Funnel Pipelines Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <LeadPipeline />
          <BookingPipeline />
        </div>

        {/* Finance Charts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <RevenueTrend />
          <FinanceSummary />
        </div>

        {/* Logistics & Workflow Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <UpcomingTrips />
          <OperationsOverview />
        </div>

      </div>

      {/* Change Password Overlay */}
      <ChangePasswordModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
      />
    </div>
  );
}
export default DashboardPage;
