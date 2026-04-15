import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';
import AdminPackages from './AdminPackages';
import AdminDestinations from './AdminDestinations';
import AdminStaff from './AdminStaff';
import AdminFinance from './AdminFinance';
import AdminTasks from './AdminTasks';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('leads');
  const [leads, setLeads] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [convertModalOpen, setConvertModalOpen] = useState(false);
  const [leadToConvert, setLeadToConvert] = useState(null);
  const [convertForm, setConvertForm] = useState({ total_price: '', start_date: '', end_date: '' });

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

      const leadsData = await apiFetch('/admin/leads', { headers });
      setLeads(leadsData || []);

      const staffData = await apiFetch('/admin/team-members', { headers });
      setTeamMembers(staffData || []);
    } catch (dashboardError) {
      setError(dashboardError.message || 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [navigate]);

  const handleStatusChange = async (leadId, newStatus) => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/lead/${leadId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });
      // Optionally refresh data or update locally
      setLeads(leads.map(lead => lead.id === leadId ? { ...lead, status: newStatus } : lead));
    } catch (err) {
      setError('Failed to update lead status: ' + err.message);
    }
  };

  const openConvertModal = (lead) => {
    setLeadToConvert(lead);
    setConvertForm({ total_price: '', start_date: '', end_date: '' });
    setConvertModalOpen(true);
  };

  const closeConvertModal = () => {
    setConvertModalOpen(false);
    setLeadToConvert(null);
  };

  const executeConvertLead = async (e) => {
    e.preventDefault();
    if (!leadToConvert) return;
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    
    try {
      await apiFetch(`/admin/lead/${leadToConvert.id}/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          total_price: parseFloat(convertForm.total_price) || 0,
          start_date: convertForm.start_date,
          end_date: convertForm.end_date
        }),
      });
      alert("Lead converted to booking successfully!");
      closeConvertModal();
      loadData(); 
    } catch (err) {
      setError('Failed to convert lead: ' + err.message);
      closeConvertModal();
    }
  };

  const handleAssigneeChange = async (leadId, newAssigneeId) => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/lead/${leadId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ contact_person_id: newAssigneeId ? parseInt(newAssigneeId) : null }),
      });
      setLeads(leads.map(lead => lead.id === leadId ? { ...lead, contact_person_id: newAssigneeId ? parseInt(newAssigneeId) : null } : lead));
    } catch (err) {
      setError('Failed to update lead assignee: ' + err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
    navigate('/admin/login');
  };

  return (
    <div className="min-h-screen bg-gray-50/50 p-4 sm:p-6 lg:p-8 font-sans">
      <div className="mx-auto max-w-7xl space-y-8">
        
        {/* Header Section */}
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 relative overflow-hidden transition-all duration-300 hover:shadow-md">
          {/* Decorative subtle orb */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>

          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between relative z-10">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent mb-1">
                Admin Dashboard
              </h1>
              <p className="text-sm font-medium text-gray-500">Manage all customer leads, packages, and catalog data securely.</p>
            </div>
            <div className="flex gap-3">
              <Link to="/" className="flex items-center justify-center rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors shadow-sm">
                <svg className="w-4 h-4 mr-1.5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                View Site
              </Link>
              <button onClick={handleLogout} className="flex items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-700 px-4 py-2 text-sm font-semibold text-white hover:from-indigo-700 hover:to-indigo-800 transition-all shadow-md shadow-indigo-200 hover:-translate-y-0.5">
                <svg className="w-4 h-4 mr-1.5 opacity-90" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                Logout
              </button>
            </div>
          </div>
          
          <div className="mt-8 border-t border-gray-100/80 pt-6 flex flex-wrap gap-3 relative z-10">
            <button 
              onClick={() => setActiveTab('leads')}
              className={`px-5 py-2.5 font-bold text-sm rounded-full transition-all duration-300 ${activeTab === 'leads' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700' : 'text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border border-transparent'}`}
            >
              Customer Leads
            </button>
            <button 
              onClick={() => setActiveTab('packages')}
              className={`px-5 py-2.5 font-bold text-sm rounded-full transition-all duration-300 ${activeTab === 'packages' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700' : 'text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border border-transparent'}`}
            >
              Tour Packages
            </button>
            <button 
              onClick={() => setActiveTab('destinations')}
              className={`px-5 py-2.5 font-bold text-sm rounded-full transition-all duration-300 ${activeTab === 'destinations' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700' : 'text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border border-transparent'}`}
            >
              Destinations Catalog
            </button>
            <button 
              onClick={() => setActiveTab('staff')}
              className={`px-5 py-2.5 font-bold text-sm rounded-full transition-all duration-300 ${activeTab === 'staff' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700' : 'text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border border-transparent'}`}
            >
              Staff Management
            </button>
            <button 
              onClick={() => setActiveTab('finance')}
              className={`px-5 py-2.5 font-bold text-sm rounded-full transition-all duration-300 ${activeTab === 'finance' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700' : 'text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border border-transparent'}`}
            >
              Accounting/Finances
            </button>
            <button 
              onClick={() => setActiveTab('tasks')}
              className={`px-5 py-2.5 font-bold text-sm rounded-full transition-all duration-300 ${activeTab === 'tasks' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700' : 'text-gray-600 bg-gray-100 hover:bg-gray-200 hover:text-gray-900 border border-transparent'}`}
            >
              System Tasks
            </button>
          </div>
        </div>

        {activeTab === 'leads' ? (
          <div className="animate-fade-in-up">
            {error && (
              <div className="rounded-xl bg-red-50/80 backdrop-blur border border-red-100 p-4 text-sm font-medium text-red-700 mb-6 flex items-center gap-3 shadow-sm">
                <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                {error}
              </div>
            )}

            <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 relative">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent mb-6">
                Leads Management <span className="text-sm font-medium bg-indigo-100 text-indigo-700 ml-2 px-2.5 py-0.5 rounded-full">{leads.length} total</span>
              </h2>
              
              {loading ? (
                <div className="flex flex-col items-center justify-center py-20 text-indigo-500">
                  <svg className="animate-spin h-8 w-8 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  <p className="text-sm font-medium animate-pulse">Loading leads directory...</p>
                </div>
              ) : leads.length === 0 ? (
                <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                  <p className="text-gray-500 font-medium">Inbox zero! No new customer leads at the moment.</p>
                </div>
              ) : (
                <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm">
                  <table className="w-full text-left border-collapse min-w-[900px] bg-white">
                    <thead>
                      <tr className="bg-gray-50/80 border-b-2 border-gray-100 text-xs uppercase tracking-wider text-gray-500">
                        <th className="py-4 px-5 font-bold w-[28%]">Customer Contact</th>
                        <th className="py-4 px-5 font-bold w-[32%]">Trip Requirements</th>
                        <th className="py-4 px-5 font-bold w-[22%]">Metrics</th>
                        <th className="py-4 px-5 font-bold w-44">Lead Status</th>
                      </tr>
                    </thead>
                    <tbody className="text-sm divide-y divide-gray-50">
                      {leads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-indigo-50/30 transition-colors group">
                          <td className="py-4 px-5 align-top">
                            <div className="font-extrabold text-gray-900 text-base mb-1">{lead.name}</div>
                            <div className="text-gray-600 font-medium text-xs flex items-center gap-1.5 mb-1">
                              <svg className="w-3 h-3 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                              {lead.phone}
                            </div>
                            {lead.email && (
                              <div className="text-gray-500 font-medium text-xs flex items-center gap-1.5 mb-2.5">
                                <svg className="w-3 h-3 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                                {lead.email}
                              </div>
                            )}
                            <div className="mt-2 inline-flex border border-indigo-100 text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-indigo-50/50 text-indigo-700 items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                              {lead.lead_type === 'trip_request' ? 'Custom Trip' : lead.lead_type.replace('_', ' ')}
                            </div>
                          </td>
                          <td className="py-4 px-5 align-top">
                            <div className="text-gray-800 font-medium flex items-start gap-2 mb-2">
                              <svg className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                              <div>
                                <span className="text-xs text-gray-400 uppercase tracking-wide block mb-0.5">Travel Dates</span>
                                {lead.travel_dates || <span className="italic text-gray-400">Flexible / Not specified</span>}
                              </div>
                            </div>
                            {lead.package_id && (
                              <div className="text-xs font-bold mt-2 bg-purple-50 text-purple-700 px-2.5 py-1 rounded-md inline-block border border-purple-100">
                                Target Package ID: <span className="font-mono text-purple-900 bg-white px-1 ml-1 rounded">{lead.package_id}</span>
                              </div>
                            )}
                            {lead.notes && (
                              <div className="text-gray-600 text-xs mt-3 bg-gray-50 border border-gray-100 p-2.5 rounded-lg border-l-2 border-l-blue-400 italic">
                                "{lead.notes}"
                              </div>
                            )}
                          </td>
                          <td className="py-4 px-5 align-top text-gray-800">
                            <div className="mb-4">
                              <span className="text-xs text-gray-400 uppercase tracking-wide font-bold block mb-1">Stated Budget</span>
                              <div className="font-mono text-gray-900 bg-gray-50 inline-block px-2 py-0.5 rounded border border-gray-100">
                                {lead.budget || <span className="text-gray-400 italic font-sans text-xs">Undefined</span>}
                              </div>
                            </div>
                            <div>
                              <span className="text-xs text-gray-400 uppercase tracking-wide font-bold block mb-1">Pax Setup</span>
                              <div className="flex items-center gap-1.5 font-bold text-gray-700">
                                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                                {lead.travelers ? `${lead.travelers} Travelers` : <span className="text-gray-400 italic text-xs">-</span>}
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-5 align-top">
                            <div className="relative">
                              <select
                                value={lead.status}
                                onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                                className={`w-full text-xs font-bold uppercase tracking-wider rounded-xl border py-2.5 px-3 appearance-none cursor-pointer transition-all focus:ring-2 focus:ring-offset-1 focus:outline-none ${
                                  lead.status === 'pending' ? 'bg-amber-50 text-amber-700 border-amber-200 focus:ring-amber-500 hover:bg-amber-100' :
                                  lead.status === 'contacted' ? 'bg-sky-50 text-sky-700 border-sky-200 focus:ring-sky-500 hover:bg-sky-100' :
                                  lead.status === 'confirmed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 focus:ring-emerald-500 hover:bg-emerald-100' :
                                  lead.status === 'completed' ? 'bg-gray-100 text-gray-700 border-gray-200 focus:ring-gray-500 hover:bg-gray-200' :
                                  'bg-white border-gray-300 text-gray-700'
                                }`}
                              >
                                <option value="pending">⏳ Pending</option>
                                <option value="contacted">📞 Contacted</option>
                                <option value="confirmed">✅ Confirmed</option>
                                <option value="completed">🎉 Completed</option>
                              </select>
                              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 opacity-60">
                                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                              </div>
                            </div>
                            
                            <div className="mt-3">
                              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide block mb-1">Assigned To</span>
                              <select
                                value={lead.contact_person_id || ''}
                                onChange={(e) => handleAssigneeChange(lead.id, e.target.value)}
                                className="w-full text-xs font-semibold rounded-lg border border-gray-200 py-1.5 px-2 bg-gray-50 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                              >
                                <option value="">Unassigned</option>
                                {teamMembers.filter(m => m.active).map(m => (
                                  <option key={m.id} value={m.id}>{m.name} ({m.role})</option>
                                ))}
                              </select>
                            </div>

                            <div className="mt-3 flex justify-between items-center">
                              {(lead.status === 'pending' || lead.status === 'contacted') && (
                                <button
                                  onClick={() => openConvertModal(lead)}
                                  className="text-[10px] font-bold bg-emerald-600 text-white px-2 py-1 rounded hover:bg-emerald-700 transition-colors uppercase shadow-sm"
                                >
                                  Convert to Booking
                                </button>
                              )}
                              <a href={`mailto:${lead.email}?subject=Regarding your trip with Amigos`} className="text-[10px] font-bold text-indigo-500 hover:text-indigo-700 uppercase tracking-widest hover:underline opacity-0 group-hover:opacity-100 transition-opacity ml-auto">Contact →</a>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

        ) : activeTab === 'packages' ? (
          <AdminPackages />
        ) : activeTab === 'destinations' ? (
          <AdminDestinations />
        ) : activeTab === 'staff' ? (
          <AdminStaff />
        ) : activeTab === 'tasks' ? (
          <AdminTasks />
        ) : (
          <AdminFinance />
        )}
      </div>

      {convertModalOpen && leadToConvert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-fade-in-up">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
              <h3 className="text-xl font-bold text-gray-900">Convert Lead to Booking</h3>
              <p className="text-sm text-gray-500 mt-1">Finalize trip details for {leadToConvert.name}</p>
            </div>
            <form onSubmit={executeConvertLead} className="p-6 space-y-4 text-left">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Total Booking Price</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500 font-bold">$</span>
                  <input 
                    type="number" 
                    required 
                    min="0"
                    step="0.01"
                    value={convertForm.total_price}
                    onChange={(e) => setConvertForm({...convertForm, total_price: e.target.value})}
                    className="w-full rounded-xl border border-gray-200 pl-8 p-3 focus:ring-2 focus:ring-indigo-500 outline-none" 
                    placeholder="15000" 
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Start Date</label>
                  <input 
                    type="date" 
                    required
                    value={convertForm.start_date}
                    onChange={(e) => setConvertForm({...convertForm, start_date: e.target.value})}
                    className="w-full rounded-xl border border-gray-200 p-3 focus:ring-2 focus:ring-indigo-500 outline-none uppercase text-sm" 
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">End Date</label>
                  <input 
                    type="date" 
                    required
                    value={convertForm.end_date}
                    onChange={(e) => setConvertForm({...convertForm, end_date: e.target.value})}
                    className="w-full rounded-xl border border-gray-200 p-3 focus:ring-2 focus:ring-indigo-500 outline-none uppercase text-sm" 
                  />
                </div>
              </div>
              <div className="pt-4 flex justify-end gap-3 border-t border-gray-100 mt-6">
                <button type="button" onClick={closeConvertModal} className="px-5 py-2.5 rounded-xl font-bold bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors">
                  Cancel
                </button>
                <button type="submit" className="px-6 py-2.5 rounded-xl font-bold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-md shadow-emerald-200">
                  Confirm Booking
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default AdminDashboard;
