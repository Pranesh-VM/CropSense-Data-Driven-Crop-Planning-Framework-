import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { rindmService, handleApiError } from '../services/api';

// Fetch active cycle
export const useActiveCycle = () => {
  return useQuery({
    queryKey: ['activeCycle'],
    queryFn: rindmService.getActiveCycle,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 10, // 10 minutes
    retry: 2,
    retryDelay: 500,
    onError: (error) => {
      console.error('Error fetching active cycle:', handleApiError(error));
    },
  });
};

// Get cycle status
export const useCycleStatus = (cycleId) => {
  return useQuery({
    queryKey: ['cycleStatus', cycleId],
    queryFn: () => rindmService.getCycleStatus(cycleId),
    enabled: !!cycleId,
    staleTime: 1000 * 30, // 30 seconds
    cacheTime: 1000 * 60, // 1 minute
    retry: 2,
    retryDelay: 500,
  });
};

// Get cycle history
export const useCycleHistory = () => {
  return useQuery({
    queryKey: ['cycleHistory'],
    queryFn: rindmService.getCycleHistory,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 10, // 10 minutes
    retry: 2,
    retryDelay: 500,
  });
};

// Start cycle mutation
export const useStartCycle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ recommendationId, selectedCrop, soilType }) =>
      rindmService.startCycle(recommendationId, selectedCrop, soilType),
    onSuccess: (data) => {
      // Invalidate and refetch active cycle
      queryClient.invalidateQueries({ queryKey: ['activeCycle'] });
      return data;
    },
    onError: (error) => {
      console.error('Error starting cycle:', handleApiError(error));
    },
  });
};

// Complete cycle mutation
export const useCompleteCycle = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cycleId) => rindmService.completeCycle(cycleId),
    onSuccess: (data) => {
      // Invalidate active cycle and history
      queryClient.invalidateQueries({ queryKey: ['activeCycle'] });
      queryClient.invalidateQueries({ queryKey: ['cycleHistory'] });
      return data;
    },
    onError: (error) => {
      console.error('Error completing cycle:', handleApiError(error));
    },
  });
};

// Check weather mutation
export const useCheckWeather = () => {
  return useMutation({
    mutationFn: (cycleId) => rindmService.checkWeather(cycleId),
    onError: (error) => {
      console.error('Error checking weather:', handleApiError(error));
    },
  });
};
