import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import crmApi from "../services/crmApi";

export function useLeadDetail(id) {
  return useQuery({
    queryKey: ["lead", id],
    queryFn: () => crmApi.getLeadDetail(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // Cache detail for 5 minutes
  });
}

export function useUpdateLead(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => crmApi.updateLead(id, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["lead", id] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
}

export function useDeleteLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => crmApi.deleteLead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
}

export function useConvertLead(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => crmApi.convertLead(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lead", id] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
