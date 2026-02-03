import { useState } from "react";

const PackageCard = ({
  packageData,
  mode = "preview",        // "preview" | "expandable"
  expanded = false,
  onToggle,
}) => {
  const isExpandable = mode === "expandable";

  // Check for Industrial Visit in highlights
  const hasIV = packageData.highlights?.some(h =>
    h.toLowerCase().includes("industrial visit") || h.toLowerCase().includes("iv included")
  );

  return (
    <div className={`bg-white shadow-lg rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-2xl group flex flex-col h-full ${expanded ? 'ring-2 ring-blue-100' : ''}`}>

      {/* Image Container with 16:9 Aspect Ratio */}
      <div className="relative w-full aspect-video overflow-hidden">
        <img
          src={packageData.image}
          alt={packageData.name}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />

        {/* Floating Price Badge */}
        {packageData.price && (
          <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full shadow-md z-10">
            <span className="text-blue-700 font-bold text-sm">{packageData.price}</span>
          </div>
        )}

        {/* IV Included Badge */}
        {hasIV && (
          <div className="absolute bottom-4 left-4 bg-indigo-600 text-white text-[10px] font-bold px-2 py-1 rounded shadow-lg flex items-center gap-1 z-10">
            <span>🏭</span>
            <span>IV INCLUDED</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5 flex flex-col flex-grow">
        <div className="flex-grow">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-bold text-gray-900 leading-tight group-hover:text-blue-600 transition-colors">
              {packageData.name}
            </h3>
          </div>

          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {packageData.description}
          </p>

          <div className="flex flex-wrap gap-2 mb-4">
            {packageData.tags?.slice(0, 3).map(tag => (
              <span key={tag} className="text-[10px] bg-gray-100 text-gray-500 px-2 py-1 rounded-md font-medium">
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* Expanded Details Section */}
        <div className={`overflow-hidden transition-all duration-500 ease-in-out ${expanded ? 'max-h-[500px] opacity-100 mt-4' : 'max-h-0 opacity-0'}`}>
          <div className="bg-blue-50/50 rounded-xl p-4 border border-blue-100 shadow-[inset_0_1px_4px_rgba(0,0,0,0.05)]">
            <h4 className="flex items-center gap-2 text-sm font-bold text-gray-900 mb-3 uppercase tracking-wider">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
              Trip Highlights
            </h4>
            <ul className="space-y-2 text-sm text-gray-700">
              {packageData.highlights?.map((item, index) => (
                <li key={index} className="flex items-start gap-2.5">
                  <span className="text-blue-500 text-xs mt-1">✦</span>
                  <span className="leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-3 pt-2 border-t border-gray-100">
          {isExpandable && (
            <button
              onClick={onToggle}
              className="flex-1 px-4 py-2.5 rounded-xl text-sm font-semibold text-gray-600 bg-gray-50 hover:bg-gray-100 hover:text-gray-900 transition-colors duration-200"
            >
              {expanded ? "Close" : "View Highlights"}
            </button>
          )}

          <button className="flex-1 bg-gradient-to-r from-blue-600 to-blue-500 text-white px-4 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-[1.02] active:scale-95 transition-all duration-300 flex items-center justify-center gap-2 group/btn">
            Plan Now
            <span className="group-hover/btn:translate-x-1 transition-transform">→</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PackageCard;
