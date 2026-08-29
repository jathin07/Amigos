import { axiosClient } from "../../../api/axiosClient";

export const reportsApi = {
  // Get financial profitability report
  getFinanceReport: async (params) => {
    const response = await axiosClient.get("/reports/finance", { params });
    return response.data; // Envelope: { success, data: {...} }
  },

  // Get CRM / Leads conversion report
  getCrmReport: async (params) => {
    const response = await axiosClient.get("/reports/crm", { params });
    return response.data;
  },

  // Get Booking reports
  getBookingReport: async (params) => {
    const response = await axiosClient.get("/reports/bookings", { params });
    return response.data;
  },

  // Get Operations reports
  getOperationsReport: async (params) => {
    const response = await axiosClient.get("/reports/operations", { params });
    return response.data;
  },

  // Get Vendor disbursements reports
  getVendorReport: async (params) => {
    const response = await axiosClient.get("/reports/vendor-payments", { params });
    return response.data;
  }
};

export default reportsApi;
