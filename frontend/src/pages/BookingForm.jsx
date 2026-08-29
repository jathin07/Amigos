import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { apiFetch } from "../config/api";
import { 
  User, 
  Phone, 
  Mail, 
  MapPin, 
  Calendar, 
  Users, 
  Wallet, 
  FileText, 
  Sparkles, 
  Loader2,
  Compass,
  CalendarDays
} from "lucide-react";

// Client-side Zod validation matching backend constraints
const bookingFormSchema = z.object({
  name: z.string().min(1, "Full Name is required").max(100, "Name must be under 100 characters"),
  phone: z.string().min(5, "Phone number must be at least 5 digits").max(20, "Phone number must be under 20 digits"),
  email: z.string().email("Invalid email address").optional().or(z.literal("")),
  destination: z.string().max(255).optional().or(z.literal("")),
  travelDate: z.string().optional().or(z.literal("")),
  travelers: z.coerce.number().min(1, "Must be at least 1 traveler"),
  budget: z.coerce.number().min(0, "Budget cannot be negative").optional().or(z.literal("")),
  tripType: z.string().optional(),
  estimatedTripDays: z.coerce.number().min(1, "Duration must be at least 1 day").optional().or(z.literal("")),
  maleCount: z.coerce.number().min(0).optional().or(z.literal("")),
  femaleCount: z.coerce.number().min(0).optional().or(z.literal("")),
  facultyCount: z.coerce.number().min(0).optional().or(z.literal("")),
  notes: z.string().optional().or(z.literal("")),
});

