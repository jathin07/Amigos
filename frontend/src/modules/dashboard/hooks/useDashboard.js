import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../services/dashboardApi";
import { useAuth } from "../../auth";

/**
 * Hook to retrieve Summary KPI cards.
 * Auto-refreshes every 30 seconds.
 */
export function useSummaryCards() {
  return useQuery({
    queryKey: ["dashboard", "summary-cards"],
    queryFn: () => dashboardApi.getSummaryCards(),
    refetchInterval: 30 * 1000,
    staleTime: 25 * 1000,
  });
}

/**
 * Hook to retrieve CRM Lead Funnel.
 * Auto-refreshes every 30 seconds.
 */
export function useLeadPipeline() {
  return useQuery({
    queryKey: ["dashboard", "lead-pipeline"],
    queryFn: () => dashboardApi.getLeadPipeline(),
    refetchInterval: 30 * 1000,
    staleTime: 25 * 1000,
  });
}

/**
 * Hook to retrieve Booking Pipeline distribution.
 * Auto-refreshes every 30 seconds.
 */
export function useBookingPipeline() {
  return useQuery({
    queryKey: ["dashboard", "booking-pipeline"],
    queryFn: () => dashboardApi.getBookingPipeline(),
    refetchInterval: 30 * 1000,
    staleTime: 25 * 1000,
  });
}

/**
 * Hook to retrieve Finance Summary metrics.
 * Auto-refreshes every 60 seconds.
 * Scoped check: only executes request if user possesses finance.read permission.
 */
export function useFinanceSummary() {
  const { hasPermission } = useAuth();
  const hasFinanceRead = hasPermission("finance.read");

  return useQuery({
    queryKey: ["dashboard", "finance-summary"],
    queryFn: () => dashboardApi.getFinanceSummary(),
    enabled: hasFinanceRead,
    refetchInterval: 60 * 1000,
    staleTime: 55 * 1000,
  });
}

/**
 * Hook to retrieve Upcoming Trips list with pagination.
 * Auto-refreshes every 60 seconds.
 */
export function useUpcomingTrips(page = 1, pageSize = 5) {
  return useQuery({
    queryKey: ["dashboard", "upcoming-trips", { page, pageSize }],
    queryFn: () => dashboardApi.getUpcomingTrips(page, pageSize),
    refetchInterval: 60 * 1000,
    staleTime: 55 * 1000,
  });
}

/**
 * Hook to retrieve Operations Overview workloads.
 * Auto-refreshes every 60 seconds.
 */
export function useOperationsOverview() {
  return useQuery({
    queryKey: ["dashboard", "operations-overview"],
    queryFn: () => dashboardApi.getOperationsOverview(),
    refetchInterval: 60 * 1000,
    staleTime: 55 * 1000,
  });
}

/**
 * Hook to retrieve Monthly Revenue trends.
 * Stale time is longer (5 minutes) as historical trends change rarely.
 */
export function useRevenueTrend() {
  const { hasPermission } = useAuth();
  const hasFinanceRead = hasPermission("finance.read");

  return useQuery({
    queryKey: ["dashboard", "revenue-trend"],
    queryFn: () => dashboardApi.getRevenueTrend(),
    enabled: hasFinanceRead,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}
