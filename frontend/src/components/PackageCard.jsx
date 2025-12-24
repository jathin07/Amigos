import { Link } from "react-router-dom";

const PackageCard = ({ packageData }) => {
  return (
    <div className="bg-white shadow-lg rounded-xl overflow-hidden hover:scale-105 transition-transform duration-300">
      <img src={packageData.image} alt={packageData.name} className="h-48 w-full object-cover" />
      <div className="p-4">
        <h3 className="text-lg font-bold text-gray-800">{packageData.name}</h3>
        <p className="text-gray-600 text-sm mb-3">{packageData.description}</p>
        <Link
          to={`/packages/${packageData.id}`}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          View Details
        </Link>
      </div>
    </div>
  );
};

export default PackageCard;
