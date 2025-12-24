import { Link } from "react-router-dom";
import { useState } from "react";

const Navbar = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="p-4 flex justify-between items-center shadow-sm bg-white">
      {/* Logo */}
      <img
        src="/images/Amigoslogo.png"
        alt="Amigos Logo"
        className="h-10 w-auto"
      />

      {/* Desktop Menu */}
      <div className="hidden sm:flex space-x-6 text-gray-800 font-medium">
        <Link to="/" className="hover:text-blue-600">Home</Link>
        <Link to="/packages" className="hover:text-blue-600">Packages</Link>
        <Link to="/plan-trip" className="hover:text-blue-600">Plan My Trip</Link>
      </div>

      {/* Mobile Menu Button */}
      <button
        className="sm:hidden text-gray-800 text-2xl focus:outline-none"
        onClick={() => setOpen(!open)}
      >
        ☰
      </button>

      {/* Mobile Dropdown */}
      {open && (
        <div className="absolute top-16 left-0 right-0 bg-white shadow-md border-t py-3 flex flex-col space-y-3 text-center sm:hidden z-50">
          <Link
            to="/"
            className="py-2 text-gray-800 hover:text-blue-600"
            onClick={() => setOpen(false)}
          >
            Home
          </Link>
          <Link
            to="/packages"
            className="py-2 text-gray-800 hover:text-blue-600"
            onClick={() => setOpen(false)}
          >
            Packages
          </Link>
          <Link
            to="/plan-trip"
            className="py-2 text-gray-800 hover:text-blue-600"
            onClick={() => setOpen(false)}
          >
            Plan My Trip
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
