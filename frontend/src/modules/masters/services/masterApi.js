import { axiosClient } from "../../../api/axiosClient";

export const masterApi = {
  // Fetch paginated master records for any master entity slug
  getItems: async (entitySlug, params) => {
    const response = await axiosClient.get(`/masters/${entitySlug}`, { params });
    return response.data; // Envelope: { success: true, data: { items: [...], pagination: {...} } }
  },

  // Retrieve single master record details
  getItem: async (entitySlug, id) => {
    const response = await axiosClient.get(`/masters/${entitySlug}/${id}`);
    return response.data;
  },

  // Create new master record
  createItem: async (entitySlug, payload) => {
    const response = await axiosClient.post(`/masters/${entitySlug}`, payload);
    return response.data;
  },

  // Update existing master record
  updateItem: async (entitySlug, id, payload) => {
    const response = await axiosClient.put(`/masters/${entitySlug}/${id}`, payload);
    return response.data;
  },

  // Soft delete / deactivate master record
  deleteItem: async (entitySlug, id) => {
    const response = await axiosClient.delete(`/masters/${entitySlug}/${id}`);
    return response.data;
  },
};

export default masterApi;
