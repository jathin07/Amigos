import { useEffect, useState } from 'react';
import { apiFetch } from '../config/api';
import { ADMIN_TOKEN_KEY } from './AdminLogin';

const AdminTasks = () => {
  const [tasks, setTasks] = useState([]);
  const [leads, setLeads] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    description: '',
    assigned_to_id: '',
    linked_lead_id: '',
    due_date: '',
    status: 'pending'
  });

  const loadData = async () => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    setLoading(true);
    setError('');

    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [tasksData, leadsData, staffData] = await Promise.all([
        apiFetch('/admin/tasks', { headers }),
        apiFetch('/admin/leads', { headers }),
        apiFetch('/admin/team-members', { headers })
      ]);
      
      setTasks(tasksData || []);
      setLeads(leadsData || []);
      setTeamMembers(staffData || []);
    } catch (err) {
      setError(err.message || 'Failed to load task data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      const method = formData.id ? 'PUT' : 'POST';
      const url = formData.id ? `/admin/tasks/${formData.id}` : '/admin/tasks';
      
      await apiFetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          assigned_to_id: formData.assigned_to_id ? parseInt(formData.assigned_to_id) : null,
          linked_lead_id: formData.linked_lead_id ? parseInt(formData.linked_lead_id) : null,
        }),
      });
      
      setShowForm(false);
      setFormData({ id: null, description: '', assigned_to_id: '', linked_lead_id: '', due_date: '', status: 'pending' });
      loadData();
    } catch (err) {
      alert('Save failed: ' + err.message);
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    const token = localStorage.getItem(ADMIN_TOKEN_KEY);
    try {
      await apiFetch(`/admin/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });
      loadData();
    } catch (err) {
      alert('Update failed: ' + err.message);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8 relative">
      <div className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent">
            Task Management
          </h2>
          <p className="text-sm text-gray-500 mt-1">Operational tasks for the team</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-indigo-700 transition-all"
        >
          {showForm ? 'Cancel' : 'Add New Task'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-10 bg-gray-50 p-6 rounded-2xl border border-gray-100 animate-fade-in-up">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Task Description</label>
              <textarea required name="description" value={formData.description} onChange={handleInputChange} className="block w-full border border-gray-200 rounded-xl p-3 text-sm" placeholder="e.g. Book hotel for Aditya Verma" rows="2" />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Assign To</label>
              <select name="assigned_to_id" value={formData.assigned_to_id} onChange={handleInputChange} className="block w-full border border-gray-200 rounded-xl p-3 text-sm">
                <option value="">Select Staff</option>
                {teamMembers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Linked Lead (Optional)</label>
              <select name="linked_lead_id" value={formData.linked_lead_id} onChange={handleInputChange} className="block w-full border border-gray-200 rounded-xl p-3 text-sm">
                <option value="">None</option>
                {leads.map(l => <option key={l.id} value={l.id}>{l.name} (#{l.id})</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase mb-2">Due Date</label>
              <input type="date" name="due_date" value={formData.due_date} onChange={handleInputChange} className="block w-full border border-gray-200 rounded-xl p-3 text-sm" />
            </div>
          </div>
          <button type="submit" className="mt-6 bg-indigo-600 text-white px-8 py-2.5 rounded-full text-sm font-bold">
            {formData.id ? 'Update Task' : 'Create Task'}
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-center py-10">Loading tasks...</p>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {tasks.map(task => (
            <div key={task.id} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 bg-white border border-gray-100 rounded-2xl hover:shadow-md transition-all group">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`w-2 h-2 rounded-full ${task.status === 'completed' ? 'bg-green-500' : 'bg-amber-500'}`}></span>
                  <p className={`font-bold text-sm ${task.status === 'completed' ? 'text-gray-400 line-through' : 'text-gray-800'}`}>
                    {task.description}
                  </p>
                </div>
                <div className="flex flex-wrap gap-4 text-[11px] font-medium text-gray-500">
                  <span className="flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                    {teamMembers.find(m => m.id === task.assigned_to_id)?.name || 'Unassigned'}
                  </span>
                  {task.linked_lead_id && (
                    <span className="flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.206"></path></svg>
                      Lead: {leads.find(l => l.id === task.linked_lead_id)?.name || '#' + task.linked_lead_id}
                    </span>
                  )}
                  {task.due_date && (
                    <span className="flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-3 sm:mt-0 flex gap-2">
                <select 
                  value={task.status} 
                  onChange={(e) => handleStatusChange(task.id, e.target.value)}
                  className={`text-[10px] font-bold uppercase tracking-wider rounded-lg border px-2 py-1 ${
                    task.status === 'completed' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'
                  }`}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
                <button 
                  onClick={() => { setFormData(task); setShowForm(true); }}
                  className="p-1.5 text-gray-400 hover:text-indigo-600 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                </button>
              </div>
            </div>
          ))}
          {tasks.length === 0 && <p className="text-center py-10 text-gray-400">No tasks found.</p>}
        </div>
      )}
    </div>
  );
};

export default AdminTasks;
