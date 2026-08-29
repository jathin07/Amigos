import { axiosClient } from "../../../api/axiosClient";

export const financeApi = {
  // Get list of bookings with outstanding balances
  getOutstandingPayments: async (params) => {
    const response = await axiosClient.get("/finance/outstanding-payments", { params });
    return response.data; // Envelope: { success, data: [...], meta: { total, page, per_page } }
  },

  // Get upcoming customer scheduled installments
  getUpcomingInstallments: async () => {
    const response = await axiosClient.get("/finance/upcoming-installments");
    return response.data; // Envelope: { success, data: [...] }
  },

  // Get list of pending vendor payouts
  getPendingVendorPayments: async () => {
    const response = await axiosClient.get("/finance/pending-vendor-payments");
    return response.data; // Envelope: { success, data: [...] }
  },

  // Record a customer payment receipt
  recordCustomerPayment: async (payload) => {
    const response = await axiosClient.post("/finance/payments", payload);
    return response.data;
  },

  // Record a vendor allocation payment payout
  recordVendorPayment: async (payload) => {
    const response = await axiosClient.post("/finance/vendor-payments", payload);
    return response.data;
  },

  // Lookup payment methods
  getPaymentMethods: async () => {
    const response = await axiosClient.get("/masters/payment-methods/lookup");
    return response.data; // Envelope: { success, data: [...] }
  },

  // Lookup payment types (Advance, Partial, Final)
  getPaymentTypes: async () => {
    const response = await axiosClient.get("/masters/payment-types/lookup");
    return response.data; // Envelope: { success, data: [...] }
  }
};

export default financeApi;
