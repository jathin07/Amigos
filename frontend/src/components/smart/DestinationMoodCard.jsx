import React from 'react';
import { useSmartTheme } from './DestinationThemeProvider';
import { getAccentClasses } from '../../data/destinationThemes';

export const DestinationMoodCard = () => {
  const { mood, themeData, loading } = useSmartTheme();

  if (loading) {
    return (
      <div className="bg-white/40 backdrop-blur-md border border-white/20 p-6 rounded-3xl shadow-lg animate-pulse flex flex-col justify-between h-[180px]">
        <div className="space-y-3">
          <div className="h-4 bg-slate-200/50 rounded w-1/4"></div>
          <div className="h-7 bg-slate-200/50 rounded w-3/4"></div>
          <div className="h-4 bg-slate-100/50 rounded w-5/6"></div>
        </div>
        <div className="h-4 bg-slate-50/50 rounded w-2/3 mt-2"></div>
      </div>
    );
  }

  if (!themeData) return null;

  const accentClasses = getAccentClasses(themeData.accent);

  return (
    <div className={`relative bg-white/70 backdrop-blur-md border border-white/40 p-6 rounded-3xl shadow-[0_15px_30px_-5px_rgba(0,0,0,0.05)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.08)] hover:-translate-y-1 hover:${accentClasses.border} flex flex-col justify-between h-[180px] group`}>
      {/* Ambient Glow */}
      <div className={`absolute -inset-0.5 bg-gradient-to-r ${accentClasses.gradient} rounded-3xl blur opacity-0 group-hover:opacity-[0.03] transition duration-500`}></div>

      <div className="z-10">
        <div className="flex items-center justify-between">
          <span className={`text-[9px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full ${accentClasses.badge}`}>
            Destination Mood
          </span>
          <span className="text-xl group-hover:rotate-12 transition-transform duration-500">🌿</span>
        </div>
        
        <h3 className="text-2xl font-black text-slate-800 mt-3.5 leading-tight tracking-tight">
          {mood}
        </h3>
        <p className="text-slate-500 text-[11px] font-bold tracking-wide mt-1.5 italic font-sans flex items-start gap-1">
          <span className={accentClasses.text}>“</span>
          <span>{themeData.tagline}</span>
          <span className={accentClasses.text}>”</span>
        </p>
      </div>

      <div className="border-t border-slate-100/60 pt-3 z-10">
        <p className="text-[11px] text-slate-500 font-bold leading-relaxed line-clamp-2">
          {themeData.personality}
        </p>
      </div>
    </div>
  );
};
