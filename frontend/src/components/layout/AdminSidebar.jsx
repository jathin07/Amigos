import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../modules/auth";
import {
  LayoutDashboard,
  Users,
  FileText,
  Luggage,
  Zap,
  Store,
  CreditCard,
  Package,
  BarChart3,
  Settings,
  User,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Menu,
  Building,
  UserCog,
  Database,
  Compass,
  UserCheck,
  CheckSquare,
  ClipboardList,
  ArrowDownCircle,
  ArrowUpCircle,
  Receipt,
  TrendingUp,
  X
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/admin/dashboard", icon: LayoutDashboard },
  {
    name: "CRM",
    icon: Users,
    children: [
      { name: "Leads", href: "/admin/crm/leads", permission: "crm.read" },
      { name: "Customers", href: "/admin/crm/customers", permission: "crm.contacts.read" },
    ],
  },
  { name: "Proposals", href: "/admin/proposals", icon: FileText, permission: "proposal.read" },
  { name: "Bookings", href: "/admin/bookings", icon: Luggage, permission: "booking.read" },
  {
    name: "Operations",
    icon: Zap,
    children: [
      { name: "Trip Plans", href: "/admin/operations/trips", permission: "operations.read" },
      { name: "Vendor Allocations", href: "/admin/operations/allocations", permission: "operations.read" },
      { name: "Tasks", href: "/admin/operations/tasks", permission: "operations.read" },
      { name: "Checklists", href: "/admin/operations/checklists", permission: "operations.read" },
    ],
  },
  { name: "Vendors", href: "/admin/vendors", icon: Store, permission: "vendor.read" },
  {
    name: "Finance",
    icon: CreditCard,
    children: [
      { name: "Payments", href: "/admin/finance/payments", permission: "finance.read" },
      { name: "Vendor Payouts", href: "/admin/finance/payouts", permission: "finance.read" },
      { name: "Expenses", href: "/admin/finance/expenses", permission: "finance.read" },
      { name: "Profitability", href: "/admin/finance/profitability", permission: "finance.read" },
    ],
  },
  { name: "Packages", href: "/admin/packages", icon: Package, permission: "package.read" },
  { name: "Reports", href: "/admin/reports", icon: BarChart3, permission: "reports.read" },
  {
    name: "Administration",
    icon: Settings,
    children: [
      { name: "Organization", href: "/admin/settings/organization", permission: "admin.full" },
      { name: "Team Members", href: "/admin/settings/team", permission: "admin.full" },
      { name: "Master Data Hub", href: "/admin/settings/masters", permission: "admin.full" },
    ],
  },
];

export function AdminSidebar({ isCollapsed, onToggle }) {
  const { user, role, hasPermission } = useAuth();
  const location = useLocation();
  const [expandedGroups, setExpandedGroups] = useState({});

  // Check if a link should be visible based on user permissions
  const filterByPermission = (item) => {
    if (!item.permission) return true;
    return hasPermission(item.permission);
  };

  // Toggle dropdown group
  const toggleGroup = (name) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [name]: !prev[name],
    }));
  };

  // Auto-expand group if child route is active on load
  useEffect(() => {
    navigation.forEach((item) => {
      if (item.children) {
        const hasActiveChild = item.children.some((child) => location.pathname === child.href);
        if (hasActiveChild) {
          setExpandedGroups((prev) => ({ ...prev, [item.name]: true }));
        }
      }
    });
  }, [location.pathname]);

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 flex flex-col bg-slate-900 border-r border-slate-800 text-slate-300 transition-all duration-300 ${
        isCollapsed ? "w-16" : "w-64"
      } h-screen select-none`}
    >
      {/* Brand Logo & Header */}
      <div className="flex items-center justify-between px-4 py-4 h-16 border-b border-slate-800 shrink-0">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold shrink-0 shadow-md shadow-blue-500/20">
            A
          </div>
          {!isCollapsed && (
            <span className="font-bold text-lg tracking-wider bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              AMIGOS<span className="text-blue-500 text-sm ml-1 font-semibold">ERP</span>
            </span>
          )}
        </div>
        {!isCollapsed && (
          <button
            onClick={onToggle}
            className="p-1 rounded-md text-slate-500 hover:text-slate-300 hover:bg-slate-800 focus:outline-none transition-colors"
          >
            <ChevronLeft size={16} />
          </button>
        )}
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        {navigation.map((item) => {
          // If group, check if any child is visible
          const visibleChildren = item.children
            ? item.children.filter(filterByPermission)
            : null;

          if (item.children && visibleChildren.length === 0) return null;
          if (!item.children && !filterByPermission(item)) return null;

          const isGroup = !!item.children;
          const Icon = item.icon;
          const isExpanded = expandedGroups[item.name];

          if (isGroup) {
            const hasActiveChild = visibleChildren.some((child) => location.pathname === child.href);

            return (
              <div key={item.name} className="space-y-1">
                <button
                  onClick={() => toggleGroup(item.name)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-lg transition-all duration-150 group ${
                    hasActiveChild
                      ? "bg-slate-800/60 text-white"
                      : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon
                      size={18}
                      className={`${
                        hasActiveChild ? "text-blue-500" : "text-slate-500 group-hover:text-slate-300"
                      } shrink-0`}
                    />
                    {!isCollapsed && <span>{item.name}</span>}
                  </div>
                  {!isCollapsed && (
                    <ChevronDown
                      size={14}
                      className={`text-slate-500 transition-transform duration-200 ${
                        isExpanded ? "rotate-180" : ""
                      }`}
                    />
                  )}
                </button>

                {/* Sub-navigation links */}
                {isExpanded && !isCollapsed && (
                  <div className="pl-9 pr-2 space-y-1">
                    {visibleChildren.map((child) => {
                      const isChildActive = location.pathname === child.href;
                      return (
                        <Link
                          key={child.name}
                          to={child.href}
                          className={`block px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                            isChildActive
                              ? "text-blue-400 bg-blue-500/5"
                              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/30"
                          }`}
                        >
                          {child.name}
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          }

          // Single Link
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-150 group ${
                isActive
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/10"
                  : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
              }`}
            >
              <Icon
                size={18}
                className={`${isActive ? "text-white" : "text-slate-500 group-hover:text-slate-300"} shrink-0 mr-3`}
              />
              {!isCollapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User Footer Profile Summary */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/50 shrink-0">
        <div className="flex items-center space-x-3 overflow-hidden">
          <div className="w-9 h-9 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold shrink-0 select-none text-xs">
            {(user?.name || role || "Admin").slice(0, 2).toUpperCase()}
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || "Administrator"}</p>
              <div className="flex items-center space-x-1.5 mt-0.5">
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-blue-400 font-bold border border-slate-700 uppercase tracking-wider">
                  {role || "Admin"}
                </span>
                <span className="text-[10px] text-slate-500 truncate">{user?.email || ""}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

export default AdminSidebar;
