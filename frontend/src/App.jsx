import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

import Home from "./pages/Home";
import PackagesList from "./pages/PackagesList";
import PackageDetail from "./pages/PackageDetails";
import BookingForm from "./pages/BookingForm";
import './App.css';
import './index.css';
function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/packages" element={<PackagesList />} />
        <Route path="/packages/:id" element={<PackageDetail />} />
        <Route path="/plan-trip" element={<BookingForm />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;
