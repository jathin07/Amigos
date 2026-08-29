import { axiosClient } from "../../../api/axiosClient";

export const proposalApi = {
  // List proposals (paginated, filtered, sortable)
  getProposals: async (params) => {
    const response = await axiosClient.get("/proposals", { params });
    return response.data; // Envelope: { success, data: [...], meta: {...} }
  },

  // Create new proposal
  createProposal: async (payload) => {
    const response = await axiosClient.post("/proposals", payload);
    return response.data;
  },

  // Retrieve proposal detail
  getProposal: async (id) => {
    const response = await axiosClient.get(`/proposals/${id}`);
    return response.data;
  },

  // Update proposal properties
  updateProposal: async (id, payload) => {
    const response = await axiosClient.put(`/proposals/${id}`, payload);
    return response.data;
  },

  // Soft delete proposal
  deleteProposal: async (id) => {
    const response = await axiosClient.delete(`/proposals/${id}`);
    return response.data;
  },

  // Retrieve all version/revisions of proposals linked to a specific CRM lead
  getProposalVersions: async (leadId) => {
    const response = await axiosClient.get(`/leads/${leadId}/proposals`);
    return response.data;
  },

  // Finalize/freeze proposal as customer ready
  finalizeProposal: async (id, payload) => {
    const response = await axiosClient.post(`/proposals/${id}/finalize`, payload);
    return response.data;
  },

  // List proposal statuses lookups
  getProposalStatuses: async () => {
    const response = await axiosClient.get("/crm/lookups/proposal_statuses");
    return response.data;
  },

  // Fetch team members list for assignments
  getTeamMembers: async () => {
    const response = await axiosClient.get("/team-members");
    return response.data;
  },

  // Fetch package list from catalog for proposal templates
  getPackages: async () => {
    const response = await axiosClient.get("/packages");
    return response.data;
  },

  // Fetch destinations list from catalog for itinerary days
  getDestinations: async () => {
    const response = await axiosClient.get("/masters/destinations/lookup", { params: { page_size: 200 } });
    return response.data;
  }
};

export default proposalApi;
