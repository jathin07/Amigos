import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import crmApi from "../services/crmApi";

export function useFollowups(leadId) {
  return useQuery({
    queryKey: ["followups", leadId],
    queryFn: () => crmApi.getFollowups(leadId),
    enabled: !!leadId,
  });
}

export function useCreateFollowup(leadId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => crmApi.createFollowup(leadId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["followups", leadId] });
    },
  });
}

export function useCompleteFollowup(leadId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ followupId, payload }) => crmApi.completeFollowup(leadId, followupId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["followups", leadId] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
