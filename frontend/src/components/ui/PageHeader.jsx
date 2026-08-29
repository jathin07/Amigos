import React from "react";
import { ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";

export function PageHeader({
  breadcrumbs = [],
  title,
  description,
  actions,
  children,
}) {
  return (
    <div className="flex flex-col space-y-3 pb-2 border-b border-slate-200/80 shrink-0 select-none">
      
      {/* Breadcrumb Navigation Trail */}
      {breadcrumbs.length > 0 && (
        <nav className="flex items-center space-x-1.5 text-xs font-semibold text-slate-400 overflow-x-auto scrollbar-thin">
          {breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1;
            return (
              <React.Fragment key={index}>
                {index > 0 && <ChevronRight size={12} className="text-slate-400 shrink-0" />}
                {crumb.href && !isLast ? (
                  <Link
                    to={crumb.href}
                    className="hover:text-blue-600 transition-colors whitespace-nowrap"
                  >
                    {crumb.label}
                  </Link>
                ) : (
                  <span
                    className={`whitespace-nowrap ${
                      isLast ? "text-slate-600 font-semibold" : "hover:text-slate-600"
                    }`}
                  >
                    {crumb.label}
                  </span>
                )}
              </React.Fragment>
            );
          })}
        </nav>
      )}

      {/* Title & Top Right Actions */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="space-y-0.5">
          {title && (
            <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
              {title}
            </h1>
          )}
          {description && (
            <p className="text-xs md:text-sm text-slate-500 max-w-3xl leading-relaxed">
              {description}
            </p>
          )}
        </div>

        {actions && (
          <div className="flex items-center space-x-2.5 shrink-0">
            {actions}
          </div>
        )}
      </div>

      {children && <div className="pt-2">{children}</div>}
    </div>
  );
}

export default PageHeader;
