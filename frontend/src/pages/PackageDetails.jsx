import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { apiFetch } from '../config/api';
import { featuredPackages } from './PackagesList';

// Smart Destination Experience Imports
import { DestinationThemeProvider } from '../components/smart/DestinationThemeProvider';
import { SmartHeroBackground } from '../components/smart/SmartHeroBackground';
import { WeatherWidget } from '../components/smart/WeatherWidget';
import { DestinationMoodCard } from '../components/smart/DestinationMoodCard';
import { TravelRecommendationCard } from '../components/smart/TravelRecommendationCard';

const extractDestination = (title) => {
  if (!title) return 'default';
  const lowercaseTitle = title.toLowerCase();
  const destinations = [
    'munnar', 'ooty', 'coorg', 'pondicherry', 'gokarna', 'wayanad', 
    'kodaikanal', 'valparai', 'dandeli', 'chikmagalur', 'murudeshwar', 
    'alleppey', 'idukki', 'kollukumalai', 'athirappilly'
  ];
  for (const dest of destinations) {
    if (lowercaseTitle.includes(dest)) {
      return dest;
    }
  }
  return 'default';
};

const PackageDetail = () => {
  const { id } = useParams();
  const numericId = Number(id);
  const [pkg, setPkg] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPackage = async () => {
      setLoading(true);

      try {
        const item = await apiFetch(`/itineraries/${numericId}`);

        setPkg({
          id: item.id,
          title: item.title,
          description: item.short_description,
          price: item.price_per_person ? `INR ${Number(item.price_per_person).toLocaleString('en-IN')}` : 'Price on request',
          image: item.thumbnail_url || '/images/places/munnar.jpg',
          highlights: item.mini_itinerary
            ? item.mini_itinerary.split('\n').map((point) => point.replace(/^[-*]\s*/, '').trim()).filter(Boolean)
            : ['Contact us for full itinerary details'],
        });
      } catch {
        const fallback = featuredPackages.find((row) => row.id === numericId);
        if (fallback) {
          setPkg({
            id: fallback.id,
            title: fallback.name,
            description: fallback.description,
            price: fallback.price,
            image: fallback.image,
            highlights: fallback.highlights || [],
          });
        } else {
          setPkg(null);
        }
      } finally {
        setLoading(false);
      }
    };

    if (Number.isFinite(numericId)) {
      loadPackage();
    } else {
      setLoading(false);
      setPkg(null);
    }
  }, [numericId]);

  if (loading) {
    return <div className="text-center mt-10 text-gray-600 text-xl font-semibold">Loading package...</div>;
  }

  if (!pkg) {
    return <div className="text-center mt-10 text-red-600 text-xl font-semibold">Package not found!</div>;
  }

  const destinationName = extractDestination(pkg.title);

  return (
    <DestinationThemeProvider destinationName={destinationName}>
      <div className="bg-gray-50 min-h-screen py-8 px-6">
        <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-2xl overflow-hidden">
          {/* Overlaid Hero Image */}
          <div className="relative w-full h-80 overflow-hidden">
            <img src={pkg.image} alt={pkg.title} className="w-full h-full object-cover" />
            <SmartHeroBackground />
          </div>

          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-800">{pkg.title}</h1>
            <p className="text-gray-600 mt-3">{pkg.description}</p>

            {/* Smart Destination Experience Section */}
            <div className="mt-10 border-t border-slate-100 pt-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-6">
                <div>
                  <h2 className="text-xl font-black text-slate-800 tracking-tight flex items-center gap-2">
                    Live Destination Insights
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                  </h2>
                  <p className="text-slate-400 text-xs font-semibold mt-0.5">
                    Real-time weather diagnostics and tailored travel recommendations.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <WeatherWidget />
                <DestinationMoodCard />
                <TravelRecommendationCard />
              </div>
            </div>

            <h2 className="text-xl font-semibold text-gray-800 mt-8">Highlights</h2>
            <ul className="list-disc pl-5 text-gray-700 mt-2 space-y-1">
              {pkg.highlights.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>

            <p className="text-indigo-600 font-bold text-2xl mt-6">{pkg.price}</p>

            <Link to="/plan-trip" className="inline-block mt-6 bg-indigo-600 text-white py-2 px-6 rounded-xl hover:bg-indigo-700 transition">
              Book Now
            </Link>

            <div className="mt-4">
              <Link to="/packages" className="text-indigo-600 hover:underline">
                Back to Packages
              </Link>
            </div>
          </div>
        </div>
      </div>
    </DestinationThemeProvider>
  );
};

export default PackageDetail;
