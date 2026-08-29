import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import financeApi from "../services/financeApi";

export function useOutstandingPayments(params = {}) {
  return useQuery({
    queryKey: ["finance", "outstanding", params],
    queryFn: () => financeApi.getOutstandingPayments(params),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useUpcomingInstallments() {
  return useQuery({
    queryKey: ["finance", "installments"],
    queryFn: () => financeApi.getUpcomingInstallments(),
    staleTime: 60 * 1000,
  });
}

export function usePendingVendorPayments() {
  return useQuery({
    queryKey: ["finance", "vendor-payouts"],
    queryFn: () => financeApi.getPendingVendorPayments(),
    staleTime: 60 * 1000,
  });
}

export function useRecordCustomerPayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => financeApi.recordCustomerPayment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["finance"] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });
}

export function useRecordVendorPayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => financeApi.recordVendorPayment(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["finance"] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });
}
