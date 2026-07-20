import React from 'react';
import { useSmartTheme } from './DestinationThemeProvider';
import { getAccentClasses } from '../../data/destinationThemes';

export const TravelRecommendationCard = () => {
  const { weatherTips, themeData, loading, recommendations } = useSmartTheme();

  if (loading) {
    return (
      <div className="bg-white/40 backdrop-blur-md border border-white/20 p-6 rounded-3xl shadow-lg animate-pulse flex flex-col justify-between h-[180px]">
        <div className="space-y-3">
          <div className="h-4 bg-slate-200/50 rounded w-1/3"></div>
          <div className="h-5 bg-slate-200/50 rounded w-full"></div>
          <div className="h-4 bg-slate-100/50 rounded w-4/5"></div>
        </div>
        <div className="h-4 bg-slate-50/50 rounded w-1/2 mt-2"></div>
      </div>
    );
  }

  if (!weatherTips || !themeData) return null;

  const accentClasses = getAccentClasses(themeData.accent);
  const displayRecs = recommendations && recommendations.length > 0;

  return (
    <div className={`relative bg-white/70 backdrop-blur-md border border-white/40 p-6 rounded-3xl shadow-[0_15px_30px_-5px_rgba(0,0,0,0.05)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.08)] hover:-translate-y-1 hover:${accentClasses.border} flex flex-col justify-between h-[180px] group`}>
      {/* Ambient Glow */}
      <div className={`absolute -inset-0.5 bg-gradient-to-r ${accentClasses.gradient} rounded-3xl blur opacity-0 group-hover:opacity-[0.03] transition duration-500`}></div>

      <div className="z-10">
        <div className="flex items-center justify-between">
          <span className={`text-[9px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full ${accentClasses.badge}`}>
            Smart Recommendations
          </span>
          <span className="text-xl group-hover:animate-bounce transition-transform duration-500">💡</span>
        </div>

        <div className="mt-3.5 space-y-2 max-h-[80px] overflow-y-auto pr-1 select-none scrollbar-thin">
          {displayRecs ? (
            recommendations.map((rec, index) => (
              <div key={index} className="flex items-start gap-1.5 text-[11px] font-semibold text-slate-700 hover:text-slate-900 transition-colors duration-200">
                <span className={`text-[10px] ${accentClasses.text} shrink-0 mt-0.5`}>✦</span>
                <p className="leading-snug">{rec}</p>
              </div>
            ))
          ) : (
            <>
              {/* Tip */}
              <div className="flex items-start gap-2 text-xs font-semibold text-slate-700">
                <span className={`px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase ${accentClasses.badge} shrink-0 mt-0.5`}>
                  Tip
                </span>
                <p className="line-clamp-2 leading-snug">
                  {weatherTips.tip}
                </p>
              </div>

              {/* Packing */}
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                <span className="px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                  Pack
                </span>
                <p className="truncate leading-none">
                  {weatherTips.packing}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="border-t border-slate-100/60 pt-3 text-[10px] text-slate-400 font-bold tracking-wider uppercase flex items-center justify-between z-10">
        <span>BEST ACTIVITY:</span>
        <span className={`${accentClasses.text} font-black truncate max-w-[170px]`}>
          {weatherTips.activity}
        </span>
      </div>
    </div>
  );
};
