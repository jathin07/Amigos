import React from "react";
import AdminSidebar from "./AdminSidebar";
import { X } from "lucide-react";

export function MobileDrawer({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 lg:hidden">
      {/* Backdrop Backdrop blur filter */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Drawer Container Panel */}
      <div className="fixed inset-y-0 left-0 w-64 bg-slate-900 flex flex-col shadow-2xl animate-in slide-in-from-left duration-250 z-50">
        
        {/* Close Button overlay */}
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Render full AdminSidebar inside drawer */}
        <div className="h-full flex-1">
          <AdminSidebar isCollapsed={false} onToggle={onClose} />
        </div>
      </div>
    </div>
  );
}

export default MobileDrawer;
