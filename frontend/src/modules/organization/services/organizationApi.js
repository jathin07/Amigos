import { axiosClient } from "../../../api/axiosClient";

export const organizationApi = {
  // Fetch paginated organization records
  getItems: async (params) => {
    const response = await axiosClient.get("/organization", { params });
    return response.data; // Envelope: { success: true, data: { items: [...], pagination: {...} } }
  },

  // Retrieve single organization details
  getItem: async (id) => {
    const response = await axiosClient.get(`/organization/${id}`);
    return response.data;
  },

  // Create new organization
  createItem: async (payload) => {
    const response = await axiosClient.post("/organization", payload);
    return response.data;
  },

  // Update existing organization
  updateItem: async (id, payload) => {
    const response = await axiosClient.put(`/organization/${id}`, payload);
    return response.data;
  },

  // Soft delete organization
  deleteItem: async (id) => {
    const response = await axiosClient.delete(`/organization/${id}`);
    return response.data;
  },

  // Lookup organization types list
  getOrganizationTypes: async () => {
    const response = await axiosClient.get("/masters/organization-types/lookup");
    return response.data; // Envelope: { success: true, data: [...] }
  },

  // Lookup all organizations list for dropdowns
  getOrganizationsLookup: async () => {
    const response = await axiosClient.get("/organization/lookup");
    return response.data; // Envelope: { success: true, data: [...] }
  }
};

export default organizationApi;
