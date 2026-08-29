import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import proposalApi from "../services/proposalApi";

export function useProposals(filters = {}) {
  return useQuery({
    queryKey: ["proposals", filters],
    queryFn: () => proposalApi.getProposals(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useProposalDetail(id) {
  return useQuery({
    queryKey: ["proposal", id],
    queryFn: () => proposalApi.getProposal(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => proposalApi.createProposal(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
}

export function useUpdateProposal(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => proposalApi.updateProposal(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposal", id] });
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
    },
  });
}

export function useDeleteProposal() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => proposalApi.deleteProposal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
    },
  });
}

export function useFinalizeProposal(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => proposalApi.finalizeProposal(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposal", id] });
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });
}
