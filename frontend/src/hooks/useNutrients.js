import { useQuery, useMutation } from '@tanstack/react-query';
import { rindmService, handleApiError } from '../services/api';

// Get recommendations mutation
export const useGetRecommendations = () => {
  return useMutation({
    mutationFn: ({ n, p, k, ph, latitude, longitude }) =>
      rindmService.getRecommendations(n, p, k, ph, latitude, longitude),
    onError: (error) => {
      console.error('Error getting recommendations:', handleApiError(error));
    },
  });
};

// Nutrient status calculation
export const useNutrientStatus = (nutrientValue, nutrientType) => {
  const thresholds = {
    nitrogen: { min: 40, optimal: 80, max: 150 },
    phosphorus: { min: 15, optimal: 40, max: 80 },
    potassium: { min: 40, optimal: 100, max: 200 },
  };

  const config = thresholds[nutrientType] || thresholds.nitrogen;

  let status = 'optimal';
  if (nutrientValue < config.min) {
    status = 'critical';
  } else if (nutrientValue < config.optimal) {
    status = 'below';
  } else if (nutrientValue > config.max) {
    status = 'above';
  }

  const colors = {
    critical: '#DC2626', // Dark red
    below: '#EF4444',    // Red
    optimal: '#22C55E',  // Green
    above: '#EAB308',    // Yellow
  };

  return {
    status,
    color: colors[status],
    threshold: config,
  };
};

// Format nutrient data for display
export const formatNutrientData = (n, p, k) => {
  return [
    {
      name: 'Nitrogen (N)',
      value: n,
      unit: 'kg/ha',
      key: 'nitrogen',
    },
    {
      name: 'Phosphorus (P)',
      value: p,
      unit: 'kg/ha',
      key: 'phosphorus',
    },
    {
      name: 'Potassium (K)',
      value: k,
      unit: 'kg/ha',
      key: 'potassium',
    },
  ];
};
