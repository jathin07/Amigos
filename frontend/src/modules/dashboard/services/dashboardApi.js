import { axiosClient } from "../../../api/axiosClient";

export const dashboardApi = {
  /**
   * Fetch business KPI summary statistics.
   */
  getSummaryCards: async () => {
    const response = await axiosClient.get("/dashboard/widgets/summary-cards");
    return response.data;
  },

  /**
   * Fetch CRM lead conversion pipeline funnel.
   */
  getLeadPipeline: async () => {
    const response = await axiosClient.get("/dashboard/widgets/lead-pipeline");
    return response.data;
  },

  /**
   * Fetch booking lifecycle distribution metrics.
   */
  getBookingPipeline: async () => {
    const response = await axiosClient.get("/dashboard/widgets/booking-pipeline");
    return response.data;
  },

  /**
   * Fetch finance summary stats (revenue, expenses, profits).
   */
  getFinanceSummary: async () => {
    const response = await axiosClient.get("/dashboard/widgets/finance-summary");
    return response.data;
  },

  /**
   * Fetch upcoming trips with pagination support.
   */
  getUpcomingTrips: async (page = 1, pageSize = 10) => {
    const response = await axiosClient.get("/dashboard/widgets/upcoming-trips", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  /**
   * Fetch operations workload and allocation metrics.
   */
  getOperationsOverview: async () => {
    const response = await axiosClient.get("/dashboard/widgets/operations-overview");
    return response.data;
  },

  /**
   * Fetch monthly revenue analytical trends.
   */
  getRevenueTrend: async () => {
    const response = await axiosClient.get("/dashboard/widgets/revenue-trend");
    return response.data;
  }
};
export default dashboardApi;
