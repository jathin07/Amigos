import React from 'react';
import { useSmartTheme } from './DestinationThemeProvider';

export const SmartHeroBackground = () => {
  const { themeData, activeCondition, loading } = useSmartTheme();

  if (loading || !themeData) return null;

  // If the simulated weather is Rainy, force show the rain effect.
  // Otherwise, use the destination's custom effect (mist, waves, rain, leaves).
  const activeEffect = activeCondition === 'Rain' ? 'rain' : themeData.effect;

  return (
    <div className="absolute inset-0 z-10 pointer-events-none overflow-hidden rounded-t-2xl">
      {/* Stylesheet containing custom animations */}
      <style>{`
        @keyframes mist-move {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes mist-move-reverse {
          0% { transform: translateX(-50%); }
          100% { transform: translateX(0); }
        }
        @keyframes wave-move {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        @keyframes wave-move-reverse {
          0% { transform: translateX(-50%); }
          100% { transform: translateX(0); }
        }
        @keyframes rain-fall {
          0% { background-position: 0 0; }
          100% { background-position: 20px 200px; }
        }
        @keyframes drift-leaves {
          0% { transform: translateY(-10px) translateX(0) rotate(0deg); opacity: 0; }
          10% { opacity: 0.8; }
          90% { opacity: 0.8; }
          100% { transform: translateY(320px) translateX(50px) rotate(360deg); opacity: 0; }
        }
      `}</style>

      {/* Dark overlay for text readability */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-black/10 z-0"></div>

      {/* 1. Mist Effect */}
      {activeEffect === 'mist' && (
        <div className="absolute inset-0 opacity-30 mix-blend-screen overflow-hidden">
          <div 
            className="absolute top-0 left-0 h-full w-[200%] animate-[mist-move_40s_linear_infinite]"
            style={{
              backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.7) 0%, transparent 40%), radial-gradient(circle at 70% 30%, rgba(255,255,255,0.6) 0%, transparent 45%)',
              backgroundSize: '50% 100%'
            }}
          />
          <div 
            className="absolute top-0 left-0 h-full w-[200%] animate-[mist-move-reverse_50s_linear_infinite] opacity-60"
            style={{
              backgroundImage: 'radial-gradient(circle at 40% 60%, rgba(255,255,255,0.5) 0%, transparent 35%), radial-gradient(circle at 80% 40%, rgba(255,255,255,0.6) 0%, transparent 40%)',
              backgroundSize: '50% 100%',
              animationDelay: '-15s'
            }}
          />
        </div>
      )}

      {/* 2. Waves Effect */}
      {activeEffect === 'waves' && (
        <div className="absolute bottom-0 left-0 w-full overflow-hidden leading-[0] opacity-80 select-none">
          <svg 
            className="relative block w-[200%] h-12 animate-[wave-move_16s_linear_infinite]" 
            viewBox="0 0 1200 120" 
            preserveAspectRatio="none"
          >
            <path 
              d="M0,60 C150,90 350,30 500,60 C650,90 850,30 1000,60 C1150,90 1350,30 1500,60 L1500,120 L0,120 Z" 
              fill="#ffffff" 
              opacity="0.25"
            />
          </svg>
          <svg 
            className="relative block w-[200%] h-10 -mt-8 animate-[wave-move-reverse_12s_linear_infinite]" 
            viewBox="0 0 1200 120" 
            preserveAspectRatio="none"
          >
            <path 
              d="M0,50 C150,80 300,20 450,50 C600,80 750,20 900,50 C1050,80 1200,20 1350,50 L1350,120 L0,120 Z" 
              fill="#ffffff" 
              opacity="0.4"
            />
          </svg>
        </div>
      )}

      {/* 3. Rain Effect */}
      {activeEffect === 'rain' && (
        <div className="absolute inset-0 mix-blend-screen opacity-30">
          <div 
            className="absolute inset-0 w-full h-[200%] animate-[rain-fall_1.2s_linear_infinite]"
            style={{
              backgroundImage: 'linear-gradient(to bottom, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.4) 10%, transparent 10%)',
              backgroundSize: '3px 60px'
            }}
          />
          <div 
            className="absolute inset-0 w-full h-[200%] animate-[rain-fall_1.6s_linear_infinite] opacity-60"
            style={{
              backgroundImage: 'linear-gradient(to bottom, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.3) 15%, transparent 15%)',
              backgroundSize: '2px 45px',
              animationDelay: '-0.5s',
              animationDirection: 'reverse'
            }}
          />
        </div>
      )}

      {/* 4. Leaves/Jungle Effect */}
      {activeEffect === 'leaves' && (
        <div className="absolute inset-0 opacity-40">
          {[
            { delay: '0s', left: '10%', size: 'w-3 h-3' },
            { delay: '2s', left: '35%', size: 'w-4 h-4' },
            { delay: '4s', left: '60%', size: 'w-3 h-3' },
            { delay: '1.5s', left: '80%', size: 'w-5 h-5' },
            { delay: '5.5s', left: '22%', size: 'w-3 h-4' },
            { delay: '3.5s', left: '72%', size: 'w-4 h-3' }
          ].map((leaf, index) => (
            <div
              key={index}
              className={`absolute top-0 ${leaf.size} bg-emerald-600/30 rounded-full animate-[drift-leaves_8s_linear_infinite]`}
              style={{
                left: leaf.left,
                animationDelay: leaf.delay,
                clipPath: 'polygon(50% 0%, 100% 35%, 100% 70%, 50% 100%, 0% 70%, 0% 35%)'
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};
