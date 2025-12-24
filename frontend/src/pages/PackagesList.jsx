import React from "react";
import PackageCard from "../components/PackageCard";

const PackageList = () => {
  const packages = [
    {
      id: 1,
      title: "Goa Beach Trip",
      description: "3 days and 2 nights of sun, sand, and surf.",
      price: "₹9,999",
      image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
    },
    {
      id: 2,
      title: "Ooty Hill Adventure",
      description: "Enjoy the chill and greenery of Ooty for 4 days.",
      price: "₹12,499",
      image: "https://images.unsplash.com/photo-1600633306740-7e3c3b4b42c4",
    },
    {
      id: 3,
      title: "Jaipur Heritage Tour",
      description: "Experience the pink city and royal palaces.",
      price: "₹8,999",
      image: "https://images.unsplash.com/photo-1604503468506-84f5e5b0e28a",
    },
  ];

  return (
    <div className="bg-gray-50 min-h-screen p-6">
      <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
        Available Packages
      </h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {packages.map((pkg) => (
          <PackageCard key={pkg.id} pkg={pkg} />
        ))}
      </div>
    </div>
  );
};

export default PackageList;
