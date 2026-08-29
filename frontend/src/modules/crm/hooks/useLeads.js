import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import crmApi from "../services/crmApi";

export function useLeads(filters = {}) {
  return useQuery({
    queryKey: ["leads", filters],
    queryFn: () => crmApi.getLeads(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000, // 30 seconds stale time for operational lead lists
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => crmApi.createLead(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
}

export function useCustomers(filters = {}) {
  return useQuery({
    queryKey: ["customers", filters],
    queryFn: () => crmApi.getCustomers(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 60 * 1000,
  });
}
