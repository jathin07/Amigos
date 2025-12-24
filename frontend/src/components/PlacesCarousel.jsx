const PlacesCarousel = ({ stateGroup }) => {
  // Safety check
  if (!stateGroup || !stateGroup.places) {
    console.error("Missing stateGroup or places:", stateGroup);
    return null;
  }

  return (
    <div className="mb-12">

      {/* Section Header */}
      <div className="flex items-center gap-3 mb-4 px-1">
        <h3 className="text-lg sm:text-xl md:text-2xl font-semibold text-gray-900">
          {stateGroup.state}
        </h3>
        <span className="flex-grow h-px bg-gray-300"></span>
      </div>

      {/* Horizontal Scroll Row */}
      <div
        className="flex overflow-x-auto gap-4 pb-3 scrollbar-hide snap-x snap-mandatory"
      >
        {stateGroup.places.map((place) => (
          <div
            key={place.name}
            className="snap-start w-[160px] sm:w-[180px] md:w-[200px] lg:w-[220px] shrink-0
                       bg-white shadow-md rounded-xl overflow-hidden
                       hover:scale-105 transition-transform duration-200"
          >

            {/* Image — Fixed Height, Uniform Crop */}
            <img
              src={place.image}
              alt={place.name}
              className="w-full h-36 sm:h-40 md:h-44 lg:h-48 object-cover object-center"
              loading="lazy"
            />

            {/* Place Name */}
            <div className="p-2 text-center font-medium text-gray-800 text-sm sm:text-base">
              {place.name}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
};

export default PlacesCarousel;
