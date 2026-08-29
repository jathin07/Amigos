import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import masterApi from "../services/masterApi";

export function useMasterItems(entitySlug, filters = {}) {
  return useQuery({
    queryKey: ["master-items", entitySlug, filters],
    queryFn: () => masterApi.getItems(entitySlug, filters),
    enabled: !!entitySlug,
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useMasterItem(entitySlug, id) {
  return useQuery({
    queryKey: ["master-item", entitySlug, id],
    queryFn: () => masterApi.getItem(entitySlug, id),
    enabled: !!entitySlug && !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateMasterItem(entitySlug) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => masterApi.createItem(entitySlug, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["master-items", entitySlug] });
    },
  });
}

export function useUpdateMasterItem(entitySlug, id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => masterApi.updateItem(entitySlug, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["master-items", entitySlug] });
      queryClient.invalidateQueries({ queryKey: ["master-item", entitySlug, id] });
    },
  });
}

export function useDeleteMasterItem(entitySlug) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => masterApi.deleteItem(entitySlug, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["master-items", entitySlug] });
    },
  });
}
