import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import crmApi from "../services/crmApi";

export function useActivities(leadId) {
  return useQuery({
    queryKey: ["activities", leadId],
    queryFn: () => crmApi.getActivities(leadId),
    enabled: !!leadId,
  });
}

export function useCreateActivity(leadId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => crmApi.createActivity(leadId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["activities", leadId] });
      queryClient.invalidateQueries({ queryKey: ["lead", leadId] }); // Refresh lead in case status updated
    },
  });
}
