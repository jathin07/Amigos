import { Link } from "react-router-dom";
import PackageCard from "../components/PackageCard";
import "./Home.css";
import { placesByState } from "../data/PlacesData";
import { useParallax } from "../hooks/useParallax";
import { useRef, useState, useEffect } from "react";
import PlacesCarousel from "../components/PlacesCarousel";
import { featuredPackages } from "./PackagesList";

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
    { id: 1, type: "video", src: "/videos/trip1.mp4" },
    { id: 2, type: "image", src: "/images/customers/c1.jpg" },
    { id: 3, type: "image", src: "/images/customers/c2.jpg" },
    { id: 4, type: "video", src: "/videos/trip2.mp4" },
  ];

  const row1Ref = useRef(null);
  const row2Ref = useRef(null);
  useParallax(row1Ref, 0.15);
  useParallax(row2Ref, 0.3);

  // Duplicate images for smoother seamless scrolling
  const baseImages = ["Trip1", "Trip2", "Trip3", "Trip4"];
  const images = [...baseImages, ...baseImages, ...baseImages];

  const [activeState, setActiveState] = useState("Tamil Nadu");
  const [expandedId, setExpandedId] = useState(null);

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
      <section className="bg-gray-50 py-16 -mx-2 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8">
        <FadeIn>
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">Our Journey</h2>
            <p className="text-gray-500 mt-2">Moments we've cherished forever.</p>
          </div>

          <div className="flex overflow-x-auto space-x-6 pb-6 scrollbar-hide px-4">
            {journeyMedia.map((item) => (
              <div key={item.id} className="min-w-[280px] sm:min-w-[360px] relative group cursor-pointer">
                <div className="relative overflow-hidden rounded-2xl shadow-lg aspect-video bg-gray-200">
                  {item.type === "video" ? (
                    <>
                      <video
                        src={item.src}
                        controls
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none bg-black/20 group-hover:bg-black/10 transition-colors">
                        <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/40 shadow-xl group-hover:scale-110 transition-transform">
                          <svg className="w-5 h-5 text-white fill-current" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        </div>
                      </div>
                    </>
                  ) : (
                    <img
                      src={item.src}
                      alt="journey"
                      className="w-full h-full object-cover hover:scale-110 transition-transform duration-700 ease-in-out"
                    />
                  )}
                </div>
              </div>
            ))}
          </div>
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
      <section className="px-2 mb-16">
        <FadeIn>
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Meet the Team</h2>
            <p className="text-center max-w-2xl mx-auto text-gray-600">
              Amigos Tourism is a passionate travel agency dedicated to curating
              memorable journeys for students and young explorers.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-8">
            {[
              { name: "Jathin M", role: "Founder", img: "/images/team/team1.jpg" },
              { name: "Anthony Paul", role: "Travel Manager", img: "/images/team/team2.jpg" },
              { name: "Sanjay", role: "Tour Coordinator", img: "/images/team/team3.jpg" },
              { name: "Yabesh", role: "Tour Coordinator", img: "/images/team/team4.jpg" },
            ].map((member, idx) => (
              <FadeIn key={member.name} delay={idx * 100}>
                <div
                  className="group relative bg-white p-6 rounded-2xl text-center shadow-[0_4px_20px_rgba(0,0,0,0.06)] w-full sm:w-72 hover:-translate-y-2 hover:shadow-2xl transition-all duration-300 overflow-hidden"
                >
                  <div className="absolute top-0 left-0 w-full h-24 bg-gradient-to-r from-blue-500 to-cyan-400 opacity-10"></div>

                  <div className="relative mb-4 inline-block">
                    <img
                      src={member.img}
                      alt={member.name}
                      className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>

                  <h4 className="text-xl font-bold text-gray-800">{member.name}</h4>
                  <p className="text-blue-500 font-medium mb-4">{member.role}</p>

                  {/* Social Icons (Fade in on hover) */}
                  <div className="flex justify-center gap-3 opacity-0 translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300">
                    {['twitter', 'linkedin', 'instagram'].map(icon => (
                      <span key={icon} className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded-full hover:bg-blue-600 hover:text-white transition-colors cursor-pointer text-gray-500 text-xs">
                        {/* Simple placeholder for icon */}
                        •
                      </span>
                    ))}
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
