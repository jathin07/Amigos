import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import organizationApi from "../services/organizationApi";

export function useOrganizations(filters = {}) {
  return useQuery({
    queryKey: ["organizations", filters],
    queryFn: () => organizationApi.getItems(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useOrganization(id) {
  return useQuery({
    queryKey: ["organization", id],
    queryFn: () => organizationApi.getItem(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => organizationApi.createItem(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      queryClient.invalidateQueries({ queryKey: ["organizations-lookup"] });
    },
  });
}

export function useUpdateOrganization(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => organizationApi.updateItem(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      queryClient.invalidateQueries({ queryKey: ["organization", id] });
      queryClient.invalidateQueries({ queryKey: ["organizations-lookup"] });
    },
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => organizationApi.deleteItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      queryClient.invalidateQueries({ queryKey: ["organizations-lookup"] });
    },
  });
}

export function useOrganizationTypes() {
  return useQuery({
    queryKey: ["lookups", "organization-types"],
    queryFn: () => organizationApi.getOrganizationTypes(),
    staleTime: 30 * 60 * 1000,
  });
}

export function useOrganizationsLookup() {
  return useQuery({
    queryKey: ["organizations-lookup"],
    queryFn: () => organizationApi.getOrganizationsLookup(),
    staleTime: 5 * 60 * 1000,
  });
}
