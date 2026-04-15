import { useEffect, useState } from 'react';
import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';

const AdminStaff = () => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Form State
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    name: '',
    role: '',
    phone: '',
    active: true
  });

  const loadData = async () => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    setLoading(true);
    setError('');

    try {
      const data = await apiFetch('/admin/team-members', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMembers(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load staff data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const resetForm = () => {
    setFormData({
      id: null, name: '', role: '', phone: '', active: true
    });
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (member) => {
    setFormData(member);
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this staff member?')) return;
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/team-members/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      setMembers(members.filter(m => m.id !== id));
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      if (isEditing) {
        await apiFetch(`/admin/team-members/${formData.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        });
      } else {
        await apiFetch(`/admin/team-members`, {
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
            Staff Management
          </h2>
          <p className="text-sm text-gray-500 mt-1">Manage team members ({members.length})</p>
        </div>
        <button 
          onClick={() => { resetForm(); setShowForm(true); }}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-indigo-500/30 hover:-translate-y-0.5 transition-all duration-300"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
          Add Staff Member
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
          <h3 className="text-lg font-bold text-gray-800 mb-6">{isEditing ? 'Edit Staff details' : 'Create new Staff Member'}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Name</label>
              <input required name="name" value={formData.name} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white" placeholder="Name" />
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Role</label>
              <select name="role" value={formData.role} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white">
                <option value="">Select a role</option>
                <option value="Founder">Founder</option>
                <option value="Organiser">Organiser</option>
                <option value="Freelancer">Freelancer</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold tracking-wide text-gray-500 uppercase mb-2">Phone</label>
              <input name="phone" value={formData.phone} onChange={handleInputChange} className="block w-full bg-gray-50/50 border border-gray-200 rounded-xl text-gray-800 text-sm p-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all focus:bg-white" placeholder="Phone Number" />
            </div>
            <div className="flex items-center mt-6">
              <input type="checkbox" name="active" checked={formData.active} onChange={handleInputChange} className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" />
              <label className="ml-2 text-sm font-medium text-gray-700">Active Member</label>
            </div>
          </div>
          <div className="mt-8 flex gap-3">
            <button type="submit" className="bg-indigo-600 text-white px-6 py-2.5 rounded-full shadow-md font-medium text-sm hover:bg-indigo-700 hover:shadow-lg transition-all focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
              Save Staff Member
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
          <p className="text-sm font-medium animate-pulse">Loading staff members...</p>
        </div>
      ) : members.length === 0 ? (
        <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-gray-200 bg-gray-50/50">
          <p className="text-gray-500 font-medium">No staff members available.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-100 shadow-sm">
          <table className="w-full text-left border-collapse bg-white">
            <thead>
              <tr className="bg-gray-50/80 border-b-2 border-gray-100 text-xs uppercase tracking-wider text-gray-500">
                <th className="py-4 px-5 font-bold">Name</th>
                <th className="py-4 px-5 font-bold">Role</th>
                <th className="py-4 px-5 font-bold">Phone</th>
                <th className="py-4 px-5 font-bold">Status</th>
                <th className="py-4 px-5 font-bold">Actions</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-gray-50">
              {members.map((member) => (
                <tr key={member.id} className="hover:bg-indigo-50/30 transition-colors">
                  <td className="py-4 px-5 font-extrabold text-gray-900">{member.name}</td>
                  <td className="py-4 px-5 text-gray-600">{member.role}</td>
                  <td className="py-4 px-5 text-gray-600">{member.phone}</td>
                  <td className="py-4 px-5">
                    <span className={`inline-flex px-2py-1 text-xs font-bold uppercase rounded-full ${member.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {member.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="py-4 px-5">
                    <div className="flex gap-2">
                      <button onClick={() => handleEdit(member)} className="text-indigo-600 hover:text-indigo-900 font-bold text-xs uppercase">Edit</button>
                      <button onClick={() => handleDelete(member.id)} className="text-red-600 hover:text-red-900 font-bold text-xs uppercase">Delete</button>
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

export default AdminStaff;
