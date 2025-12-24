import { Link } from "react-router-dom";
import PackageCard from "../components/PackageCard";
import "./Home.css";
import { placesByState } from "../data/PlacesData";
import { useParallax } from "../hooks/useParallax";
import { useRef, useState } from "react";
import PlacesCarousel from "../components/PlacesCarousel";

const Home = () => {
  // Featured packages
  const featuredPackages = [
    {
      id: 1,
      name: "Ooty Getaway",
      description: "3 Nights 4 Days in the Queen of Hills.",
      image: "/images/ooty.jpg",
    },
    {
      id: 2,
      name: "Goa Beach Vibes",
      description: "Enjoy the sun, sand, and sea — 4 Nights package.",
      image: "/images/goa.jpg",
    },
    {
      id: 3,
      name: "Kerala Backwaters",
      description: "Serene houseboat trip in Alleppey — 3 Nights.",
      image: "/images/kerala.jpg",
    },
  ];

  // Our Journey (videos & photos)
  const journeyMedia = [
    { id: 1, type: "video", src: "/videos/trip1.mp4" },
    { id: 2, type: "image", src: "/images/journey1.jpg" },
    { id: 3, type: "image", src: "/images/journey2.jpg" },
    { id: 4, type: "video", src: "/videos/trip2.mp4" },
  ];

  const row1Ref = useRef(null);
  const row2Ref = useRef(null);
  useParallax(row1Ref, 0.15);
  useParallax(row2Ref, 0.3);

  const images = ["Trip1", "Trip2", "Trip3", "Trip4"];
  const [activeState, setActiveState] = useState("Tamil Nadu");

  return (
    <div className="w-full max-w-[100vw] overflow-x-hidden px-2 sm:px-6 lg:px-8">


      {/* ===== Parallax Hero Section ===== */}
      <section className="relative w-full min-h-[55vh] sm:min-h-[65vh] md:min-h-[70vh] lg:h-[85vh] overflow-hidden rounded-2xl sm:rounded-3xl mb-12">

        {/* Row 1 - slower parallax; hidden on very small screens for perf */}
        <div
          ref={row1Ref}
          className="absolute inset-0 opacity-70 overflow-hidden hidden sm:block"
        >
          <div className="scroll-row animate-scroll-left h-full">
            {images.map((img) => (
              <img
                key={img}
                src={`/images/trip/${img}.jpg`}
                className="h-full object-cover mx-2 rounded-lg min-w-[260px] sm:min-w-[320px] md:min-w-[380px]"
                alt={img}
              />
            ))}
          </div>
        </div>

        {/* Row 2 - moves faster; hidden on very small screens */}
        <div
          ref={row2Ref}
          className="absolute inset-0 opacity-60 overflow-hidden hidden sm:block"
        >
          <div className="scroll-row animate-scroll-right h-full">
            {images.map((img) => (
              <img
                key={img + "2"}
                src={`/images/trip/${img}.jpg`}
                className="h-full object-cover mx-2 rounded-lg min-w-[260px] sm:min-w-[320px] md:min-w-[380px]"
                alt={img}
              />
            ))}
          </div>
        </div>

        {/* Fallback single background image on small screens */}
        <div
          className="absolute inset-0 bg-cover bg-center sm:hidden"
          style={{ backgroundImage: "url('/images/trip/Trip1.jpg')" }}
          aria-hidden="true"
        />

        <div className="absolute inset-0 bg-black/50"></div>

        <div className="relative z-10 flex flex-col items-center justify-center text-center h-full text-white px-4">
          <h1 className="text-2xl sm:text-4xl md:text-6xl font-extrabold mb-3 sm:mb-4 leading-tight">
            Discover. Travel. Live. ✈️
          </h1>
          <p className="text-sm sm:text-base md:text-lg mb-4 sm:mb-6 max-w-lg sm:max-w-3xl">
            Student-friendly & budget smart tours — curated with love 💙
          </p>

          <Link
            to="/plan-trip"
            className="bg-white text-blue-700 px-6 py-2 sm:px-8 sm:py-3 rounded-full text-sm sm:text-lg font-semibold hover:bg-gray-200 transition"
          >
            Plan My Trip
          </Link>
        </div>
      </section>

      {/* ===== Places We Cover ===== */}
      <section className="mb-12">
        <h2 className="text-2xl sm:text-3xl font-bold mb-6 text-gray-800 text-center">
          Top Places We Cover
        </h2>

        <div className="mb-6">
          {/* horizontally scrollable on small, wrapped on larger screens */}
          <div className="flex gap-3 overflow-x-auto py-2 px-1 scrollbar-hide sm:flex-wrap sm:justify-center">
            {placesByState.map((group) => (
              <button
                key={group.state}
                onClick={() => setActiveState(group.state)}
                className={`px-4 py-2 rounded-full text-sm font-medium border whitespace-nowrap transition
                ${activeState === group.state
                  ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-100 active:scale-95"
                }`}

              >
                {group.state}
              </button>
            ))}
          </div>
        </div>

        {placesByState
          .filter((group) => group.state === activeState)
          .map((group) => <PlacesCarousel key={group.state} stateGroup={group} />)}
      </section>

      {/* ===== Featured Packages ===== */}
      <section className="mb-12">
        <h2 className="text-xl text-center sm:text-2xl font-bold mb-4 text-gray-800">
          Featured Packages
        </h2>
        <div className="flex overflow-x-auto gap-4 pb-3 scrollbar-hide sm:grid sm:grid-cols-2 md:grid-cols-3 sm:gap-6">
          {featuredPackages.map((pkg) => (
            <div key={pkg.id} className="min-w-[240px] sm:min-w-0">
              <PackageCard packageData={pkg} />
            </div>
          ))}
        </div>

        <div className="text-center mt-6">
          <Link
            to="/packages"
            className="bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 text-sm sm:text-base w-full sm:w-auto"

          >
            Browse All Packages
          </Link>
        </div>
      </section>

      {/* ===== Our Journey ===== */}
      <section className="py-8 bg-gray-50 mb-12">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6 text-gray-800">
          Our Journey
        </h2>
        <div className="flex overflow-x-auto space-x-4 px-4 sm:px-6 scrollbar-hide">
          {journeyMedia.map((item) => (
            <div key={item.id} className="min-w-[240px] sm:min-w-[320px] relative">
              {item.type === "video" ? (
                <video
                  src={item.src}
                  controls
                  className="rounded-xl shadow-md w-full h-44 sm:h-52 md:h-56 object-cover"
                />
              ) : (
                <img
                  src={item.src}
                  alt="journey"
                  className="rounded-xl shadow-md w-full h-44 sm:h-52 md:h-56 object-cover hover:scale-105 transition-transform duration-300"
                />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ===== Reviews Section ===== */}
      <section className="bg-gray-50 py-8 mb-12">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6 text-gray-800">
          What Our Travelers Say
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 px-4 sm:px-6">
          {[
            {
              name: "Arun",
              review: "Best trip experience! Smooth booking and great spots.",
              img: "/images/user1.jpg",
            },
            {
              name: "Priya",
              review: "Loved the Kerala package! Worth every penny.",
              img: "/images/user2.jpg",
            },
            {
              name: "Rahul",
              review: "Professional team and great coordination.",
              img: "/images/user3.jpg",
            },
          ].map((rev) => (
            <div
              key={rev.name}
              className="bg-white p-6 rounded-xl shadow-md text-center"
            >
              <img
                src={rev.img}
                alt={rev.name}
                className="w-14 h-14 sm:w-16 sm:h-16 rounded-full mx-auto mb-4 object-cover"
              />
              <p className="italic text-gray-600 mb-2">"{rev.review}"</p>
              <h4 className="font-semibold text-gray-800">{rev.name}</h4>
            </div>
          ))}
        </div>
      </section>

      {/* ===== About Us ===== */}
      <section className="py-8 px-4 sm:px-6 bg-white mb-12">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6 text-gray-800">
          About Us
        </h2>
        <p className="text-center max-w-3xl mx-auto mb-8 text-gray-600">
          Amigos Tourism is a passionate travel agency dedicated to curating
          memorable journeys for students and young explorers.
        </p>

        <div className="flex flex-wrap justify-center gap-6">
          {[
            { name: "Jathin M", role: "Founder", img: "/images/team1.jpg" },
            { name: "Sneha R", role: "Travel Manager", img: "/images/team2.jpg" },
            { name: "Vikram S", role: "Tour Coordinator", img: "/images/team3.jpg" },
          ].map((member) => (
            <div
              key={member.name}
              className="bg-gray-50 p-4 sm:p-6 rounded-lg text-center shadow-md w-full sm:w-60 hover:shadow-lg"
            >
              <img
                src={member.img}
                alt={member.name}
                className="w-20 h-20 rounded-full mx-auto mb-4 object-cover"
              />
              <h4 className="text-lg font-semibold">{member.name}</h4>
              <p className="text-gray-500">{member.role}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
