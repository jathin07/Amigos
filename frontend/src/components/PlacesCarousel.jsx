import { useRef } from 'react';

const PlacesCarousel = ({ stateGroup }) => {
  const scrollContainerRef = useRef(null);

  // Safety check
  if (!stateGroup || !stateGroup.places) {
    console.error("Missing stateGroup or places:", stateGroup);
    return null;
  }

  const scroll = (direction) => {
    if (scrollContainerRef.current) {
      const { current } = scrollContainerRef;
      const scrollAmount = direction === "left" ? -320 : 320;
      current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  return (
    <div className="mb-12 relative group/section">

      {/* Section Header */}
      <div className="flex items-center gap-4 mb-6 px-2 sm:px-4">
        <h3 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 tracking-tight">
          {stateGroup.state}
        </h3>
        <div className="h-1 flex-1 rounded-full bg-gradient-to-r from-gray-200 to-transparent"></div>
        {/* Subtle accent line */}
      </div>

      {/* Navigation 'Cheat' Arrows - Visible on Desktop Hover */}
      {/* Left Arrow */}
      <button
        onClick={() => scroll('left')}
        className="absolute left-2 top-[60%] -translate-y-1/2 z-20 
                   p-3 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white shadow-lg
                   opacity-0 group-hover/section:opacity-100 transition-all duration-300 transform 
                   hover:bg-white/20 hover:scale-110 hidden md:flex items-center justify-center"
        aria-label="Scroll left"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* Right Arrow */}
      <button
        onClick={() => scroll('right')}
        className="absolute right-2 top-[60%] -translate-y-1/2 z-20 
                   p-3 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white shadow-lg
                   opacity-0 group-hover/section:opacity-100 transition-all duration-300 transform 
                   hover:bg-white/20 hover:scale-110 hidden md:flex items-center justify-center"
        aria-label="Scroll right"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Horizontal Scroll Row */}
      <div
        ref={scrollContainerRef}
        className="flex overflow-x-auto gap-5 pb-8 px-4 sm:px-8 scrollbar-hide snap-x snap-mandatory 
                   [mask-image:linear-gradient(to_right,transparent,black_5%,black_95%,transparent)]"
      >
        {stateGroup.places.map((place) => (
          <div
            key={place.name}
            className="group/card relative snap-start shrink-0 
                       w-[220px] sm:w-[260px] md:w-[280px] lg:w-[300px] aspect-[3/4]
                       rounded-2xl overflow-hidden cursor-pointer bg-gray-900 shadow-xl
                       transition-all duration-500 ease-out
                       hover:-translate-y-3 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.6)]"
          >
            {/* Image Layer */}
            <img
              src={place.image}
              alt={place.name}
              className="w-full h-full object-cover transition-transform duration-700 ease-in-out group-hover/card:scale-110"
              loading="lazy"
            />

            {/* Dark Overlay - Lightens on hover */}
            <div className="absolute inset-0 bg-black/40 transition-colors duration-500 group-hover/card:bg-black/20" />

            {/* Glassmorphism Text Container */}
            <div className="absolute bottom-4 left-4 right-4 
                          bg-white/10 backdrop-blur-lg border border-white/10 shadow-lg rounded-xl p-4
                          transition-all duration-500 transform translate-y-2 
                          group-hover/card:translate-y-0 group-hover/card:bg-white/20 group-hover/card:border-white/30"
            >
              <h4 className="text-white font-bold text-lg leading-tight dropshadow-md">
                {place.name}
              </h4>
              {/* Optional subtext or decoration could go here */}
            </div>

            {/* Subtle shiny border effect on hover */}
            <div className="absolute inset-0 rounded-2xl border-2 border-transparent group-hover/card:border-white/30 pointer-events-none transition-colors duration-500" />

          </div>
        ))}
      </div>

    </div>
  );
};

export default PlacesCarousel;
