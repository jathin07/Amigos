import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import vendorApi from "../services/vendorApi";

export function useVendors(params = {}) {
  return useQuery({
    queryKey: ["vendors", params],
    queryFn: () => vendorApi.getVendors(params),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useVendorTypes() {
  return useQuery({
    queryKey: ["lookups", "vendor-types"],
    queryFn: () => vendorApi.getVendorTypes(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => vendorApi.createVendor(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
    },
  });
}

export function useVerifyVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, verify }) => 
      verify ? vendorApi.verifyVendor(id) : vendorApi.unverifyVendor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vendors"] });
    },
  });
}
