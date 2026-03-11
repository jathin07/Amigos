import React, { useEffect, useMemo, useState } from 'react';
import PackageCard from '../components/PackageCard';
import { apiFetch } from '../config/api';

export const featuredPackages = [
  {
    id: 1,
    name: 'Dandeli & Gokarna Combo',
    description: 'Beach trekking in Gokarna and river rafting in Dandeli. Includes DJ night!',
    price: 'INR 4,800',
    image: '/images/places/dandeli.jpg',
    state: 'Karnataka',
    tags: ['Water Sports', 'Trekking', 'DJ Night'],
    highlights: [
      'Rain Dance with DJ Music',
      '3 Water activities (Kayaking, Boating, Zorbing)',
      '5km Gokarna Beach Trekking',
      'Night Fire Camp with Music'
    ]
  },
  {
    id: 2,
    name: 'Vagamon & Kochi Explorer',
    description: 'Jeep Safari in Vagamon hills and a day of thrills at Wonderla Kochi.',
    price: 'INR 7,000',
    image: '/images/places/vagamon.jpg',
    state: 'Kerala',
    tags: ['Jeep Safari', 'Theme Park', 'Hill Stay'],
    highlights: [
      'Full-day Wonderla Amusement Park entry',
      '4x4 Jeep Safari to Thavalappara & Kottamala view points',
      'Pine Forest & Thangalpara sightseeing',
      'Fort Kochi & Marine Drive exploration'
    ]
  },
  {
    id: 3,
    name: 'Coorg & Chikmagalur IV',
    description: 'The ultimate industrial visit covering Coffee Museums and Golden Temple.',
    price: 'INR 4,800',
    image: '/images/places/coorg.jpg',
    state: 'Karnataka',
    tags: ['Industrial Visit', 'Nature', 'Temple'],
    highlights: [
      'Industrial Visit: World Coffee Museum',
      'Golden Temple (Namdroling Monastery) visit',
      'Mullayana Giri Peak & Z Point View',
      'Industrial Visit: Tasty Food Industry'
    ]
  },
  {
    id: 4,
    name: 'Wayanad Wild Explorer',
    description: 'Deep forest Jeep Safari, Bamboo Rafting, and an Industrial Visit to tea plants.',
    price: 'INR 4,800',
    image: '/images/places/wayanad.jpg',
    state: 'Kerala',
    tags: ['Jeep Safari', 'Bamboo Rafting', 'IV Visit'],
    highlights: [
      'Industrial Visit: Kannan Devan Tea Manufacturing',
      'Munnar Top Station & Kundale Lake',
      'Mattupetty Dam & Echo Point',
      'Traditional Houseboat / Day Cruise (Optional)'
    ]
  },
  {
    id: 5,
    name: 'Coorg & Bangalore Escape',
    description: 'Nature walks in Bamboo forests, Golden Temple visits, and a day at Wonderla.',
    price: 'INR 4,600',
    image: '/images/places/coorg.jpg',
    state: 'Karnataka',
    tags: ['Nature', 'Theme Park', 'Shopping'],
    highlights: [
      'Full-day entry to Wonderla Amusement Park',
      'Nisargadhama Bamboo Forest nature walk',
      'Explore Madikeri Fort & Raja\'s Seat sunset',
      'Shopping at Lulu Mall & Bangalore markets'
    ]
  },
  {
    id: 6,
    name: 'Munnar & Alleppey Combo',
    description: 'Tea industry insights in the hills followed by a serene backwater day cruise.',
    price: 'INR 4,800',
    image: '/images/places/allepey.jpg',
    state: 'Kerala',
    tags: ['Industrial Visit', 'Backwaters', 'Hills'],
    highlights: [
      'Industrial Visit: State Coir Corporation Ltd',
      'Alleppey Day Cruise (2.5 Hours Boat Ride)',
      'Kannan Devan Tea Production Industry Visit',
      'Overnight stay in Munnar with Campfire'
    ]
  }
];

const normalizeApiPackage = (item) => ({
  id: item.id,
  name: item.title,
  description: item.short_description,
  price: item.price_per_person ? `INR ${Number(item.price_per_person).toLocaleString('en-IN')}` : 'Price on request',
  image: item.thumbnail_url || '/images/places/munnar.jpg',
  state: 'All',
  tags: item.inclusions ? item.inclusions.split(',').map((tag) => tag.trim()).filter(Boolean).slice(0, 3) : ['Custom'],
  highlights: item.mini_itinerary
    ? item.mini_itinerary.split('\n').map((point) => point.replace(/^[-*]\s*/, '').trim()).filter(Boolean)
    : ['Contact us for full itinerary details'],
});

const PackageList = () => {
  const [expandedId, setExpandedId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [apiPackages, setApiPackages] = useState([]);

  useEffect(() => {
    const loadPackages = async () => {
      try {
        const rows = await apiFetch('/itineraries');
        if (Array.isArray(rows) && rows.length > 0) {
          setApiPackages(rows.map(normalizeApiPackage));
        }
      } catch {
        setApiPackages([]);
      }
    };

    loadPackages();
  }, []);

  const packages = apiPackages.length > 0 ? apiPackages : featuredPackages;

  const toggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  const filters = useMemo(() => {
    const dynamicStates = [...new Set(packages.map((pkg) => pkg.state).filter(Boolean))].filter((state) => state !== 'All');
    return ['All', ...dynamicStates];
  }, [packages]);

  const filteredPackages = packages.filter((pkg) => {
    const matchesSearch =
      pkg.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pkg.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesFilter = activeFilter === 'All' || pkg.state === activeFilter;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="relative bg-gradient-to-r from-blue-900 to-blue-700 pt-32 pb-24 px-6 text-center text-white overflow-hidden">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              'radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 20%, white 1px, transparent 1px)',
            backgroundSize: '40px 40px'
          }}
        />

        <div className="relative z-10 max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-6 tracking-tight">
            Discover Your Next <span className="text-blue-300">Adventure</span>
          </h1>
          <p className="text-lg md:text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
            Explore our curated student packages across South India's most scenic destinations.
          </p>

          <div className="relative max-w-xl mx-auto mb-12 group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
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

          <div className="flex flex-wrap justify-center gap-3 animate-fade-in-up">
            {filters.map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`px-6 py-2 rounded-full text-sm font-semibold transition-all duration-300 ${
                  activeFilter === filter
                    ? 'bg-white text-blue-700 shadow-lg scale-105'
                    : 'bg-blue-800/50 text-blue-100 hover:bg-blue-700 border border-blue-400/30 backdrop-blur-sm'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 -mt-12 pb-20 relative z-20">
        {filteredPackages.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-10">
            {filteredPackages.map((pkg) => (
              <div key={pkg.id} className="transition-all duration-500">
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
          <div className="bg-white rounded-3xl shadow-xl p-12 text-center max-w-2xl mx-auto mt-8">
            <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">Map</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">No packages found</h3>
            <p className="text-gray-500 mb-8">
              We could not find any trips matching "{searchTerm}" in {activeFilter}.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PackageList;
