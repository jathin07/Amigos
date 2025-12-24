import React from "react";
import { useParams, Link } from "react-router-dom";

const PackageDetail = () => {
  const { id } = useParams();

  const packages = [
    {
      id: 1,
      title: "Goa Beach Trip",
      description: "3 days and 2 nights of sun, sand, and surf in Goa.",
      price: "₹9,999",
      image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
      highlights: [
        "Beachside resort stay",
        "Water sports & sightseeing",
        "Evening cruise and party",
      ],
    },
    {
      id: 2,
      title: "Ooty Hill Adventure",
      description: "4 days of chill weather, nature walks, and mountain views.",
      price: "₹12,499",
      image: "https://images.unsplash.com/photo-1600633306740-7e3c3b4b42c4",
      highlights: [
        "Stay in premium cottages",
        "Botanical garden visit",
        "Tea factory tour",
      ],
    },
    {
      id: 3,
      title: "Jaipur Heritage Tour",
      description: "Explore royal palaces and vibrant culture of Jaipur.",
      price: "₹8,999",
      image: "https://images.unsplash.com/photo-1604503468506-84f5e5b0e28a",
      highlights: [
        "Amber Fort & City Palace visit",
        "Shopping at Johari Bazaar",
        "Traditional Rajasthani dinner",
      ],
    },
  ];

  const pkg = packages.find((p) => p.id === parseInt(id));

  if (!pkg) {
    return (
      <div className="text-center mt-10 text-red-600 text-xl font-semibold">
        Package not found!
      </div>
    );
  }

  return (
    <div className="bg-gray-50 min-h-screen py-8 px-6">
      <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-2xl overflow-hidden">
        <img
          src={pkg.image}
          alt={pkg.title}
          className="w-full h-80 object-cover"
        />
        <div className="p-6">
          <h1 className="text-3xl font-bold text-gray-800">{pkg.title}</h1>
          <p className="text-gray-600 mt-3">{pkg.description}</p>

          <h2 className="text-xl font-semibold text-gray-800 mt-6">
            Highlights
          </h2>
          <ul className="list-disc pl-5 text-gray-700 mt-2 space-y-1">
            {pkg.highlights.map((point, index) => (
              <li key={index}>{point}</li>
            ))}
          </ul>

          <p className="text-indigo-600 font-bold text-2xl mt-6">
            {pkg.price}
          </p>

          <button className="mt-6 bg-indigo-600 text-white py-2 px-6 rounded-xl hover:bg-indigo-700 transition">
            Book Now
          </button>

          <div className="mt-4">
            <Link to="/packages" className="text-indigo-600 hover:underline">
              ← Back to Packages
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PackageDetail;