const BookingForm = () => {
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    reset
  } = useForm({
    resolver: zodResolver(bookingFormSchema),
    mode: "onBlur",
    defaultValues: {
      travelers: 1,
      name: "",
      phone: "",
      email: "",
      destination: "",
      travelDate: "",
      budget: "",
      tripType: "",
      estimatedTripDays: "",
      maleCount: "",
      femaleCount: "",
      facultyCount: "",
      notes: "",
    }
  });

  const notesValue = watch("notes") || "";
  const travelersCount = Number(watch("travelers")) || 1;

  // Dynamic AI suggestion fetcher on notes input
  useEffect(() => {
    if (notesValue.length < 15) {
      setAiSuggestion("");
      return;
    }

    const timer = setTimeout(async () => {
      setAiLoading(true);
      try {
        const res = await apiFetch("/ai/analyze-notes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ notes: notesValue }),
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
  }, [notesValue]);

  const handleFormSubmit = async (data) => {
    setError("");
    setSuccess("");

    // Inject operational context into notes if provided
    let finalNotes = data.notes || "";
    if (data.tripType) finalNotes += `\n[Trip Type]: ${data.tripType}`;
    if (data.leadSource) finalNotes += `\n[Source]: ${data.leadSource}`;
    finalNotes = finalNotes.trim();

    // Adapt flat form fields to backend payload expectation
    const payload = {
      name: data.name,
      phone: data.phone,
      email: data.email || null,
      lead_type: "trip_request",
      preferred_destination: data.destination || null,
      travel_dates: data.travelDate || null,
      travelers: Number(data.travelers) || 1,
      budget: data.budget ? String(data.budget) : null,
      trip_type: data.tripType || null,
      estimated_trip_days: data.estimatedTripDays ? Number(data.estimatedTripDays) : null,
      male_count: data.maleCount ? Number(data.maleCount) : null,
      female_count: data.femaleCount ? Number(data.femaleCount) : null,
      faculty_count: data.facultyCount ? Number(data.facultyCount) : null,
      notes: data.notes || null,
    };

    try {
      const result = await apiFetch("/lead", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      setSuccess(`Trip request submitted successfully! Your Lead reference ID is: ${result.lead_id}`);
      setAiSuggestion("");
      reset();
    } catch (err) {
      console.error("Error submitting trip request:", err);
      setError(err.message || "Failed to submit request. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 select-none font-sans">
      
      {/* Centered card frame */}
      <div className="max-w-xl w-full space-y-8 bg-white border border-slate-200 p-8 rounded-2xl shadow-xl transition-all duration-300">
        
        {/* Title branding */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 bg-blue-50 text-blue-600 rounded-2xl border border-blue-100 shadow-sm">
            <Sparkles size={24} />
          </div>
          <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Plan Your Ideal Escape</h2>
          <p className="text-xs text-slate-500 font-medium">
            Share your preferences and let our tour coordinators craft a custom itinerary for you.
          </p>
        </div>

        {/* Status Alerts */}
        {error && (
          <div className="p-3 bg-rose-50 border border-rose-100 text-rose-700 text-xs font-semibold rounded-xl animate-in fade-in duration-200">
            {error}
          </div>
        )}

        {success && (
          <div className="p-4 bg-emerald-50 border border-emerald-100 text-emerald-800 text-xs font-semibold rounded-xl animate-in fade-in duration-200 space-y-1">
            <p className="text-emerald-700 font-bold">Thank you!</p>
            <p className="text-slate-600 leading-relaxed font-semibold">{success}</p>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 pt-1">
          
          {/* Customer contact fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <User size={12} className="mr-1 text-slate-400" />
                Full Name *
              </label>
              <input
                type="text"
                placeholder="e.g. Adarsh Hegde"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.name ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("name")}
              />
              {errors.name && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <Phone size={12} className="mr-1 text-slate-400" />
                Phone Number *
              </label>
              <input
                type="text"
                placeholder="e.g. +91 9988776655"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.phone ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("phone")}
              />
              {errors.phone && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.phone.message}</p>
              )}
            </div>
          </div>

          {/* Email and Destination */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <Mail size={12} className="mr-1 text-slate-400" />
                Email Address
              </label>
              <input
                type="email"
                placeholder="e.g. adarsh@example.com"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.email ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("email")}
              />
              {errors.email && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <MapPin size={12} className="mr-1 text-slate-400" />
                Preferred Destination
              </label>
              <input
                type="text"
                placeholder="e.g. Munnar, Wayanad"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.destination ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("destination")}
              />
              {errors.destination && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.destination.message}</p>
              )}
            </div>
          </div>

          {/* Travel Date and Travelers Count */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <Calendar size={12} className="mr-1 text-slate-400" />
                Target Travel Date
              </label>
              <input
                type="date"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.travelDate ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("travelDate")}
              />
              {errors.travelDate && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.travelDate.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <Users size={12} className="mr-1 text-slate-400" />
                Total Travelers
              </label>
              <input
                type="number"
                min="1"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.travelers ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("travelers")}
              />
              {errors.travelers && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.travelers.message}</p>
              )}
            </div>
          </div>

          {/* Trip Type and Estimated Duration */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <Compass size={12} className="mr-1 text-slate-400 animate-spin-slow" />
                Trip Type
              </label>
              <select
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.tripType ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("tripType")}
              >
                <option value="">Select Trip Type...</option>
                <option value="leisure">Leisure</option>
                <option value="corporate">Corporate</option>
                <option value="educational">Educational</option>
                <option value="adventure">Adventure</option>
                <option value="honeymoon">Honeymoon</option>
                <option value="wellness">Wellness</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
                <CalendarDays size={12} className="mr-1 text-slate-400" />
                Estimated Duration (Days)
              </label>
              <input
                type="number"
                min="1"
                placeholder="e.g. 5"
                className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                  errors.estimatedTripDays ? "border-red-300 focus:ring-red-500" : "border-slate-300"
                }`}
                {...register("estimatedTripDays")}
              />
              {errors.estimatedTripDays && (
                <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.estimatedTripDays.message}</p>
              )}
            </div>
          </div>

          {/* Demographic Breakdown (Conditional) */}
          {travelersCount > 1 && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3 animate-in fade-in duration-200">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Group Demographics Breakdown (Optional)</p>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[10px] font-semibold text-slate-600 mb-1">Adult Males</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="0"
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                    {...register("maleCount")}
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-600 mb-1">Adult Females</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="0"
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                    {...register("femaleCount")}
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-slate-600 mb-1">Faculty / Chaperone</label>
                  <input
                    type="number"
                    min="0"
                    placeholder="0"
                    className="w-full px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                    {...register("facultyCount")}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Budget */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center">
              <Wallet size={12} className="mr-1 text-slate-400" />
              Budget Range (INR)
            </label>
            <input
              type="text"
              placeholder="e.g. 30000 - 50000"
              className={`w-full px-3 py-2 border rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium ${
                errors.budget ? "border-red-300 focus:ring-red-500" : "border-slate-300"
              }`}
              {...register("budget")}
            />
            {errors.budget && (
              <p className="mt-1 text-[10px] text-red-600 font-bold">{errors.budget.message}</p>
            )}
          </div>

          {/* Travel requirements and AI panel */}
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-slate-600 flex items-center">
              <FileText size={12} className="mr-1 text-slate-400" />
              Detailed Request Notes
            </label>
            <textarea
              rows="3"
              placeholder="List specific preferences (e.g. vegetarian dining, child seats, active trekking, premium hotels)..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
              {...register("notes")}
            />
            
            {/* Dynamic AI Analysis block */}
            {aiLoading && (
              <div className="flex items-center text-[10px] text-blue-600 font-semibold animate-pulse pt-1 pl-1">
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                <span>AI travel assistant is analyzing notes...</span>
              </div>
            )}
            
            {aiSuggestion && !aiLoading && (
              <div className="bg-blue-50 border border-blue-100 rounded-xl p-3.5 mt-2 transition-all duration-300 flex items-start space-x-2.5 shadow-sm">
                <span className="text-sm shrink-0">✨</span>
                <p className="text-[11px] text-blue-900 leading-relaxed font-semibold">
                  {aiSuggestion}
                </p>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-4 flex items-center justify-center space-x-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 rounded-lg font-bold text-xs shadow-md shadow-blue-500/10 transition-colors focus:outline-none"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="animate-spin" size={14} />
                <span>Submitting request...</span>
              </>
            ) : (
              <span>Submit Trip Request</span>
            )}
          </button>

        </form>

      </div>
    </div>
  );
};

export default BookingForm;