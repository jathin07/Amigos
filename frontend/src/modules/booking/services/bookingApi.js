import { axiosClient } from "../../../api/axiosClient";

export const bookingApi = {
  // Fetch paginated bookings
  getBookings: async (params = {}) => {
    const { search, status, page_size, ...rest } = params;
    const mappedParams = {
      ...rest,
      q: search || undefined,
      booking_status_id: status || undefined,
      limit: page_size || undefined,
    };
    const response = await axiosClient.get("/bookings", { params: mappedParams });
    return response.data; // Envelope: { success: true, data: { items: [...], pagination: {...} } }
  },

  // Get single booking details
  getBooking: async (id) => {
    const response = await axiosClient.get(`/bookings/${id}`);
    return response.data;
  },

  // Create booking
  createBooking: async (payload) => {
    const response = await axiosClient.post("/bookings", payload);
    return response.data;
  },

  // Update booking (e.g. group_name, internal_notes)
  updateBooking: async (id, payload) => {
    const response = await axiosClient.put(`/bookings/${id}`, payload);
    return response.data;
  },

  // Confirm booking (payload: { row_version, trip_coordinator_team_member_id, notes })
  confirmBooking: async (id, payload) => {
    const response = await axiosClient.post(`/bookings/${id}/confirm`, payload);
    return response.data;
  },

  // Cancel booking (payload: { row_version, cancellation_reason })
  cancelBooking: async (id, payload) => {
    const response = await axiosClient.post(`/bookings/${id}/cancel`, payload);
    return response.data;
  },

  // List travelers
  getTravelers: async (bookingId) => {
    const response = await axiosClient.get(`/bookings/${bookingId}/travelers`);
    return response.data;
  },

  // Add traveler
  addTraveler: async (bookingId, payload) => {
    const response = await axiosClient.post(`/bookings/${bookingId}/travelers`, payload);
    return response.data;
  },

  // Update traveler
  updateTraveler: async (bookingId, travelerId, payload) => {
    const response = await axiosClient.put(`/bookings/${bookingId}/travelers/${travelerId}`, payload);
    return response.data;
  },

  // Delete traveler
  deleteTraveler: async (bookingId, travelerId) => {
    const response = await axiosClient.delete(`/bookings/${bookingId}/travelers/${travelerId}`);
    return response.data;
  },

  // List documents
  getDocuments: async (bookingId) => {
    const response = await axiosClient.get(`/bookings/${bookingId}/documents`);
    return response.data;
  },

  // Add document (payload: { file_name, file_url, document_type_id })
  addDocument: async (bookingId, payload) => {
    const response = await axiosClient.post(`/bookings/${bookingId}/documents`, payload);
    return response.data;
  },

  // Delete document
  deleteDocument: async (bookingId, documentId) => {
    const response = await axiosClient.delete(`/bookings/${bookingId}/documents/${documentId}`);
    return response.data;
  },

  // Fetch timeline audit history
  getTimeline: async (bookingId) => {
    const response = await axiosClient.get(`/bookings/${bookingId}/timeline`);
    return response.data;
  },

  // Lookup booking statuses
  getStatuses: async () => {
    const response = await axiosClient.get("/lookups/booking-statuses");
    return response.data;
  },

  // Update status (payload: { status_code, notes })
  updateStatus: async (id, payload) => {
    const response = await axiosClient.post(`/bookings/${id}/status`, payload);
    return response.data;
  },
};

export default bookingApi;

