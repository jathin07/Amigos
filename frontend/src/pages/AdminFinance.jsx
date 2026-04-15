import { useEffect, useState } from 'react';
import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';

const AdminFinance = () => {
  const [finances, setFinances] = useState([]);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    lead_id: '',
    revenue: 0,
    transport_cost: 0,
    hotel_cost: 0,
    food_cost: 0,
    activity_cost: 0,
    other_cost: 0
  });

  const loadData = async () => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    setLoading(true);
    setError('');

    try {
      const headers = { Authorization: `Bearer ${token}` };
      
      const financeData = await apiFetch('/admin/finance', { headers });
      setFinances(financeData || []);
      
      const leadsData = await apiFetch('/admin/leads', { headers });
      setLeads(leadsData || []);
    } catch (err) {
      setError(err.message || 'Failed to load finance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'lead_id' ? value : parseFloat(value) || 0
    }));
  };

  const resetForm = () => {
    setFormData({
      id: null,
      lead_id: '',
      revenue: 0,
      transport_cost: 0,
      hotel_cost: 0,
      food_cost: 0,
      activity_cost: 0,
      other_cost: 0
    });
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (finance) => {
    setFormData({
      id: finance.id,
      lead_id: finance.lead_id || '',
      revenue: finance.revenue || 0,
      transport_cost: finance.transport_cost || 0,
      hotel_cost: finance.hotel_cost || 0,
      food_cost: finance.food_cost || 0,
      activity_cost: finance.activity_cost || 0,
      other_cost: finance.other_cost || 0
    });
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this finance record?')) return;
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/finance/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      setFinances(finances.filter(f => f.id !== id));
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      if (isEditing) {
        await apiFetch(`/admin/finance/${formData.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        });
      } else {
        await apiFetch(`/admin/finance`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        });
      }
      loadData();
      resetForm();
    } catch (err) {
      alert('Save failed: ' + err.message);
    }
  };

  // Helper calculation
  const totalCost = formData.transport_cost + formData.hotel_cost + formData.food_cost + formData.activity_cost + formData.other_cost;
  const currentProfit = formData.revenue - totalCost;

  return (
    <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 relative">
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-900 to-emerald-600 bg-clip-text text-transparent">
            Accounting & Finances
          </h2>
          <p className="text-sm text-gray-500 mt-1">Track trip revenues, costs, and profit margins</p>
        </div>
        <button 
          onClick={() => { resetForm(); setShowForm(true); }}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-emerald-500/30 hover:-translate-y-0.5 transition-all duration-300"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          Log Expense / Revenue
        </button>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50/50 border border-red-100 p-4 text-sm text-red-700 mb-6 flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          {error}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-10 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-6 sm:p-8 rounded-2xl border border-emerald-50/50 relative overflow-hidden transition-all duration-500 animate-fade-in-up">
          <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
          <h3 className="text-lg font-bold text-gray-800 mb-6">{isEditing ? 'Edit Finance Record' : 'Create Finance Record'}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="md:col-span-2 lg:col-span-3">
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Linked Lead (Trip)</label>
              <select required name="lead_id" value={formData.lead_id} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white">
                <option value="">Select a Lead / Trip</option>
                {leads.map(lead => (
                  <option key={lead.id} value={lead.id}>{lead.name} - {lead.travel_dates || 'No dates'} (ID: {lead.id})</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2 text-emerald-700">Total Revenue</label>
              <input type="number" step="0.01" required name="revenue" value={formData.revenue} onChange={handleInputChange} className="block w-full bg-emerald-50/30 border border-emerald-100 rounded-xl text-emerald-900 font-bold text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white" />
            </div>

            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Transport Cost</label>
              <input type="number" step="0.01" name="transport_cost" value={formData.transport_cost} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white" />
            </div>

            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Hotel Cost</label>
              <input type="number" step="0.01" name="hotel_cost" value={formData.hotel_cost} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white" />
            </div>

            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Food Cost</label>
              <input type="number" step="0.01" name="food_cost" value={formData.food_cost} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white" />
            </div>

            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Activity Cost</label>
              <input type="number" step="0.01" name="activity_cost" value={formData.activity_cost} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white" />
            </div>

            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Other Cost</label>
              <input type="number" step="0.01" name="other_cost" value={formData.other_cost} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all focus:bg-white" />
            </div>
          </div>
          
          <div className="mt-6 p-4 rounded-xl bg-gray-50 border border-gray-200 flex justify-between items-center sm:w-1/2 md:w-1/3">
            <div>
              <div className="text-xs uppercase tracking-wide text-gray-500 font-bold mb-1">Calculated Profit</div>
              <div className={`text-xl font-extrabold ${currentProfit >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                ₹{currentProfit.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="mt-8 flex gap-3">
            <button type="submit" className="bg-emerald-600 text-white px-6 py-2.5 rounded-full shadow-md font-medium text-sm hover:bg-emerald-700 hover:shadow-lg transition-all focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500">
              Save Record
            </button>
            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2.5 rounded-full font-medium text-sm hover:bg-gray-200 transition-all">
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-emerald-500">
          <svg className="animate-spin h-8 w-8 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <p className="text-sm font-medium animate-pulse">Loading finance records...</p>
        </div>
      ) : finances.length === 0 ? (
        <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50">
          <p className="text-gray-500 font-medium">No finance records available.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm">
          <table className="w-full text-left border-collapse bg-white whitespace-nowrap">
            <thead>
              <tr className="bg-gray-50/80 border-b-2 border-gray-100 text-xs uppercase tracking-wider text-gray-500">
                <th className="py-4 px-5 font-bold">Trip / Lead</th>
                <th className="py-4 px-5 font-bold">Revenue</th>
                <th className="py-4 px-5 font-bold">Costs Component</th>
                <th className="py-4 px-5 font-bold">Total Cost</th>
                <th className="py-4 px-5 font-bold">Profit</th>
                <th className="py-4 px-5 font-bold">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-gray-50">
              {finances.map((f) => (
                <tr key={f.id} className="hover:bg-emerald-50/30 transition-colors">
                  <td className="py-4 px-5 font-extrabold text-gray-900">{f.lead_name} <span className="text-xs font-normal text-gray-400 block">ID: {f.lead_id}</span></td>
                  <td className="py-4 px-5 font-bold text-emerald-700">₹{f.revenue}</td>
                  <td className="py-4 px-5">
                    <div className="text-xs text-gray-500 flex flex-col gap-0.5">
                       <span>🚗 ₹{f.transport_cost}</span>
                       <span>🏨 ₹{f.hotel_cost}</span>
                       <span>🍔 ₹{f.food_cost}</span>
                    </div>
                  </td>
                  <td className="py-4 px-5 font-bold text-gray-700">₹{f.total_cost}</td>
                  <td className="py-4 px-5">
                    <span className={`inline-flex px-2 py-1 text-xs font-bold uppercase rounded-md border ${f.profit >= 0 ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-red-50 text-red-700 border-red-100'}`}>
                      ₹{f.profit}
                    </span>
                  </td>
                  <td className="py-4 px-5">
                    <div className="flex gap-2">
                      <button onClick={() => handleEdit(f)} className="text-emerald-600 hover:text-emerald-900 font-bold text-xs uppercase">Edit</button>
                      <button onClick={() => handleDelete(f.id)} className="text-red-600 hover:text-red-900 font-bold text-xs uppercase">Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminFinance;
