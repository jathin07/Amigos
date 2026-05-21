import { useMemo } from 'react';

const journeyMedia = [
  { id: 1, type: "image", src: "/images/customers/c1.jpg", caption: "Munnar Adventure" },
  { id: 2, type: "image", src: "/images/customers/c2.jpg", caption: "Coorg Escape" },
  { id: 3, type: "image", src: "/images/customers/c3.jpg", caption: "Wayanad Diaries" },
  { id: 4, type: "image", src: "/images/customers/c4.jpg", caption: "Ooty Escapade" },
  { id: 5, type: "image", src: "/images/customers/c5.jpg", caption: "Goa Vibes" },
  { id: 6, type: "image", src: "/images/customers/c6.jpg", caption: "Gokarna Treks" },
  { id: 7, type: "image", src: "/images/customers/c7.jpg", caption: "River Rafting" },
  { id: 8, type: "image", src: "/images/customers/c8.jpg", caption: "Pine Forests" },
  { id: 9, type: "image", src: "/images/customers/c9.jpg", caption: "Coffee Estates" },
  { id: 10, type: "image", src: "/images/customers/c10.jpg", caption: "Houseboat Chill" },
];

const desktopTransforms = [
  "md:-translate-y-8 md:-translate-x-6 md:-rotate-6",
  "md:translate-y-12 md:rotate-3",
  "md:-translate-y-4 md:translate-x-6 md:rotate-6",
  "md:translate-y-6 md:-translate-x-8 md:rotate-2",
  "md:-translate-y-12 md:-rotate-3",
  "md:translate-y-8 md:translate-x-8 md:-rotate-6",
];

const PolaroidGallery = () => {
  // Randomly select exactly 6 images without mutating the original array
  const displayImages = useMemo(() => {
    const shuffled = [...journeyMedia].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 6);
  }, []);

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
      <div className="text-center mb-16 md:mb-24">
        <h2 className="text-3xl sm:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">Our Journey</h2>
        <p className="text-gray-500 max-w-2xl mx-auto text-lg leading-relaxed">
          Thousands of memories, countless adventures, and unforgettable experiences across South India.
        </p>
      </div>

      {/* Grid container with top/bottom padding to prevent transforms from clipping */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 md:gap-x-12 md:gap-y-24 md:py-16">
        {displayImages.map((item, idx) => {
          const transformClass = desktopTransforms[idx % desktopTransforms.length];
          return (
            <div
              key={item.id}
              className={`group relative bg-white p-3 sm:p-4 pb-14 sm:pb-16 rounded shadow-[0_10px_30px_rgba(0,0,0,0.1)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.2)] transition-all duration-500 ease-out transform ${transformClass} hover:!rotate-0 hover:!translate-y-0 hover:!translate-x-0 hover:scale-[1.07] hover:z-50 mx-auto w-[90%] sm:w-full max-w-[320px]`}
            >
              <div className="relative w-full aspect-square overflow-hidden bg-gray-100">
                <img
                  src={item.src}
                  alt={item.caption}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  loading="lazy"
                />
              </div>
              <div className="absolute bottom-0 left-0 w-full h-14 sm:h-16 flex items-center justify-center px-4">
                <span className="font-medium text-gray-700 text-sm sm:text-base italic opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0">
                  {item.caption}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PolaroidGallery;
