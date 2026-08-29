import React from "react";
import { useAuth } from "../../auth";
import { PlusCircle, Link as LinkIcon, Compass, Landmark, Settings, Users } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function QuickActions() {
  const { role } = useAuth();
  const navigate = useNavigate();

  const handleAction = (route, label) => {
    // Navigate if route matches current setup, else show toast/alert
    if (route === "/admin/login") {
      navigate(route);
    } else {
      alert(`Shortcut triggered: "${label}". This form is located in the next implementation roadmap phase.`);
    }
  };

  const getActions = () => {
    switch (role?.toLowerCase()) {
      case "admin":
        return [
          { label: "Onboard Vendor", route: "/vendors/new", icon: PlusCircle, color: "text-blue-600 bg-blue-50" },
          { label: "Create Package", route: "/packages/new", icon: Compass, color: "text-indigo-600 bg-indigo-50" },
          { label: "Configure Master Data", route: "/masters", icon: Settings, color: "text-purple-600 bg-purple-50" },
          { label: "Add Team Member", route: "/team/new", icon: Users, color: "text-emerald-600 bg-emerald-50" },
        ];
      case "sales executive":
        return [
          { label: "Create New Lead", route: "/crm/leads/new", icon: PlusCircle, color: "text-blue-600 bg-blue-50" },
          { label: "Create New Proposal", route: "/proposals/new", icon: Compass, color: "text-cyan-600 bg-cyan-50" },
        ];
      case "finance executive":
        return [
          { label: "Log Customer Payment", route: "/finance/payments/new", icon: PlusCircle, color: "text-emerald-600 bg-emerald-50" },
          { label: "Record Opex Expense", route: "/finance/expenses/new", icon: Landmark, color: "text-orange-600 bg-orange-50" },
        ];
      case "operations coordinator":
      case "operations executive":
        return [
          { label: "Assign Operations Task", route: "/operations/tasks/new", icon: PlusCircle, color: "text-blue-600 bg-blue-50" },
          { label: "Allocate New Vendor", route: "/operations/allocations/new", icon: Compass, color: "text-indigo-600 bg-indigo-50" },
        ];
      default:
        return [
          { label: "Sign Out Session", route: "/admin/login", icon: PlusCircle, color: "text-slate-600 bg-slate-50" }
        ];
    }
  };

  const actions = getActions();

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 flex flex-col h-full hover:shadow-md transition-shadow duration-200">
      
      {/* Header */}
      <div className="flex items-center space-x-2 mb-5 border-b border-slate-50 pb-3">
        <LinkIcon size={18} className="text-blue-600" />
        <h3 className="text-base font-semibold text-slate-800">Quick Actions</h3>
      </div>

      {/* Button list */}
      <div className="flex-grow grid grid-cols-1 gap-3.5">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          return (
            <button
              key={idx}
              onClick={() => handleAction(act.route, act.label)}
              className="flex items-center space-x-3.5 w-full text-left p-3 rounded-xl border border-slate-50 hover:bg-slate-50 hover:border-slate-100 transition-all duration-150 group"
            >
              <div className={`p-2.5 rounded-lg transition-transform group-hover:scale-105 ${act.color}`}>
                <Icon size={16} />
              </div>
              <span className="text-xs font-bold text-slate-700 group-hover:text-blue-600 transition-colors">
                {act.label}
              </span>
            </button>
          );
        })}
      </div>

    </div>
  );
}
export default QuickActions;
