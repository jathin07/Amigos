import React, { useState } from "react";
import { useAuth } from "../../modules/auth";
import { 
  Menu, 
  Bell, 
  Search, 
  Plus, 
  LogOut, 
  User, 
  Key, 
  ChevronDown,
  Globe,
  Settings
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export function AdminNavbar({ isSidebarCollapsed, onToggleSidebar, onOpenMobileDrawer }) {
  const { user, logout, hasPermission } = useAuth();
  const navigate = useNavigate();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isQuickActionOpen, setIsQuickActionOpen] = useState(false);
  const searchInputRef = React.useRef(null);

  // Focus search input on '/' keypress
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/admin/login");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  const getInitials = () => {
    if (user?.name) {
      const parts = user.name.split(" ");
      return parts.map(p => p[0]).join("").toUpperCase().slice(0, 2);
    }
    return "AD";
  };

  return (
    <header className="sticky top-0 z-25 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white px-4 shadow-sm select-none">
      
      {/* Left side: Hamburger Toggle & Search */}
      <div className="flex items-center space-x-3 flex-1">
        {/* Mobile Hamburger (visible on mobile only) */}
        <button
          onClick={onOpenMobileDrawer}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 lg:hidden focus:outline-none"
        >
          <Menu size={20} />
        </button>

        {/* Desktop Collapse Toggle (visible on desktop only) */}
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 hidden lg:flex focus:outline-none"
        >
          <Menu size={20} />
        </button>

        {/* Global Search Bar */}
        <div className="relative max-w-md w-full hidden md:block">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
            <Search size={16} />
          </span>
          <input
            ref={searchInputRef}
            type="search"
            placeholder="Search leads, bookings, proposals... (Press '/' to focus)"
            className="w-full pl-9 pr-4 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-slate-700"
          />
        </div>
      </div>

      {/* Right side: Actions, Notifications & Profile */}
      <div className="flex items-center space-x-4">
        {/* Quick Actions Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsQuickActionOpen(!isQuickActionOpen)}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm focus:outline-none transition-colors"
          >
            <Plus size={14} />
            <span className="hidden sm:inline">Quick Create</span>
            <ChevronDown size={12} />
          </button>
          
          {isQuickActionOpen && (
            <>
              <div 
                className="fixed inset-0 z-30" 
                onClick={() => setIsQuickActionOpen(false)}
              />
              <div className="absolute right-0 mt-2 w-52 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-40 text-xs text-slate-700 animate-in fade-in slide-in-from-top-2 duration-150">
                {hasPermission("crm.write") && (
                  <button
                    onClick={() => { setIsQuickActionOpen(false); navigate("/admin/crm/leads"); }}
                    className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center space-x-2 font-medium"
                  >
                    <span>+ New Lead Enquiry</span>
                  </button>
                )}
                {hasPermission("proposal.write") && (
                  <button
                    onClick={() => { setIsQuickActionOpen(false); navigate("/admin/proposals"); }}
                    className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center space-x-2 font-medium"
                  >
                    <span>+ New Proposal</span>
                  </button>
                )}
                {hasPermission("booking.write") && (
                  <button
                    onClick={() => { setIsQuickActionOpen(false); navigate("/admin/bookings"); }}
                    className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center space-x-2 font-medium"
                  >
                    <span>+ New Booking File</span>
                  </button>
                )}
              </div>
            </>
          )}
        </div>

        {/* Notifications Icon */}
        <button className="relative p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 focus:outline-none transition-colors">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
        </button>

        {/* Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="flex items-center space-x-2 focus:outline-none p-1 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-blue-100 border border-blue-200 text-blue-700 flex items-center justify-center font-bold text-xs select-none shadow-sm">
              {getInitials()}
            </div>
            <span className="text-xs font-semibold text-slate-700 hidden sm:block truncate max-w-[100px]">
              {user?.name || "Administrator"}
            </span>
            <ChevronDown size={14} className="text-slate-400 hidden sm:block" />
          </button>

          {isProfileOpen && (
            <>
              <div 
                className="fixed inset-0 z-30" 
                onClick={() => setIsProfileOpen(false)}
              />
              <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-lg shadow-lg py-1.5 z-40 text-xs text-slate-700 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-4 py-2 border-b border-slate-100">
                  <p className="font-semibold text-slate-800">{user?.name || "Administrator"}</p>
                  <p className="text-[10px] text-slate-400 mt-0.5 truncate">{user?.email || "test@example.com"}</p>
                  <p className="text-[10px] bg-blue-50 text-blue-700 inline-block px-1.5 py-0.5 rounded font-semibold mt-1">
                    {user?.role || "Admin"}
                  </p>
                </div>
                
                <button
                  onClick={() => { setIsProfileOpen(false); }}
                  className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center space-x-2 text-slate-600"
                >
                  <User size={14} />
                  <span>My Profile settings</span>
                </button>
                
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center space-x-2 text-red-600 border-t border-slate-100"
                >
                  <LogOut size={14} />
                  <span>Sign out portal</span>
                </button>
              </div>
            </>
          )}
        </div>

      </div>
    </header>
  );
}

export default AdminNavbar;
