import React from "react";
import { useAuth } from "../../auth";
import { ListTodo, CheckSquare, Clock, AlertTriangle, ShieldCheck } from "lucide-react";

export function MyWorkPanel() {
  const { role } = useAuth();

  const getRolePanelData = () => {
    switch (role?.toLowerCase()) {
      case "admin":
      case "manager":
        return {
          title: "System Task Overview",
          items: [
            { id: 1, type: "alert", text: "Pending Vendor verification check: Hilton Coorg", meta: "Admin action required", icon: AlertTriangle, color: "text-amber-600 bg-amber-50" },
            { id: 2, type: "check", text: "Ledger check requested for Booking #BK-918", meta: "Operations completed", icon: CheckSquare, color: "text-indigo-600 bg-indigo-50" },
            { id: 3, type: "clock", text: "Finance Lock pending validation for 2 WON leads", meta: "Sales completed", icon: Clock, color: "text-blue-600 bg-blue-50" },
          ]
        };
      case "sales executive":
        return {
          title: "Sales Task Overview",
          items: [
            { id: 1, type: "alert", text: "Log followup call: Customer Sanjay Sharma", meta: "Overdue by 2 hours", icon: AlertTriangle, color: "text-red-600 bg-red-50" },
            { id: 2, type: "check", text: "Draft Proposal for Lead #LD-332", meta: "Awaiting itinerary pricing", icon: CheckSquare, color: "text-blue-600 bg-blue-50" },
            { id: 3, type: "clock", text: "Schedule itinerary review with client Jathin", meta: "Today at 5:00 PM", icon: Clock, color: "text-indigo-600 bg-indigo-50" },
          ]
        };
      case "finance executive":
        return {
          title: "Finance Verification Queue",
          items: [
            { id: 1, type: "alert", text: "Verify customer deposit: Booking #BK-411", meta: "Receipt upload check", icon: AlertTriangle, color: "text-amber-600 bg-amber-50" },
            { id: 2, type: "check", text: "Disburse vendor payment: Taj Vivanta Coorg", meta: "Allocation locked", icon: CheckSquare, color: "text-emerald-600 bg-emerald-50" },
            { id: 3, type: "clock", text: "Outstanding balance invoice: traveler Sanjay", meta: "Due in 2 days", icon: Clock, color: "text-blue-600 bg-blue-50" },
          ]
        };
      case "operations coordinator":
      case "operations executive":
        return {
          title: "Operations Workspace Queue",
          items: [
            { id: 1, type: "alert", text: "Verify vehicle allocation check: Cab Coorg", meta: "Driver info missing", icon: AlertTriangle, color: "text-red-600 bg-red-50" },
            { id: 2, type: "check", text: "Verify trip checklist: Alleppey Houseboat", meta: "Departs in 3 days", icon: CheckSquare, color: "text-indigo-600 bg-indigo-50" },
            { id: 3, type: "clock", text: "Bulk task assignment check: Sanjay Workload", meta: "5 tasks unassigned", icon: Clock, color: "text-blue-600 bg-blue-50" },
          ]
        };
      default:
        return {
          title: "My Workspace Tasks",
          items: [
            { id: 1, type: "check", text: "Review active catalog master lists", meta: "Geography / Hotels config", icon: ShieldCheck, color: "text-emerald-600 bg-emerald-50" }
          ]
        };
    }
  };

  const panel = getRolePanelData();

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col h-full hover:shadow-md transition-shadow duration-200">
      
      {/* Title */}
      <div className="flex justify-between items-center mb-5 border-b border-slate-50 pb-3">
        <div className="flex items-center space-x-2">
          <ListTodo size={18} className="text-blue-600" />
          <h3 className="text-base font-semibold text-slate-800">{panel.title}</h3>
        </div>
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
          Role: {role || "Staff"}
        </span>
      </div>

      {/* Items list */}
      <div className="flex-1 space-y-3.5">
        {panel.items.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className="flex items-start space-x-3.5 p-3 rounded-xl hover:bg-slate-50 transition-colors"
            >
              <div className={`p-2 rounded-lg shrink-0 ${item.color}`}>
                <Icon size={16} />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs font-semibold text-slate-800 leading-tight">{item.text}</p>
                <span className="text-[10px] text-slate-400 font-normal block">{item.meta}</span>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
export default MyWorkPanel;
