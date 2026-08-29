import React, { useState, useEffect } from "react";
import { Outlet, Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../modules/auth";
import AdminSidebar from "./AdminSidebar";
import AdminNavbar from "./AdminNavbar";
import MobileDrawer from "./MobileDrawer";

export function AdminLayout() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem("admin_sidebar_collapsed");
    return saved ? JSON.parse(saved) : false;
  });
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setIsMobileDrawerOpen(false);
  }, [location.pathname]);

  // Persist sidebar collapsed status
  const handleToggleSidebar = () => {
    setIsSidebarCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("admin_sidebar_collapsed", JSON.stringify(next));
      return next;
    });
  };

  // Auth Guard integration
  if (isLoading) {
    return null; // Let the global router auth loading spinner handle initial states
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 flex overflow-hidden">
      
      {/* 1. Left Side: Sidebar navigation (Desktop) */}
      <div className="hidden lg:block shrink-0">
        <AdminSidebar 
          isCollapsed={isSidebarCollapsed} 
          onToggle={handleToggleSidebar} 
        />
        {/* Placeholder spacer to push content when fixed sidebar is active */}
        <div className={`transition-all duration-300 ${isSidebarCollapsed ? "w-16" : "w-64"}`} />
      </div>

      {/* 2. Mobile slide-out Drawer navigation */}
      <MobileDrawer 
        isOpen={isMobileDrawerOpen} 
        onClose={() => setIsMobileDrawerOpen(false)} 
      />

      {/* 3. Right Side: Top bar & content wrapper */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        
        {/* Top Header navbar bar */}
        <AdminNavbar 
          isSidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={handleToggleSidebar}
          onOpenMobileDrawer={() => setIsMobileDrawerOpen(true)}
        />

        {/* Scrollable primary content viewport container */}
        <main className="flex-1 overflow-y-auto bg-slate-50 p-4 md:p-6 focus:outline-none scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent">
          <Outlet />
        </main>
      </div>

    </div>
  );
}

export default AdminLayout;
