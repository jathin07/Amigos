import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [tripRequests, setTripRequests] = useState([]);
  const [quickBookings, setQuickBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      const token = localStorage.getItem(ADMIN_TOKEN_KEY);
      if (!token) {
        navigate('/admin/login');
        return;
      }

      setLoading(true);
      setError('');

      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        };

        const [tripData, quickData] = await Promise.all([
          apiFetch('/admin/trip-requests', { headers }),
          apiFetch('/admin/quick-bookings', { headers }),
        ]);

        setTripRequests(tripData || []);
        setQuickBookings(quickData || []);
      } catch (dashboardError) {
        setError(dashboardError.message || 'Failed to load admin data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
    navigate('/admin/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="rounded-xl bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-500">View trip requests and quick booking leads.</p>
            </div>
            <div className="flex gap-3">
              <Link to="/" className="rounded-lg border px-3 py-2 text-sm text-gray-700 hover:bg-gray-50">Home</Link>
              <button onClick={handleLogout} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white hover:bg-indigo-700">
                Logout
              </button>
            </div>
          </div>
        </div>

        {error && <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <section className="rounded-xl bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Trip Requests ({tripRequests.length})</h2>
            {loading ? (
              <p className="text-sm text-gray-500">Loading...</p>
            ) : tripRequests.length === 0 ? (
              <p className="text-sm text-gray-500">No trip requests yet.</p>
            ) : (
              <div className="space-y-3">
                {tripRequests.map((request) => (
                  <div key={request.id} className="rounded-lg border border-gray-200 p-3 text-sm">
                    <div className="font-semibold text-gray-900">{request.user_name}</div>
                    <div className="text-gray-600">{request.contact_number} | {request.email || 'No email'}</div>
                    <div className="text-gray-600">Destination: {request.selected_destinations || 'Not specified'}</div>
                    <div className="text-gray-600">Travel Date: {request.travel_dates || 'Not specified'}</div>
                    <div className="text-gray-600">Travelers: {request.num_travelers || '-'}</div>
                    <div className="text-gray-600">Budget: {request.budget_range || 'Not specified'}</div>
                    {request.notes && <div className="mt-1 text-gray-700">Notes: {request.notes}</div>}
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-xl bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Quick Bookings ({quickBookings.length})</h2>
            {loading ? (
              <p className="text-sm text-gray-500">Loading...</p>
            ) : quickBookings.length === 0 ? (
              <p className="text-sm text-gray-500">No quick bookings yet.</p>
            ) : (
              <div className="space-y-3">
                {quickBookings.map((booking) => (
                  <div key={booking.id} className="rounded-lg border border-gray-200 p-3 text-sm">
                    <div className="font-semibold text-gray-900">{booking.user_name}</div>
                    <div className="text-gray-600">{booking.contact_number} | {booking.email || 'No email'}</div>
                    <div className="text-gray-600">Destination: {booking.preferred_destinations || 'Not specified'}</div>
                    <div className="text-gray-600">Preferred Time: {booking.preferred_time || 'Not specified'}</div>
                    {booking.notes && <div className="mt-1 text-gray-700">Notes: {booking.notes}</div>}
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
