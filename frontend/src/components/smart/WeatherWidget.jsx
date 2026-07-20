import React from 'react';
import { useSmartTheme } from './DestinationThemeProvider';
import { getAccentClasses } from '../../data/destinationThemes';

export const WeatherWidget = () => {
  const { weatherData, activeCondition, themeData, loading, isLive } = useSmartTheme();
  const [currentTime, setCurrentTime] = React.useState(new Date());

  React.useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  if (loading) {
    return (
      <div className="bg-white/40 backdrop-blur-md border border-white/20 p-6 rounded-3xl shadow-lg animate-pulse flex flex-col justify-between h-[180px]">
        <div className="space-y-3">
          <div className="h-4 bg-slate-200/50 rounded w-1/3"></div>
          <div className="h-10 bg-slate-200/50 rounded w-24"></div>
          <div className="h-4 bg-slate-200/50 rounded w-1/2"></div>
        </div>
        <div className="h-4 bg-slate-200/30 rounded w-full mt-4"></div>
      </div>
    );
  }

  if (!weatherData || !themeData) return null;

  const accentClasses = getAccentClasses(themeData.accent);
  const formattedTime = currentTime.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });

  const renderWeatherIcon = () => {
    switch (activeCondition) {
      case 'Clear':
        return (
          <div className="relative w-14 h-14 flex items-center justify-center">
            {/* Spinning sun rays */}
            <div className="absolute inset-0 border-4 border-dashed border-amber-400 rounded-full animate-[spin_30s_linear_infinite] opacity-60"></div>
            {/* Inner sun body */}
            <div className="w-8 h-8 bg-gradient-to-br from-amber-300 to-amber-500 rounded-full shadow-[0_0_15px_rgba(245,158,11,0.5)]"></div>
          </div>
        );
      case 'Rain':
        return (
          <div className="relative w-14 h-14 flex flex-col items-center justify-center">
            {/* Cloud body */}
            <svg className="w-10 h-10 text-slate-400 drop-shadow-md" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
            </svg>
            {/* Raindrops */}
            <div className="absolute bottom-1.5 flex gap-2 justify-center w-full">
              <span className="w-0.5 h-2 bg-blue-400 rounded-full animate-[bounce_1s_infinite] delay-0"></span>
              <span className="w-0.5 h-2 bg-blue-400 rounded-full animate-[bounce_1s_infinite] delay-150"></span>
              <span className="w-0.5 h-2 bg-blue-400 rounded-full animate-[bounce_1s_infinite] delay-300"></span>
            </div>
          </div>
        );
      case 'Clouds':
      default:
        return (
          <div className="relative w-14 h-14 flex items-center justify-center">
            {/* Behind Cloud (Sun peek) */}
            <div className="absolute top-1 right-1 w-6 h-6 bg-amber-400 rounded-full animate-pulse opacity-80"></div>
            {/* Main Cloud */}
            <svg className="absolute w-11 h-11 text-slate-300 drop-shadow-md" fill="currentColor" viewBox="0 0 24 24">
              <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z" />
            </svg>
          </div>
        );
    }
  };

  return (
    <div className={`relative bg-white/70 backdrop-blur-md border border-white/40 p-6 rounded-3xl shadow-[0_15px_30px_-5px_rgba(0,0,0,0.05)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.08)] hover:-translate-y-1 hover:${accentClasses.border} flex flex-col justify-between h-[180px] group`}>
      {/* Dynamic Glow background */}
      <div className={`absolute -inset-0.5 bg-gradient-to-r ${accentClasses.gradient} rounded-3xl blur opacity-0 group-hover:opacity-[0.03] transition duration-500`}></div>

      {/* Top Header Section */}
      <div className="flex justify-between items-start z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className={`text-[9px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full ${accentClasses.badge}`}>
              Weather
            </span>
            <span className="flex items-center gap-1 text-[10px] text-slate-400 font-semibold bg-slate-50 px-2 py-0.5 rounded-full border border-slate-100">
              <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`}></span>
              {isLive ? 'Live Sync' : 'Simulated'}
            </span>
          </div>

          <div className="flex items-baseline gap-1 mt-3">
            <h3 className="text-4xl font-black text-slate-800 tracking-tight">{weatherData.temp}</h3>
            <span className="text-xl font-extrabold text-slate-400">°C</span>
          </div>
          <p className="text-slate-500 text-xs font-bold capitalize mt-1 flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-slate-200"></span>
            {activeCondition === 'Clear' ? 'Sunny & Clear' : activeCondition === 'Rain' ? 'Rainy / Showers' : 'Overcast / Cloudy'}
          </p>
        </div>

        <div className="flex flex-col items-end gap-1">
          <div className="p-1.5 bg-white/90 rounded-2xl shadow-sm border border-slate-50 group-hover:scale-110 transition-transform duration-500">
            {renderWeatherIcon()}
          </div>
          <span className="text-[10px] font-bold text-slate-400 mt-1.5 bg-slate-100/60 px-2 py-0.5 rounded-md">
            {formattedTime}
          </span>
        </div>
      </div>

      {/* Bottom Grid Metrics */}
      <div className="grid grid-cols-3 gap-2 pt-4 border-t border-slate-100/60 text-[10px] text-slate-400 font-bold tracking-wider uppercase z-10">
        <div className="transition-transform duration-300 hover:scale-105">
          <span className="block text-[9px] text-slate-400/80 font-bold mb-0.5">HUMIDITY</span>
          <span className="text-slate-700 text-xs font-black">{weatherData.humidity}%</span>
        </div>
        <div className="transition-transform duration-300 hover:scale-105">
          <span className="block text-[9px] text-slate-400/80 font-bold mb-0.5">WIND</span>
          <span className="text-slate-700 text-xs font-black">{weatherData.wind_speed} km/h</span>
        </div>
        <div className="transition-transform duration-300 hover:scale-105">
          <span className="block text-[9px] text-slate-400/80 font-bold mb-0.5">SUNSET</span>
          <span className="text-slate-700 text-xs font-black">{weatherData.sunset}</span>
        </div>
      </div>
    </div>
  );
};
