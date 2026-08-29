import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import bookingApi from "../services/bookingApi";

export function useBookings(filters = {}) {
  return useQuery({
    queryKey: ["bookings", filters],
    queryFn: () => bookingApi.getBookings(filters),
    placeholderData: (previousData) => previousData,
    staleTime: 30 * 1000,
  });
}

export function useBookingDetail(id) {
  return useQuery({
    queryKey: ["booking", id],
    queryFn: () => bookingApi.getBooking(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useConfirmBooking(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => bookingApi.confirmBooking(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking", id] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });
}

export function useCancelBooking(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => bookingApi.cancelBooking(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking", id] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });
}

export function useUpdateBooking(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => bookingApi.updateBooking(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking", id] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
    },
  });
}

export function useUpdateBookingStatus(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => bookingApi.updateStatus(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking", id] });
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["booking-timeline", id] });
    },
  });
}

export function useBookingTravelers(bookingId) {
  return useQuery({
    queryKey: ["booking-travelers", bookingId],
    queryFn: () => bookingApi.getTravelers(bookingId),
    enabled: !!bookingId,
  });
}

export function useAddTraveler(bookingId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => bookingApi.addTraveler(bookingId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking-travelers", bookingId] });
      queryClient.invalidateQueries({ queryKey: ["booking", bookingId] });
    },
  });
}

export function useUpdateTraveler(bookingId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ travelerId, ...payload }) => bookingApi.updateTraveler(bookingId, travelerId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking-travelers", bookingId] });
      queryClient.invalidateQueries({ queryKey: ["booking", bookingId] });
    },
  });
}

export function useDeleteTraveler(bookingId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (travelerId) => bookingApi.deleteTraveler(bookingId, travelerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking-travelers", bookingId] });
      queryClient.invalidateQueries({ queryKey: ["booking", bookingId] });
    },
  });
}

export function useBookingTimeline(id) {
  return useQuery({
    queryKey: ["booking-timeline", id],
    queryFn: () => bookingApi.getTimeline(id),
    enabled: !!id,
  });
}

export function useBookingDocuments(bookingId) {
  return useQuery({
    queryKey: ["booking-documents", bookingId],
    queryFn: () => bookingApi.getDocuments(bookingId),
    enabled: !!bookingId,
  });
}

export function useAddDocument(bookingId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => bookingApi.addDocument(bookingId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking-documents", bookingId] });
      queryClient.invalidateQueries({ queryKey: ["booking", bookingId] });
    },
  });
}

export function useDeleteDocument(bookingId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId) => bookingApi.deleteDocument(bookingId, documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking-documents", bookingId] });
      queryClient.invalidateQueries({ queryKey: ["booking", bookingId] });
    },
  });
}

