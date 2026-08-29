import { axiosClient } from "../../../api/axiosClient";

export const crmApi = {
  // Leads Listing (supports paginated, sorted, filtered parameters)
  getLeads: async (params) => {
    const { search, q, status_id, current_status_id, priority_id, owner_id, owner_team_member_id, ...rest } = params || {};
    const apiParams = {
      ...rest,
      q: search || q || undefined,
      current_status_id: current_status_id || status_id || undefined,
      priority_id: priority_id || undefined,
      owner_team_member_id: owner_team_member_id || owner_id || undefined,
    };
    const response = await axiosClient.get("/leads", { params: apiParams });
    return response.data; // Paginated envelope: { success, data, meta }
  },

  // Create Lead
  createLead: async (payload) => {
    const response = await axiosClient.post("/leads", payload);
    return response.data;
  },

  // Retrieve Lead Details
  getLeadDetail: async (id) => {
    const response = await axiosClient.get(`/leads/${id}`);
    return response.data;
  },

  // Update Lead
  updateLead: async (id, payload) => {
    const response = await axiosClient.put(`/leads/${id}`, payload);
    return response.data;
  },

  // Soft Delete Lead
  deleteLead: async (id) => {
    const response = await axiosClient.delete(`/leads/${id}`);
    return response.data;
  },

  // List Activities logged for a lead
  getActivities: async (id) => {
    const response = await axiosClient.get(`/leads/${id}/activities`);
    return response.data;
  },

  // Log a new activity
  createActivity: async (id, payload) => {
    const response = await axiosClient.post(`/leads/${id}/activities`, payload);
    return response.data;
  },

  // List followups scheduled for a lead
  getFollowups: async (id) => {
    const response = await axiosClient.get(`/leads/${id}/followups`);
    return response.data;
  },

  // Schedule a followup
  createFollowup: async (id, payload) => {
    const response = await axiosClient.post(`/leads/${id}/followups`, payload);
    return response.data;
  },

  // Complete a followup
  completeFollowup: async (leadId, followupId, payload) => {
    const response = await axiosClient.put(`/leads/${leadId}/followups/${followupId}/complete`, payload);
    return response.data;
  },

  // Convert Lead to Booking
  convertLead: async (id, payload) => {
    const response = await axiosClient.post(`/leads/${id}/convert`, payload);
    return response.data;
  },

  // Customer contacts directory
  getCustomers: async (params) => {
    const response = await axiosClient.get("/crm/contacts", { params });
    return response.data;
  },

  // Lookup tables (statuses, sources, priorities, lost_reasons, activity_types, followup_types)
  getLookups: async (type) => {
    const response = await axiosClient.get(`/crm/lookups/${type}`);
    return response.data;
  },
  
  // Package list from master catalog
  getPackages: async () => {
    const response = await axiosClient.get("/packages", { params: { page_size: 100 } });
    return response.data;
  },

  // Team members list for owner assignments
  getTeamMembers: async () => {
    const response = await axiosClient.get("/team-members", { params: { page_size: 100 } });
    return response.data;
  },

  // Destinations list lookup from master database
  getDestinations: async () => {
    const response = await axiosClient.get("/masters/destinations/lookup");
    return response.data;
  },

  // Create new Destination in master DB
  createDestination: async (name) => {
    const response = await axiosClient.post("/masters/destinations", { name });
    return response.data;
  },

  // Trip types list
  getTripTypes: async () => {
    const response = await axiosClient.get("/crm/lookups/trip_types");
    return response.data;
  }
};

export default crmApi;
