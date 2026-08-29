import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import teamApi from "../services/teamApi";

export function useTeamMembers(filters = {}) {
  return useQuery({
    queryKey: ["team-members", filters],
    queryFn: () => teamApi.getTeamMembers(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useTeamMemberDetail(id) {
  return useQuery({
    queryKey: ["team-member", id],
    queryFn: () => teamApi.getTeamMember(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateTeamMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => teamApi.createTeamMember(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
    },
  });
}

export function useUpdateTeamMember(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => teamApi.updateTeamMember(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
      queryClient.invalidateQueries({ queryKey: ["team-member", id] });
    },
  });
}

export function useDeleteTeamMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => teamApi.deleteTeamMember(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["team-members"] });
    },
  });
}
