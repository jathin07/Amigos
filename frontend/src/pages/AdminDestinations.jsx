import { useEffect, useState } from 'react';
import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';

const AdminDestinations = () => {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    name: '',
    state: '',
    description: '',
    image_url: '',
    tags: ''
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
      const destsData = await apiFetch('/admin/destinations', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDestinations(destsData || []);
    } catch (err) {
      setError(err.message || 'Failed to load destinations data');
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
      [name]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      id: null, name: '', state: '', description: '', image_url: '', tags: ''
    });
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (dest) => {
    setFormData(dest);
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this destination? Projects matching this destination will be affected.')) return;
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/destinations/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      setDestinations(destinations.filter(d => d.id !== id));
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      if (isEditing) {
        await apiFetch(`/admin/destinations/${formData.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        });
      } else {
        await apiFetch(`/admin/destinations`, {
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
      {/* Decorative gradient orb for premium feel */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent">
            Destinations Catalog
          </h2>
          <p className="text-sm text-gray-500 mt-1">Manage all available places ({destinations.length})</p>
        </div>
        <button 
          onClick={() => { resetForm(); setShowForm(true); }}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-0.5 transition-all duration-300"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          Add Destination
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
          <h3 className="text-lg font-bold text-gray-800 mb-6">{isEditing ? 'Edit Destination details' : 'Create new Destination'}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Name</label>
              <input required name="name" value={formData.name} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white" placeholder="e.g. Munnar" />
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">State / Region</label>
              <input name="state" value={formData.state} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white" placeholder="e.g. Kerala" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Description</label>
              <textarea name="description" value={formData.description} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white resize-none" rows="3" placeholder="A brief description of what makes this place special..."></textarea>
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Image URL</label>
              <input name="image_url" value={formData.image_url} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white" placeholder="filename.jpg or full URL" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Tags</label>
              <input name="tags" value={formData.tags} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white" placeholder="e.g. mountains, nature, peaceful" />
            </div>
          </div>
          <div className="mt-8 flex gap-3">
            <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-full shadow-md font-medium text-sm hover:bg-indigo-700 hover:shadow-lg transition-all focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Save Destination
            </button>
            <button type="button" onClick={resetForm} className="bg-gray-100 text-gray-700 px-6 py-2.5 rounded-full font-medium text-sm hover:bg-gray-200 transition-all">
              Cancel
            </button>
          </div>
        </form>
      ) : null}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-indigo-500">
          <svg className="animate-spin h-8 w-8 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <p className="text-sm font-medium animate-pulse">Loading destinations...</p>
        </div>
      ) : destinations.length === 0 ? (
        <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50">
          <p className="text-gray-500 font-medium">No destinations available. Adding some places will allow customers to choose them for trips.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 relative z-10">
          {destinations.map((dest) => (
            <div key={dest.id} className="group relative rounded-2xl overflow-hidden bg-white shadow-sm border border-gray-100 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.1)] transition-all duration-500 hover:-translate-y-1 flex flex-col">
              
              <div className="relative aspect-[4/3] overflow-hidden bg-gray-100 placeholder-image-wrapper">
                {dest.image_url ? (
                  <>
                    <img 
                      src={getImageUrl(dest.image_url)} 
                      className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-110" 
                      alt={dest.name} 
                      onError={(e) => { e.target.onerror = null; e.target.src = "https://placehold.co/600x400/f3f4f6/a1a1aa?text=No+Image"; }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-900/80 via-gray-900/20 to-transparent opacity-60 group-hover:opacity-80 transition-opacity duration-300"></div>
                  </>
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400">
                    <svg className="w-10 h-10 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                  </div>
                )}
                
                {/* Overlay Badges */}
                <div className="absolute top-3 right-3 flex flex-col items-end gap-2">
                  <span className="bg-white/90 backdrop-blur pb-[1px] px-2.5 py-1 rounded-full text-[10px] uppercase tracking-wider font-bold text-indigo-700 shadow-sm border border-white/50">
                    {dest.state || 'Global'}
                  </span>
                </div>
                
                {/* Floating Title over image */}
                <div className="absolute bottom-3 left-4 right-4 text-white transform transition-transform duration-300 translate-y-2 group-hover:translate-y-0">
                  <h4 className="font-bold text-lg leading-tight truncate">{dest.name}</h4>
                </div>
              </div>

              <div className="p-4 flex-1 flex flex-col bg-white">
                <p className="text-sm text-gray-500 line-clamp-3 mb-4 flex-1 text-pretty group-hover:text-gray-700 transition-colors">
                  {dest.description || <span className="italic opacity-50">No description provided</span>}
                </p>
                
                <div className="flex justify-between items-center pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-1.5 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                     {/* Tags purely for design */}
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                    <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">Listed</span>
                  </div>
                  
                  <div className="flex gap-2">
                    <button 
                      onClick={(e) => { e.preventDefault(); handleEdit(dest); }} 
                      className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center hover:bg-indigo-600 hover:text-white transition-colors"
                      title="Edit"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                    </button>
                    <button 
                      onClick={(e) => { e.preventDefault(); handleDelete(dest.id); }} 
                      className="w-8 h-8 rounded-full bg-red-50 text-red-600 flex items-center justify-center hover:bg-red-600 hover:text-white transition-colors"
                      title="Delete"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminDestinations;
