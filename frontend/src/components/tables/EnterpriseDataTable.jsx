import React from "react";
import { ChevronLeft, ChevronRight, Inbox, Loader2 } from "lucide-react";

export function EnterpriseDataTable({
  columns = [],
  data = [],
  isLoading = false,
  pageIndex = 0,
  pageSize = 10,
  totalCount = 0,
  onPageChange,
  onPageSizeChange,
  emptyStateTitle = "No records found",
  emptyStateDescription = "Get started by creating a new entry.",
  emptyStateAction,
}) {
  const pageCount = Math.ceil(totalCount / pageSize) || 1;
  const startIdx = totalCount === 0 ? 0 : pageIndex * pageSize + 1;
  const endIdx = Math.min((pageIndex + 1) * pageSize, totalCount);

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm flex flex-col min-w-0">
      
      {/* Scrollable table container */}
      <div className="overflow-x-auto min-w-0 flex-1 relative min-h-[300px]">
        
        {/* Loading Overlay */}
        {isLoading && data.length > 0 && (
          <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center z-10 transition-all">
            <div className="flex items-center space-x-2 bg-slate-900 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-lg">
              <Loader2 className="animate-spin text-blue-500" size={16} />
              <span>Updating records...</span>
            </div>
          </div>
        )}

        <table className="w-full text-left border-collapse table-auto text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 sticky top-0 z-5 select-none">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className={`px-4 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-500 ${
                    col.className || ""
                  }`}
                  style={col.style}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          
          <tbody className="divide-y divide-slate-100 bg-white">
            {isLoading && data.length === 0 ? (
              // Loading skeletons
              Array.from({ length: pageSize }).map((_, rIdx) => (
                <tr key={rIdx} className="animate-pulse">
                  {columns.map((_, cIdx) => (
                    <td key={cIdx} className="px-4 py-4">
                      <div className="h-4 bg-slate-100 rounded w-4/5" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              // Empty State
              <tr>
                <td colSpan={columns.length} className="px-4 py-16 text-center">
                  <div className="max-w-sm mx-auto flex flex-col items-center justify-center space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400">
                      <Inbox size={22} />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-slate-800">{emptyStateTitle}</h3>
                      <p className="text-xs text-slate-500 mt-1">{emptyStateDescription}</p>
                    </div>
                    {emptyStateAction}
                  </div>
                </td>
              </tr>
            ) : (
              // Table Rows
              data.map((row, rIdx) => (
                <tr
                  key={row.id || rIdx}
                  className="hover:bg-slate-50/70 transition-colors text-slate-700 font-medium"
                >
                  {columns.map((col, cIdx) => {
                    const value = col.accessorKey ? row[col.accessorKey] : undefined;
                    return (
                      <td
                        key={cIdx}
                        className={`px-4 py-3.5 text-xs text-slate-600 ${col.className || ""}`}
                        style={col.style}
                      >
                        {col.render ? col.render(row, value) : value ?? "—"}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {data.length > 0 && (
        <div className="px-4 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between flex-wrap gap-3 select-none text-xs font-semibold text-slate-500 shrink-0">
          
          {/* Sizing options */}
          <div className="flex items-center space-x-2">
            <span>Rows per page:</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange?.(Number(e.target.value))}
              className="bg-white border border-slate-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-slate-600"
            >
              {[10, 25, 50, 100].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>

          {/* Record indicators */}
          <div className="text-slate-500">
            Showing <span className="font-semibold text-slate-800">{startIdx}</span> to{" "}
            <span className="font-semibold text-slate-800">{endIdx}</span> of{" "}
            <span className="font-semibold text-slate-800">{totalCount}</span> entries
          </div>

          {/* Navigation controls */}
          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => onPageChange?.(pageIndex - 1)}
              disabled={pageIndex === 0 || isLoading}
              className="p-1.5 border border-slate-200 rounded bg-white hover:bg-slate-50 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:text-slate-500 transition-colors"
            >
              <ChevronLeft size={14} />
            </button>
            
            <div className="px-2 text-slate-700">
              Page <span className="font-semibold text-slate-900">{pageIndex + 1}</span> of{" "}
              <span className="font-semibold text-slate-900">{pageCount}</span>
            </div>

            <button
              onClick={() => onPageChange?.(pageIndex + 1)}
              disabled={pageIndex + 1 >= pageCount || isLoading}
              className="p-1.5 border border-slate-200 rounded bg-white hover:bg-slate-50 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:text-slate-500 transition-colors"
            >
              <ChevronRight size={14} />
            </button>
          </div>

        </div>
      )}

    </div>
  );
}

export default EnterpriseDataTable;
