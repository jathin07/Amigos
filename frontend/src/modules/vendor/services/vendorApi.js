import { axiosClient } from "../../../api/axiosClient";

export const vendorApi = {
  // Get list of vendors with pagination and optional search
  getVendors: async (params) => {
    const response = await axiosClient.get("/vendors", { params });
    return response.data; // Envelope: { success, data: { items: [...], pagination: {...} } }
  },

  // Get details of a single vendor
  getVendorDetail: async (id) => {
    const response = await axiosClient.get(`/vendors/${id}`);
    return response.data;
  },

  // Create a new vendor
  createVendor: async (payload) => {
    const response = await axiosClient.post("/vendors", payload);
    return response.data;
  },

  // Update a vendor record
  updateVendor: async (id, payload) => {
    const response = await axiosClient.put(`/vendors/${id}`, payload);
    return response.data;
  },

  // Delete a vendor (deactivate)
  deleteVendor: async (id) => {
    const response = await axiosClient.delete(`/vendors/${id}`);
    return response.data;
  },

  // Verify vendor
  verifyVendor: async (id) => {
    const response = await axiosClient.post(`/vendors/${id}/verify`);
    return response.data;
  },

  // Unverify vendor
  unverifyVendor: async (id) => {
    const response = await axiosClient.post(`/vendors/${id}/unverify`);
    return response.data;
  },

  // Lookup vendor types (Accommodation, Transport, etc.)
  getVendorTypes: async () => {
    const response = await axiosClient.get("/masters/vendor-types/lookup");
    return response.data; // Envelope: { success, data: [...] }
  }
};

export default vendorApi;
