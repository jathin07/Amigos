import { useEffect, useState } from 'react';
import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';

const AdminPackages = () => {
  const [packages, setPackages] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    title: '',
    description: '',
    duration_days: 1,
    duration_nights: 1,
    price_per_person: 0,
    thumbnail_url: '',
    highlights: '',
    destination_ids: []
  });

  const getImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('http') || url.startsWith('/')) return url;
    return `/images/places/${url}`;
  };

  const loadData = async () => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    setLoading(true);
    setError('');

    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [pkgsData, destsData] = await Promise.all([
        apiFetch('/admin/packages', { headers }),
        apiFetch('/destinations')
      ]);
      
      setPackages(pkgsData || []);
      setDestinations(destsData || []);
    } catch (err) {
      setError(err.message || 'Failed to load packages data');
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
      [name]: name === 'duration_days' || name === 'duration_nights' || name === 'price_per_person' 
        ? Number(value) 
        : value
    }));
  };

  const handleDestinationToggle = (destId) => {
    setFormData(prev => {
      const isSelected = prev.destination_ids.includes(destId);
      return {
        ...prev,
        destination_ids: isSelected 
          ? prev.destination_ids.filter(id => id !== destId)
          : [...prev.destination_ids, destId]
      };
    });
  };

  const resetForm = () => {
    setFormData({
      id: null, title: '', description: '', duration_days: 1, duration_nights: 1,
      price_per_person: 0, thumbnail_url: '', highlights: '', destination_ids: []
    });
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (pkg) => {
    setFormData({
      ...pkg,
      destination_ids: pkg.destination_ids || []
    });
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this package?')) return;
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/packages/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      setPackages(packages.filter(p => p.id !== id));
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      if (isEditing) {
        await apiFetch(`/admin/packages/${formData.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        });
      } else {
        await apiFetch(`/admin/packages`, {
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

  return (
    <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 relative">
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent">
            Packages Management
          </h2>
          <p className="text-sm text-gray-500 mt-1">Design and manage tour packages ({packages.length})</p>
        </div>
        <button 
          onClick={() => { resetForm(); setShowForm(true); }}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-0.5 transition-all duration-300"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          Add Package
        </button>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50/50 border border-red-100 p-4 text-sm text-red-700 mb-6 flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          {error}
        </div>
      )}

      {showForm ? (
        <form onSubmit={handleSubmit} className="mb-10 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-6 sm:p-8 rounded-2xl border border-indigo-50/50 relative overflow-hidden transition-all duration-500 animate-fade-in-up">
          <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
          <h3 className="text-lg font-bold text-gray-800 mb-6">{isEditing ? 'Edit Package details' : 'Create new Package'}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Title</label>
              <input required name="title" value={formData.title} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all" />
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Price Per Person (₹)</label>
              <input required type="number" name="price_per_person" value={formData.price_per_person} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all cursor-text font-mono" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Description</label>
              <textarea name="description" value={formData.description} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all resize-none" rows="2"></textarea>
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Duration (Days)</label>
              <input required type="number" name="duration_days" value={formData.duration_days} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Duration (Nights)</label>
              <input required type="number" name="duration_nights" value={formData.duration_nights} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Thumbnail URL</label>
              <input name="thumbnail_url" value={formData.thumbnail_url} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all" />
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Highlights (Comma separated)</label>
              <input name="highlights" value={formData.highlights} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-3">Linked Destinations</label>
              <div className="flex flex-wrap gap-2 p-4 bg-gray-50/50 border border-gray-200 rounded-xl max-h-48 overflow-y-auto">
                {destinations.length === 0 ? <span className="text-sm text-gray-400 italic">No destinations in catalog</span> : null}
                {destinations.map(dest => (
                  <label key={dest.id} className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-sm cursor-pointer transition-all ${formData.destination_ids.includes(dest.id) ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                    <input 
                      type="checkbox" 
                      checked={formData.destination_ids.includes(dest.id)}
                      onChange={() => handleDestinationToggle(dest.id)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                    />
                    <span className="font-medium">{dest.name}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-8 flex gap-3">
            <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-full shadow-md font-medium text-sm hover:bg-indigo-700 hover:shadow-lg transition-all focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Save Package</button>
            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2.5 rounded-full font-medium text-sm hover:bg-gray-200 transition-all">Cancel</button>
          </div>
        </form>
      ) : null}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-indigo-500">
          <svg className="animate-spin h-8 w-8 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <p className="text-sm font-medium animate-pulse">Loading packages...</p>
        </div>
      ) : packages.length === 0 ? (
        <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50">
          <p className="text-gray-500 font-medium">No packages created yet.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm relative z-10">
          <table className="w-full text-left border-collapse min-w-[800px] bg-white">
             <thead>
              <tr className="bg-gray-50/80 border-b border-gray-100 text-xs uppercase tracking-wider text-gray-500">
                <th className="py-4 px-4 font-semibold w-24">Image</th>
                <th className="py-4 px-4 font-semibold w-[30%]">Package Details</th>
                <th className="py-4 px-4 font-semibold w-[30%]">Destinations</th>
                <th className="py-4 px-4 font-semibold">Pricing</th>
                <th className="py-4 px-4 font-semibold text-right w-28">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-gray-50">
              {packages.map((pkg) => (
                <tr key={pkg.id} className="hover:bg-indigo-50/30 transition-colors group">
                  <td className="py-3 px-4">
                    <div className="relative w-16 h-16 rounded-xl overflow-hidden bg-gray-100 border border-gray-200">
                      {pkg.thumbnail_url ? (
                        <img 
                          src={getImageUrl(pkg.thumbnail_url)} 
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" 
                          alt={pkg.title} 
                          onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/100x100/f3f4f6/a1a1aa?text=Image"; }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-[10px] text-gray-400 font-medium">No img</div>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 align-middle">
                    <div className="font-bold text-gray-900 text-base">{pkg.title}</div>
                    <div className="flex items-center gap-2 mt-1.5 opacity-80">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                        {pkg.duration_days}D / {pkg.duration_nights}N
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 align-middle">
                    <div className="flex flex-wrap gap-1.5">
                      {pkg.destination_ids && pkg.destination_ids.length > 0 ? (
                        pkg.destination_ids.map(id => {
                          const name = destinations.find(d => d.id === id)?.name;
                          return name ? (
                            <span key={id} className="bg-gray-100 text-gray-600 border border-gray-200 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide">
                              {name}
                            </span>
                          ) : null;
                        })
                      ) : (
                        <span className="text-xs text-gray-400 italic">None</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4 align-middle">
                    <div className="font-mono text-lg font-bold text-gray-900">₹{pkg.price_per_person.toLocaleString('en-IN')}</div>
                    <div className="text-[10px] uppercase tracking-wide text-gray-400 font-bold mt-0.5">per person</div>
                  </td>
                  <td className="py-3 px-4 align-middle text-right">
                    <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <button 
                        onClick={() => handleEdit(pkg)} 
                        className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center hover:bg-indigo-600 hover:text-white transition-colors border border-indigo-100 hover:border-transparent cursor-pointer"
                        title="Edit"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                      </button>
                      <button 
                        onClick={() => handleDelete(pkg.id)} 
                        className="w-8 h-8 rounded-full bg-red-50 text-red-600 flex items-center justify-center hover:bg-red-600 hover:text-white transition-colors border border-red-100 hover:border-transparent cursor-pointer"
                        title="Delete"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                      </button>
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

export default AdminPackages;
