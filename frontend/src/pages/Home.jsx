import { Link } from "react-router-dom";
import PackageCard from "../components/PackageCard";
import "./Home.css";
import { placesByState as fallbackPlaces } from "../data/PlacesData";
import { useParallax } from "../hooks/useParallax";
import { apiFetch } from "../config/api";
import { useRef, useState, useEffect } from "react";
import PlacesCarousel from "../components/PlacesCarousel";
import { featuredPackages } from "./PackagesList";
import PolaroidGallery from "../components/PolaroidGallery";
/**
 * FadeIn Component
 * key-concept: uses IntersectionObserver to trigger a fade-up animation
 */
const FadeIn = ({ children, delay = 0, className = "" }) => {
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`transition-all duration-1000 ease-out transform ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
        } ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
};

const Home = () => {
  // Featured packages


  // Our Journey (videos & photos)
  const journeyMedia = [
  
    { id: 1, type: "image", src: "/images/customers/c1.jpg" },
    { id: 2, type: "image", src: "/images/customers/c2.jpg" },
    { id: 3, type: "image", src: "/images/customers/c3.jpg" },
    { id: 4, type: "image", src: "/images/customers/c4.jpg" },
    { id: 5, type: "image", src: "/images/customers/c5.jpg" },
    { id: 6, type: "image", src: "/images/customers/c6.jpg" },
    { id: 7, type: "image", src: "/images/customers/c7.jpg" },
    { id: 8, type: "image", src: "/images/customers/c8.jpg" },
    { id: 9, type: "image", src: "/images/customers/c9.jpg" },
    { id: 10, type: "image", src: "/images/customers/c10.jpg" },
   
  ];

  const row1Ref = useRef(null);
  const row2Ref = useRef(null);
  useParallax(row1Ref, 0.15);
  useParallax(row2Ref, 0.3);

  // Duplicate images for smoother seamless scrolling
  const baseImages = ["Trip1", "Trip2", "Trip3", "Trip4"];
  const images = [...baseImages, ...baseImages, ...baseImages];

  const [placesByState, setPlacesByState] = useState(fallbackPlaces || []);
  const [activeState, setActiveState] = useState("Tamil Nadu");
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    async function loadDestinations() {
      try {
        const data = await apiFetch("/destinations");

        if (Array.isArray(data)) {
          if (data.length > 0) {
            setPlacesByState(data);

            // set first state as active if not already set or if current state is not in the data
            const hasActiveState = data.some(d => d.state === activeState);
            if (!activeState || !hasActiveState) {
              setActiveState(data[0].state);
            }
          }
        }
      } catch (error) {
        console.error("Failed to load destinations:", error);
      }
    }

    loadDestinations();
  }, []);
  const toggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  {/* Put this array above your Home component function or at the top of the file */ }
  const reviews = [
    {
      name: "Aditya Verma",
      college: "SRM University (KTR)",
      review: "The Munnar-Thekkady trip was insane! The luxury semi-sleeper bus made the night journey so comfortable. Special shoutout to our coordinator—he felt like one of us. 10/10 for the campfire night!",
      rating: 5,
      tags: ["Bus Travel", "Munnar"],
      color: "blue" // SRM Blue
    },
    {
      name: "Sneha Reddy",
      college: "Loyola College",
      review: "Properly organized Kerala backwaters trip. The houseboat stay was the highlight! As a group of girls, we felt very safe throughout. The food was authentic and hot every single day.",
      rating: 5,
      tags: ["Safety", "Food"],
      color: "red" // Loyola Maroonish/Red
    },
    {
      name: "Rohan Das",
      college: "Jain University",
      review: "Goa vibes were unmatched! Usually, college trips have bad hotel food, but here the stay was premium and the buffet was actually good. The itinerary wasn't rushed at all.",
      rating: 4,
      tags: ["Stay", "Goa"],
      color: "yellow" // Jain Gold/Yellow
    },
    {
      name: "Vikram",
      college: "MGR University",
      review: "Kodaikanal trip was 💯. The bus driver was experienced and the tour coordinator managed the 50+ crowd without any chaos. The sightseeing spots were exactly as promised.",
      rating: 5,
      tags: ["Coordinator", "Kodai"],
      color: "purple" // MGR
    },
    {
      name: "Pooja Krishnan",
      college: "Vels University",
      review: "Best budget smart tour! We visited Ooty and the rooms were way better than what other agencies provide for students. Clean bathrooms and great view from the balcony!",
      rating: 5,
      tags: ["Accommodation", "Ooty"],
      color: "cyan" // Vels
    }
  ];

  // Helper dictionary to map color names to Tailwind classes dynamically
  const colorMap = {
    blue: "bg-blue-50 text-blue-600 group-hover:bg-blue-100",
    red: "bg-red-50 text-red-600 group-hover:bg-red-100",
    yellow: "bg-yellow-50 text-yellow-700 group-hover:bg-yellow-100",
    purple: "bg-purple-50 text-purple-600 group-hover:bg-purple-100",
    cyan: "bg-cyan-50 text-cyan-700 group-hover:bg-cyan-100",
  };

  const iconColorMap = {
    blue: "group-hover:text-blue-100",
    red: "group-hover:text-red-100",
    yellow: "group-hover:text-yellow-100",
    purple: "group-hover:text-purple-100",
    cyan: "group-hover:text-cyan-100",
  };

  return (
    <div className="w-full max-w-[100vw] overflow-x-hidden px-2 sm:px-6 lg:px-8 bg-white space-y-24 pb-20">

      {/* ===== Parallax Hero Section ===== */}
      <section className="relative w-full min-h-[60vh] sm:min-h-[70vh] md:min-h-[85vh] overflow-hidden rounded-2xl sm:rounded-3xl mt-6 shadow-2xl">

        {/* Row 1 - slower parallax */}
        <div
          ref={row1Ref}
          className="absolute inset-0 opacity-80 overflow-hidden hidden sm:block"
        >
          <div className="scroll-row animate-scroll-left h-full flex w-[200%]">
            {images.map((img, i) => (
              <img
                key={i}
                src={`/images/trip/${img}.jpg`}
                className="h-full object-cover mx-2 rounded-lg min-w-[280px] sm:min-w-[340px] md:min-w-[400px] shadow-lg"
                alt="trip"
              />
            ))}
          </div>
        </div>

        {/* Row 2 - moves faster */}
        <div
          ref={row2Ref}
          className="absolute inset-0 opacity-70 overflow-hidden hidden sm:block pointer-events-none"
        >
          <div className="scroll-row animate-scroll-right h-full flex w-[200%]">
            {images.map((img, i) => (
              <img
                key={i + "row2"}
                src={`/images/trip/${img}.jpg`}
                className="h-full object-cover mx-2 rounded-lg min-w-[280px] sm:min-w-[340px] md:min-w-[400px] shadow-lg"
                alt="trip"
              />
            ))}
          </div>
        </div>

        {/* Fallback single background image on small screens */}
        <div
          className="absolute inset-0 bg-cover bg-center sm:hidden transition-transform duration-1000 hover:scale-105"
          style={{ backgroundImage: "url('/images/trip/Trip1.jpg')" }}
          aria-hidden="true"
        />

        {/* Gradient Overlay (subtle bottom-to-top) */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent"></div>

        {/* Hero Content */}
        <div className="relative z-10 flex flex-col items-center justify-center text-center h-full text-white px-4">
          <div className="overflow-hidden mb-4">
            <h1 className="text-3xl sm:text-5xl md:text-7xl font-extrabold leading-tight animate-fade-in-up drop-shadow-lg">
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-100 to-white">
                Discover. Travel. Live.
              </span>
            </h1>
          </div>

          <p className="text-base sm:text-lg md:text-xl mb-8 max-w-lg sm:max-w-2xl text-gray-200 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            Student-friendly & budget smart tours — curated with love and adventure in mind.
          </p>

          <Link
            to="/plan-trip"
            className="group relative px-8 py-3 rounded-full text-base sm:text-lg font-semibold text-white overflow-hidden transition-all duration-300 transform hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(255,255,255,0.4)] opacity-0 animate-fade-in-up"
            style={{ animationDelay: '0.6s' }}
          >
            {/* Glassmorphism Effect */}
            <div className="absolute inset-0 bg-white/10 backdrop-blur-md border border-white/30 rounded-full transition-all duration-300 group-hover:bg-white/20"></div>
            <span className="relative z-10 flex items-center gap-2">
              Plan My Trip
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </span>
          </Link>
        </div>
      </section>

      {/* ===== Who We Are ===== */}
      <section className="px-4 py-16 bg-gradient-to-br from-blue-50/40 via-transparent to-cyan-50/20 rounded-3xl border border-gray-100/50">
        <FadeIn>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left side description */}
            <div className="lg:col-span-5 space-y-6">
              <span className="inline-block text-xs font-bold tracking-widest text-blue-600 uppercase bg-blue-50 px-4 py-1.5 rounded-full">
                Who We Are
              </span>
              <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-gray-900 leading-tight">
                A <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">Young Team</span> mapping your next big adventure.
              </h2>
              <p className="text-gray-600 text-lg leading-relaxed">
                At Amigos Tourism, we are passionate young travelers who design budget-friendly, high-energy, and completely safe journeys across India. We plan every detail so you can focus on building lifelong memories.
              </p>
              <div className="flex flex-wrap gap-4 pt-2">
                <div className="flex items-center gap-2 text-gray-700 bg-white shadow-sm border border-gray-100 px-4 py-2.5 rounded-2xl">
                  <span className="text-blue-500 text-xl">🇮🇳</span>
                  <span className="font-semibold text-sm">Trips Across India</span>
                </div>
                <div className="flex items-center gap-2 text-gray-700 bg-white shadow-sm border border-gray-100 px-4 py-2.5 rounded-2xl">
                  <span className="text-cyan-500 text-xl">🤝</span>
                  <span className="font-semibold text-sm">Expert Trip Planners</span>
                </div>
              </div>
            </div>

            {/* Right side stats grid */}
            <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* School trips */}
              <div className="group bg-white p-8 rounded-3xl border border-gray-100 shadow-[0_10px_30px_rgba(0,0,0,0.02)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform">
                  🎒
                </div>
                <h3 className="text-4xl font-black text-gray-900 mb-1">10+</h3>
                <h4 className="font-bold text-gray-800 mb-2">School Trips</h4>
                <p className="text-gray-500 text-sm leading-relaxed">Exciting, educational, and strictly secured journeys for younger explorers.</p>
              </div>

              {/* College trips */}
              <div className="group bg-white p-8 rounded-3xl border border-gray-100 shadow-[0_10px_30px_rgba(0,0,0,0.02)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 bg-cyan-50 text-cyan-600 rounded-2xl flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform">
                  🎓
                </div>
                <h3 className="text-4xl font-black text-gray-900 mb-1">100+</h3>
                <h4 className="font-bold text-gray-800 mb-2">College Trips</h4>
                <p className="text-gray-500 text-sm leading-relaxed">High-energy, pocket-friendly, and unforgettable college getaways.</p>
              </div>

              {/* Group trips */}
              <div className="group bg-white p-8 rounded-3xl border border-gray-100 shadow-[0_10px_30px_rgba(0,0,0,0.02)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-2xl flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform">
                  🚌
                </div>
                <h3 className="text-4xl font-black text-gray-900 mb-1">50+</h3>
                <h4 className="font-bold text-gray-800 mb-2">Group Trips</h4>
                <p className="text-gray-500 text-sm leading-relaxed">Tailored packages for families, friends, corporate retreats, and spiritual trips.</p>
              </div>

              {/* Expert Planners */}
              <div className="group bg-white p-8 rounded-3xl border border-gray-100 shadow-[0_10px_30px_rgba(0,0,0,0.02)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300">
                <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform">
                  🗺️
                </div>
                <h3 className="text-4xl font-black text-gray-900 mb-1">Expert</h3>
                <h4 className="font-bold text-gray-800 mb-2">Consultation</h4>
                <p className="text-gray-500 text-sm leading-relaxed">Personalized travel planning to craft custom, stress-free itineraries.</p>
              </div>
            </div>
          </div>
        </FadeIn>
      </section>

      {/* ===== What We Provide ===== */}
      <section className="px-4 py-16 bg-gray-50/50 rounded-3xl border border-gray-100">
        <FadeIn>
          <div className="text-center mb-12">
            <span className="inline-block text-xs font-bold tracking-widest text-blue-600 uppercase bg-blue-50 px-4 py-1.5 rounded-full mb-3">
              Our Offerings
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900">What We Provide</h2>
            <div className="h-1 w-20 bg-blue-500 mx-auto rounded-full mt-4"></div>
            <p className="text-gray-500 max-w-2xl mx-auto mt-4 text-sm sm:text-base">
              We handle all the heavy lifting so you can enjoy a hassle-free, memorable trip from start to finish.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* Transport */}
            <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4 p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <div className="flex-shrink-0 w-14 h-14 sm:w-12 sm:h-12 bg-blue-50 text-blue-600 rounded-2xl sm:rounded-xl flex items-center justify-center text-2xl sm:text-2xl shadow-sm sm:shadow-none">
                🚌
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 sm:mb-1">Seamless Transport</h3>
                <p className="text-gray-500 text-sm leading-relaxed">Luxury semi-sleeper buses, pushback seating, and reliable local transit for comfortable journeys.</p>
              </div>
            </div>

            {/* Stays */}
            <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4 p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <div className="flex-shrink-0 w-14 h-14 sm:w-12 sm:h-12 bg-cyan-50 text-cyan-600 rounded-2xl sm:rounded-xl flex items-center justify-center text-2xl sm:text-2xl shadow-sm sm:shadow-none">
                🏨
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 sm:mb-1">Premium Stays</h3>
                <p className="text-gray-500 text-sm leading-relaxed">Handpicked hotels, cozy homestays, dynamic camps, and scenic houseboats with top-tier safety.</p>
              </div>
            </div>

            {/* Food */}
            <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4 p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <div className="flex-shrink-0 w-14 h-14 sm:w-12 sm:h-12 bg-emerald-50 text-emerald-600 rounded-2xl sm:rounded-xl flex items-center justify-center text-2xl sm:text-2xl shadow-sm sm:shadow-none">
                🍔
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 sm:mb-1">Hygienic Meals</h3>
                <p className="text-gray-500 text-sm leading-relaxed">Delicious and authentic local buffet spreads with pure veg and non-veg options served hot.</p>
              </div>
            </div>

            {/* Coordinators */}
            <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4 p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <div className="flex-shrink-0 w-14 h-14 sm:w-12 sm:h-12 bg-indigo-50 text-indigo-600 rounded-2xl sm:rounded-xl flex items-center justify-center text-2xl sm:text-2xl shadow-sm sm:shadow-none">
                🙋🏽‍♂️
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 sm:mb-1">Trip Coordinators</h3>
                <p className="text-gray-500 text-sm leading-relaxed">Friendly travel captains who feel like family, organizing logistics and ensuring safety.</p>
              </div>
            </div>

            {/* DJ & Campfire */}
            <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4 p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <div className="flex-shrink-0 w-14 h-14 sm:w-12 sm:h-12 bg-purple-50 text-purple-600 rounded-2xl sm:rounded-xl flex items-center justify-center text-2xl sm:text-2xl shadow-sm sm:shadow-none">
                🔥
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 sm:mb-1">Campfire & DJ Nights</h3>
                <p className="text-gray-500 text-sm leading-relaxed">Unwind with lively music, high-energy DJ nights, and cozy campfires under the stars.</p>
              </div>
            </div>

            {/* Custom Planning */}
            <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-4 p-6 bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow duration-300">
              <div className="flex-shrink-0 w-14 h-14 sm:w-12 sm:h-12 bg-rose-50 text-rose-600 rounded-2xl sm:rounded-xl flex items-center justify-center text-2xl sm:text-2xl shadow-sm sm:shadow-none">
                ✨
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2 sm:mb-1">Custom Activities</h3>
                <p className="text-gray-500 text-sm leading-relaxed">Tailored itineraries including adventure sports, guided sightseeing, and pre-booked entry tickets.</p>
              </div>
            </div>
          </div>
        </FadeIn>
      </section>

      {/* ===== Places We Cover (Pill Nav) ===== */}
      <section className="relative px-2">
        <FadeIn>
          <div className="text-center mb-10">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Top Destinations</h2>
            <div className="h-1 w-20 bg-blue-500 mx-auto rounded-full"></div>
          </div>

          <div className="flex justify-center mb-12">
            <div className="flex gap-4 overflow-x-auto py-4 px-4 scrollbar-hide sm:flex-wrap sm:justify-center">
              {placesByState.map((group) => (
                <button
                  key={group.state}
                  onClick={() => setActiveState(group.state)}
                  className={`relative px-6 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 ease-out whitespace-nowrap
                  ${activeState === group.state
                      ? "text-white shadow-[0_0_15px_rgba(37,99,235,0.5)] bg-blue-600 scale-105"
                      : "text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900"
                    }`}
                >
                  {group.state}
                  {/* Active Underline (Glow) */}
                  {activeState === group.state && (
                    <span className="absolute bottom-1 left-1/2 transform -translate-x-1/2 w-1/3 h-0.5 bg-blue-300/50 rounded-full blur-[1px]"></span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {placesByState
            .filter((group) => group.state === activeState)
            .map((group) => (
              <div key={group.state} className="animate-fade-in-up">
                <PlacesCarousel stateGroup={group} />
              </div>
            ))}
        </FadeIn>
      </section>

      {/* ===== Featured Packages ===== */}
      <section className="px-2">
        <FadeIn>
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Featured Packages</h2>
            <p className="text-gray-500 max-w-2xl mx-auto">Handpicked experiences for the best memories.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 sm:gap-10">
            {featuredPackages.slice(0, 6).map((pkg, idx) => (
              <FadeIn key={pkg.id} delay={idx * 100}>
                <div className="hover:scale-[1.02] transition-transform duration-500">
                  <PackageCard
                    packageData={pkg}
                    mode="expandable"
                    expanded={expandedId === pkg.id}
                    onToggle={() => toggleExpand(pkg.id)}
                  />
                </div>
              </FadeIn>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/packages"
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-blue-700 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300"
            >
              Browse All Packages
            </Link>
          </div>
        </FadeIn>
      </section>

      {/* ===== Our Journey ===== */}
      <section className="bg-gray-50 py-16 -mx-2 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <FadeIn>
          <PolaroidGallery />
        </FadeIn>
      </section>


      {/* ===== Reviews Section ===== */}
      <section className="px-4 py-16 bg-gray-50/50">
        <FadeIn>
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl sm:text-5xl font-bold text-center mb-4 text-gray-900">
              What Our Travelers Say
            </h2>
            <p className="text-center text-gray-500 mb-12">Trusted by students across top universities</p>

            {/* Creative Bento-style Grid */}
            <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
              {reviews.map((rev, idx) => (
                <FadeIn
                  key={rev.name}
                  delay={idx * 100}
                  className={`${idx === 0 || idx === 3 ? 'md:col-span-3' : 'md:col-span-2'}`}
                >
                  <div className="relative bg-white/80 backdrop-blur-xl border border-white/40 p-8 rounded-3xl shadow-sm hover:shadow-[0_20px_40px_-5px_rgba(0,0,0,0.1)] transition-all duration-500 ease-out transform hover:-translate-y-3 h-full flex flex-col group">

                    {/* College Tag */}
                    <div className="flex justify-between items-start mb-6">
                      <span className={`text-[10px] font-bold tracking-widest uppercase py-1 px-3 rounded-full transition-colors ${colorMap[rev.color] || "bg-gray-100 text-gray-600"}`}>
                        {rev.college}
                      </span>
                      <div className="flex text-yellow-400 text-xs">
                        {"★".repeat(rev.rating)}
                      </div>
                    </div>

                    {/* Quote Icon (Micro-animation on hover) */}
                    <div className={`absolute top-12 right-8 text-gray-100 transition-all duration-500 group-hover:-translate-y-2 ${iconColorMap[rev.color]}`}>
                      <svg width="60" height="60" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M14.017 21L14.017 18C14.017 16.8954 14.9124 16 16.017 16H19.017C19.5693 16 20.017 15.5523 20.017 15V9C20.017 8.44772 19.5693 8 19.017 8H15.017C14.4647 8 14.017 8.44772 14.017 9V11C14.017 11.5523 13.5693 12 13.017 12H12.017V5H22.017V15C22.017 18.3137 19.3307 21 16.017 21H14.017ZM5.0166 21L5.0166 18C5.0166 16.8954 5.91203 16 7.0166 16H10.0166C10.5689 16 11.0166 15.5523 11.0166 15V9C11.0166 8.44772 10.5689 8 10.0166 8H6.0166C5.46432 8 5.0166 8.44772 5.0166 9V11C5.0166 11.5523 4.56889 12 4.0166 12H3.0166V5H13.0166V15C13.0166 18.3137 10.3303 21 7.0166 21H5.0166Z" />
                      </svg>
                    </div>

                    {/* Review Text */}
                    <p className="text-gray-700 text-lg leading-relaxed italic mb-8 relative z-10">
                      "{rev.review}"
                    </p>

                    {/* Bottom Section */}
                    <div className="mt-auto flex flex-col gap-4">
                      <div className="flex flex-wrap gap-2">
                        {rev.tags.map(tag => (
                          <span key={tag} className="text-[10px] font-medium bg-gray-100 text-gray-500 px-2 py-1 rounded">
                            #{tag}
                          </span>
                        ))}
                      </div>
                      <div className="border-t border-gray-100 pt-4">
                        <h4 className="font-bold bg-gradient-to-r from-gray-900 to-gray-500 bg-clip-text text-transparent transform transition-all duration-300 group-hover:translate-x-1">
                          — {rev.name}
                        </h4>
                      </div>
                    </div>

                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </FadeIn>
      </section>

      {/* ===== About Us (Team) ===== */}
      <section className="relative px-4 sm:px-6 py-20 bg-gradient-to-b from-white to-slate-50 border-t border-gray-100/50 overflow-hidden">
        {/* Decorative Travel Route Background */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden select-none opacity-20 hidden md:block z-0">
          <svg className="w-full h-full min-h-[500px]" viewBox="0 0 1440 600" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path 
              d="M -100 300 Q 250 150, 550 300 T 1150 300 T 1650 300" 
              stroke="url(#route-grad)" 
              strokeWidth="3" 
              strokeDasharray="8 8" 
            />
            <defs>
              <linearGradient id="route-grad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3B82F6" />
                <stop offset="100%" stopColor="#06B6D4" />
              </linearGradient>
            </defs>
            {/* Pins along the path */}
            <g transform="translate(200, 220)">
              <circle cx="0" cy="0" r="4" fill="#3B82F6" />
              <circle cx="0" cy="0" r="10" stroke="#3B82F6" strokeWidth="1.5" strokeDasharray="2 2" className="animate-spin" style={{ animationDuration: '6s' }} />
            </g>
            <g transform="translate(680, 280)">
              <circle cx="0" cy="0" r="4" fill="#06B6D4" />
              <circle cx="0" cy="0" r="10" stroke="#06B6D4" strokeWidth="1.5" strokeDasharray="2 2" className="animate-spin" style={{ animationDuration: '8s' }} />
            </g>
            <g transform="translate(1120, 275)">
              <circle cx="0" cy="0" r="4" fill="#3B82F6" />
              <circle cx="0" cy="0" r="10" stroke="#3B82F6" strokeWidth="1.5" strokeDasharray="2 2" className="animate-spin" style={{ animationDuration: '7s' }} />
            </g>
          </svg>
        </div>

        <FadeIn className="relative z-10 max-w-7xl mx-auto">
          <div className="text-center mb-6">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Meet the Team</h2>
            <p className="text-center max-w-2xl mx-auto text-gray-600">
              Amigos Tourism is a passionate travel agency dedicated to curating
              memorable journeys for students and young explorers.
            </p>
          </div>

          {/* Team Statistics Pill Counters */}
          <div className="flex flex-wrap justify-center gap-4 sm:gap-6 mb-16">
            {/* Badge 1 */}
            <div className="flex items-center gap-2.5 px-4 py-2 bg-white/90 backdrop-blur-sm border border-blue-100 rounded-full shadow-[0_2px_10px_rgba(0,0,0,0.02)] transition-all duration-300 hover:shadow-md hover:border-blue-200">
              <div className="p-1 bg-blue-50 rounded-full text-blue-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.109A9.342 9.342 0 0012.24 21c.5-.83.76-1.797.76-2.825V18c0-1.285-.378-2.485-1.026-3.49M7 10.5a3.5 3.5 0 117 0 3.5 3.5 0 01-7 0zM17.25 8.25a2.25 2.25 0 114.5 0 2.25 2.25 0 01-4.5 0zM1.5 17.5a6.002 6.002 0 0111.477-2.31 3.5 3.5 0 01-6.143-2.89 6.002 6.002 0 01-5.334 5.2z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-700">5+ Organizers</span>
            </div>
            {/* Badge 2 */}
            <div className="flex items-center gap-2.5 px-4 py-2 bg-white/90 backdrop-blur-sm border border-cyan-100 rounded-full shadow-[0_2px_10px_rgba(0,0,0,0.02)] transition-all duration-300 hover:shadow-md hover:border-cyan-200">
              <div className="p-1 bg-cyan-50 rounded-full text-cyan-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.684A1.125 1.125 0 003 6.69v11.22c0 .425.24.815.622 1.006l4.875 2.437a1.125 1.125 0 001.006 0l5.375-2.688a1.125 1.125 0 011.006 0z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-700">50+ Trips Conducted</span>
            </div>
            {/* Badge 3 */}
            <div className="flex items-center gap-2.5 px-4 py-2 bg-white/90 backdrop-blur-sm border border-indigo-100 rounded-full shadow-[0_2px_10px_rgba(0,0,0,0.02)] transition-all duration-300 hover:shadow-md hover:border-indigo-200">
              <div className="p-1 bg-indigo-50 rounded-full text-indigo-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c2.785 0 5.5-.413 8.083-1.21.217-.677.34-1.397.37-2.147m-16.193-7.4a6.038 6.038 0 000 12.015m16.193-12.015a6.038 6.038 0 010 12.015m-16.193-12.015L12 3l8.77 4.147L12 11.293l-7.74-4.146z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-gray-700">1000+ Students Traveled</span>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-8 lg:gap-10 pb-8">
            {[
              { 
                name: "Jathin M", 
                role: "Founder", 
                img: "/images/team/jathin.jpg",
                bio: "Building memorable student travel experiences with passion."
              },
              { 
                name: "Anthony Paul", 
                role: "Tour Operator", 
                img: "/images/team/anthony.jpg",
                bio: "Operations & destination planning specialist."
              },
              { 
                name: "Sanjay", 
                role: "Tour Coordinator", 
                img: "/images/team/sanjay.jpg",
                bio: "Trip coordination and customer success coordinator."
              },
              { 
                name: "Yabesh", 
                role: "Tour Coordinator", 
                img: "/images/team/yabesh.jpg",
                bio: "Media capture specialist and adventure leader."
              },
              { 
                name: "Shakeleshwaran", 
                role: "Tour Coordinator", 
                img: "/images/team/shakeleshwaran.jpg",
                bio: "Safety coordinator and trekking specialist."
              }
            ].map((member, idx) => (
              <FadeIn 
                key={member.name} 
                delay={idx * 100} 
                className={`w-full sm:w-auto flex justify-center ${idx % 2 !== 0 ? 'lg:pt-6' : ''}`}
              >
                <div
                  className={`group relative bg-white pt-28 pb-6 px-6 rounded-3xl text-center transition-all duration-500 ease-out w-full max-w-[300px] sm:max-w-none sm:w-72 flex flex-col items-center border hover:-translate-y-2
                    ${member.role === "Founder" 
                      ? 'border-blue-200 shadow-[0_12px_30px_rgba(59,130,246,0.06)] hover:shadow-[0_20px_40px_rgba(59,130,246,0.14)]' 
                      : 'border-slate-100 shadow-[0_10px_25px_rgba(0,0,0,0.03)] hover:shadow-[0_20px_35px_rgba(0,0,0,0.08)]'
                    }`}
                >
                  {/* Sky-to-blue gradient top header banner */}
                  <div className="absolute top-0 left-0 w-full h-24 bg-gradient-to-br from-sky-400 to-blue-500 overflow-hidden">
                    {/* Subtle mountain silhouette/grid pattern overlay */}
                    <svg className="absolute inset-0 w-full h-full opacity-15" viewBox="0 0 100 50" preserveAspectRatio="none" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M0 45 L20 20 L40 40 L60 15 L80 35 L100 10 L100 50 L0 50 Z" fill="white" />
                      <path d="M0 50 L10 30 L25 45 L45 25 L65 48 L85 30 L100 45 L100 50 Z" fill="white" opacity="0.5" />
                    </svg>
                  </div>

                  {/* Profile Image (130px size with overlap) */}
                  <div className="absolute top-8 left-1/2 -translate-x-1/2 z-10">
                    <div className="relative">
                      <img
                        src={member.img}
                        alt={member.name}
                        className={`w-[130px] h-[130px] rounded-full object-cover border-4 border-white shadow-md transition-transform duration-500 ease-out group-hover:scale-105
                          ${member.role === "Founder" ? 'ring-2 ring-blue-400/50' : ''}`}
                      />
                      
                      {/* Founder badge highlight */}
                      {member.role === "Founder" && (
                        <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-[10px] font-black uppercase tracking-wider px-3 py-1 rounded-full shadow-md border border-white whitespace-nowrap">
                          Founder
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Content space to push below overlapping image */}
                  <div className="h-14"></div>

                  <h4 className="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition-colors duration-300">{member.name}</h4>
                  <p className="text-blue-500 font-semibold text-xs uppercase tracking-wider mb-2.5">{member.role}</p>
                  <p className="text-gray-500 text-sm px-1 mb-4 leading-relaxed h-10 flex items-center justify-center">{member.bio}</p>

                  {/* Ticket Divider Line */}
                  <div className="w-full border-t border-dashed border-slate-100 my-3"></div>

                  {/* Social Icons (Fade and slide in on hover) */}
                  <div className="flex justify-center gap-3.5 opacity-0 translate-y-3 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 ease-out">
                    {/* LinkedIn */}
                    <a
                      href="#"
                      className="w-8.5 h-8.5 flex items-center justify-center bg-slate-50 text-slate-400 rounded-full hover:bg-blue-600 hover:text-white transition-all duration-300"
                      aria-label={`${member.name}'s LinkedIn`}
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                      </svg>
                    </a>
                    {/* Instagram */}
                    <a
                      href="#"
                      className="w-8.5 h-8.5 flex items-center justify-center bg-slate-50 text-slate-400 rounded-full hover:bg-pink-600 hover:text-white transition-all duration-300"
                      aria-label={`${member.name}'s Instagram`}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                        <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                        <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                      </svg>
                    </a>
                    {/* Email */}
                    <a
                      href="mailto:contact@amigostourism.com"
                      className="w-8.5 h-8.5 flex items-center justify-center bg-slate-50 text-slate-400 rounded-full hover:bg-cyan-600 hover:text-white transition-all duration-300"
                      aria-label={`Email ${member.name}`}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                        <polyline points="22,6 12,13 2,6"></polyline>
                      </svg>
                    </a>
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>
        </FadeIn>
      </section>
    </div>
  );
};

export default Home;
