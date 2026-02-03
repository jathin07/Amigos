import React, { useState } from "react";
import PackageCard from "../components/PackageCard";
import { Link } from "react-router-dom";

export const featuredPackages = [
  {
    id: 1,
    name: "Dandeli & Gokarna Combo",
    description: "Beach trekking in Gokarna and river rafting in Dandeli. Includes DJ night!",
    price: "₹4,800",
    image: "/images/places/dandeli.jpg",
    state: "Karnataka",
    tags: ["Water Sports", "Trekking", "DJ Night"],
    highlights: [
      "Rain Dance with DJ Music",
      "3 Water activities (Kayaking, Boating, Zorbing)",
      "5km Gokarna Beach Trekking",
      "Night Fire Camp with Music"
    ]
  },
  {
    id: 2,
    name: "Vagamon & Kochi Explorer",
    description: "Jeep Safari in Vagamon hills and a day of thrills at Wonderla Kochi.",
    price: "₹7,000",
    image: "/images/places/vagamon.jpg",
    state: "Kerala",
    tags: ["Jeep Safari", "Theme Park", "Hill Stay"],
    highlights: [
      "Full-day Wonderla Amusement Park entry",
      "4x4 Jeep Safari to Thavalappara & Kottamala view points",
      "Pine Forest & Thangalpara sightseeing",
      "Fort Kochi & Marine Drive exploration"
    ]
  },
  {
    id: 3,
    name: "Coorg & Chikmagalur IV",
    description: "The ultimate industrial visit covering Coffee Museums and Golden Temple.",
    price: "₹4,800",
    image: "/images/places/coorg.jpg",
    state: "Karnataka",
    tags: ["Industrial Visit", "Nature", "Temple"],
    highlights: [
      "Industrial Visit: World Coffee Museum",
      "Golden Temple (Namdroling Monastery) visit",
      "Mullayana Giri Peak & Z Point View",
      "Industrial Visit: Tasty Food Industry"
    ]
  },
  {
    id: 4,
    name: "Wayanad Wild Explorer",
    description: "Deep forest Jeep Safari, Bamboo Rafting, and an Industrial Visit to tea plants.",
    price: "₹4,800",
    image: "/images/places/wayanad.jpg",
    state: "Kerala",
    tags: ["Jeep Safari", "Bamboo Rafting", "IV Visit"],
    highlights: [
      "Industrial Visit: Kannan Devan Tea Manufacturing",
      "Munnar Top Station & Kundale Lake",
      "Mattupetty Dam & Echo Point",
      "Traditional Houseboat / Day Cruise (Optional)"
    ]
  },
  {
    id: 5,
    name: "Coorg & Bangalore Escape",
    description: "Nature walks in Bamboo forests, Golden Temple visits, and a day at Wonderla.",
    price: "₹4,600",
    image: "/images/places/coorg_hills.jpg",
    state: "Karnataka",
    tags: ["Nature", "Theme Park", "Shopping"],
    highlights: [
      "Full-day entry to Wonderla Amusement Park",
      "Nisargadhama Bamboo Forest nature walk",
      "Explore Madikeri Fort & Raja's Seat sunset",
      "Shopping at Lulu Mall & Bangalore markets"
    ]
  },
  {
    id: 6,
    name: "Munnar & Alleppey Combo",
    description: "Tea industry insights in the hills followed by a serene backwater day cruise.",
    price: "₹4,800",
    image: "/images/places/alleppey.jpg",
    state: "Kerala",
    tags: ["Industrial Visit", "Backwaters", "Hills"],
    highlights: [
      "Industrial Visit: State Coir Corporation Ltd",
      "Alleppey Day Cruise (2.5 Hours Boat Ride)",
      "Kannan Devan Tea Production Industry Visit",
      "Overnight stay in Munnar with Campfire"
    ]
  },
  {
    id: 7,
    name: "Kochi Cultural IV",
    description: "Deep dive into tech industries and coastal heritage at Fort Kochi.",
    price: "₹4,800",
    image: "/images/places/kochi_beach.jpg",
    state: "Kerala",
    tags: ["Tech Visit", "Heritage", "Lulu Mall"],
    highlights: [
      "Industrial Visit: Iroid Technologies Industry",
      "Fort Kochi & Marine Drive sightseeing",
      "Premium shopping experience at Lulu Mall",
      "Night train transit with packed dinner provided"
    ]
  }
];

const PackageList = () => {
  const [expandedId, setExpandedId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");

  const toggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const filters = ["All", "Kerala", "Karnataka", "Tamil Nadu"];

  const filteredPackages = featuredPackages.filter((pkg) => {
    // Search logic (check name or tags)
    const matchesSearch = pkg.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pkg.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

    // Filter logic
    const matchesFilter = activeFilter === "All" || pkg.state === activeFilter;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="bg-gray-50 min-h-screen">

      {/* Header Section */}
      <div className="relative bg-gradient-to-r from-blue-900 to-blue-700 pt-32 pb-24 px-6 text-center text-white overflow-hidden">
        {/* Abstract Background pattern */}
        <div className="absolute inset-0 opacity-10"
          style={{ backgroundImage: 'radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 20%, white 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 tracking-tight">
            Discover Your Next <span className="text-blue-300">Adventure</span>
          </h1>
          <p className="text-lg md:text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
            Explore our curated student packages across South India's most scenic destinations.
          </p>

          {/* Search Bar */}
          <div className="relative max-w-xl mx-auto mb-12 group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search destinations (e.g., 'Munnar', 'Trekking')..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-6 py-4 rounded-full bg-white text-gray-900 shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-500/30 transition-shadow placeholder-gray-400 font-medium"
            />
          </div>

          {/* Pill Navigation */}
          <div className="flex flex-wrap justify-center gap-3 animate-fade-in-up">
            {filters.map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`px-6 py-2 rounded-full text-sm font-semibold transition-all duration-300 ${activeFilter === filter
                  ? "bg-white text-blue-700 shadow-lg scale-105"
                  : "bg-blue-800/50 text-blue-100 hover:bg-blue-700 border border-blue-400/30 backdrop-blur-sm"
                  }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Packages Grid */}
      <div className="max-w-7xl mx-auto px-6 -mt-12 pb-20 relative z-20">
        {filteredPackages.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10">
            {filteredPackages.map((pkg) => (
              <div
                key={pkg.id}
                className={`transition-all duration-500 ${filteredPackages.length % 3 !== 0 && expandedId === pkg.id
                  ? "md:col-span-2 lg:col-span-2"
                  : ""}`}
              >
                <PackageCard
                  packageData={pkg}
                  mode="expandable"
                  expanded={expandedId === pkg.id}
                  onToggle={() => toggleExpand(pkg.id)}
                />
              </div>
            ))}
          </div>
        ) : (
          /* Empty State */
          <div className="bg-white rounded-3xl shadow-xl p-12 text-center max-w-2xl mx-auto mt-8">
            <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">🗺️</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">No packages found</h3>
            <p className="text-gray-500 mb-8">
              We couldn't find any trips matching "{searchTerm}" in {activeFilter}.
              Looking for something specific?
            </p>
            <button className="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-blue-700 transition shadow-lg hover:shadow-blue-500/30">
              Request Custom Trip
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PackageList;