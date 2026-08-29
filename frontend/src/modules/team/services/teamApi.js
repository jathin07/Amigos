import { axiosClient } from "../../../api/axiosClient";

export const teamApi = {
  // List team members (paginated, filtered, sortable)
  getTeamMembers: async (params) => {
    const response = await axiosClient.get("/team-members", { params });
    return response.data; // Envelope: { success: true, data: { items: [...], pagination: {...} } }
  },

  // Retrieve team member details
  getTeamMember: async (id) => {
    const response = await axiosClient.get(`/team-members/${id}`);
    return response.data;
  },

  // Create new team member
  createTeamMember: async (payload) => {
    const response = await axiosClient.post("/team-members", payload);
    return response.data;
  },

  // Update team member details
  updateTeamMember: async (id, payload) => {
    const response = await axiosClient.put(`/team-members/${id}`, payload);
    return response.data;
  },

  // Soft delete / deactivate team member
  deleteTeamMember: async (id) => {
    const response = await axiosClient.delete(`/team-members/${id}`);
    return response.data;
  },
};

export default teamApi;
