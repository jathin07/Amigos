import { useState, useEffect } from "react";
import { apiFetch } from "../config/api";

const initialForm = {
  name: "",
  phone: "",
  email: "",
  destination: "",
  travelDate: "",
  travelers: 1,
  budget: "",
  notes: "",
};

const BookingForm = () => {
  const [formData, setFormData] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    const notes = formData.notes;
    if (notes.length < 15) {
      setAiSuggestion("");
      return;
    }

    const timer = setTimeout(async () => {
      setAiLoading(true);
      try {
        const res = await apiFetch("/ai/analyze-notes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ notes }),
        });
        if (res.suggestion) {
          setAiSuggestion(res.suggestion);
        } else {
          setAiSuggestion("");
        }
      } catch (e) {
        console.error("AI error:", e);
      } finally {
        setAiLoading(false);
      }
    }, 1500);

    return () => clearTimeout(timer);
  }, [formData.notes]);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    const payload = {
      name: formData.name,
      phone: formData.phone,
      email: formData.email,
      lead_type: "trip_request",
      preferred_destination: formData.destination,
      travel_dates: formData.travelDate,
      travelers: Number(formData.travelers) || 1,
      budget: formData.budget,
      notes: formData.notes,
    };

    try {
      const result = await apiFetch("/lead", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      setSuccess(`Trip request submitted successfully. Request ID: ${result.lead_id}`);
      setFormData(initialForm);
    } catch (err) {
      console.error("Error submitting trip request:", err);
      setError(err.message || "Failed to submit request. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex justify-center items-center p-6">
      <div className="bg-white shadow-xl rounded-2xl p-8 max-w-lg w-full">
        <h2 className="text-2xl font-bold text-center text-indigo-600 mb-6">
          Plan Your Trip
        </h2>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Full Name"
            required
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <input
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="Phone Number"
            required
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <input
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email (optional)"
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <input
            name="destination"
            value={formData.destination}
            onChange={handleChange}
            placeholder="Preferred Destination"
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <input
            type="date"
            name="travelDate"
            value={formData.travelDate}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <input
            type="number"
            name="travelers"
            value={formData.travelers}
            onChange={handleChange}
            min="1"
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <input
            name="budget"
            value={formData.budget}
            onChange={handleChange}
            placeholder="Budget Range"
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows="3"
            placeholder="Tell us about any specific details (kids, seniors, honeymoon, adventure, budget constraints)..."
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-indigo-500"
          />

          {aiLoading && (
            <div className="flex items-center text-sm text-indigo-500 animate-pulse mt-1 ml-2">
              <svg className="w-4 h-4 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              AI is analyzing your notes...
            </div>
          )}
          
          {aiSuggestion && !aiLoading && (
            <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-4 mt-2 transition-all duration-500 shadow-sm flex items-start space-x-3">
              <div className="text-xl">✨</div>
              <div className="text-sm text-indigo-800 leading-relaxed font-medium">
                {aiSuggestion}
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-60"
          >
            {loading ? "Submitting..." : "Submit Trip Request"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default BookingForm;