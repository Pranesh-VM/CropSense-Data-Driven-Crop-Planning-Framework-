import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { recommendationService } from '../../services/api';

export const QuickRecommendation = () => {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      N: 50,
      P: 50,
      K: 50,
      ph: 7.0,
      latitude: 28.6139,
      longitude: 77.2090,
    },
  });

  const [recommendations, setRecommendations] = useState(null);

  const getRecommendation = useMutation({
    mutationFn: (data) => recommendationService.getQuickRecommendation(
      parseFloat(data.N),
      parseFloat(data.P),
      parseFloat(data.K),
      parseFloat(data.ph),
      parseFloat(data.latitude),
      parseFloat(data.longitude)
    ),
    onSuccess: (response) => {
      setRecommendations(response.top_3_crops || []);
      toast.success('Recommendations fetched successfully!');
    },
    onError: (error) => {
      toast.error('Failed to fetch recommendations');
      console.error(error);
    },
  });

  const onSubmit = (data) => {
    getRecommendation.mutate(data);
  };

  const handleStartCycle = () => {
    navigate('/cycle/new');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-blue-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🌾</div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            Quick Crop Recommendation
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Get instant crop suggestions based on your soil nutrients and location. 
            Perfect for quick decisions!
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Form */}
          <div className="bg-white rounded-lg shadow-md p-6 h-fit">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span>📝</span>
              <span>Soil & Location Data</span>
            </h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Nutrient Inputs */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <span>🔵</span>
                    <span>N (kg/ha)</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.N ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('N', {
                      required: true,
                      min: 0,
                      max: 300,
                    })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <span>🟠</span>
                    <span>P (kg/ha)</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.P ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('P', {
                      required: true,
                      min: 0,
                      max: 150,
                    })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <span>🟣</span>
                    <span>K (kg/ha)</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.K ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('K', {
                      required: true,
                      min: 0,
                      max: 300,
                    })}
                  />
                </div>
              </div>

              {/* pH Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                  <span>⚗️</span>
                  <span>pH Level</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="14"
                  className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                    errors.ph ? 'border-red-500' : 'border-gray-300'
                  }`}
                  {...register('ph', {
                    required: true,
                    min: 0,
                    max: 14,
                  })}
                />
              </div>

              {/* Location */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <span>📍</span>
                    <span>Latitude</span>
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.latitude ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('latitude', {
                      required: true,
                      min: -90,
                      max: 90,
                    })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                    <span>🌐</span>
                    <span>Longitude</span>
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.longitude ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('longitude', {
                      required: true,
                      min: -180,
                      max: 180,
                    })}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={getRecommendation.isPending}
                className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center gap-2"
              >
                {getRecommendation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span>🔍</span>
                    <span>Get Recommendations</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Results */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <span>🌱</span>
              <span>Recommended Crops</span>
            </h2>

            {!recommendations ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🌾</div>
                <p className="text-gray-500 mb-2">No results yet</p>
                <p className="text-sm text-gray-400">
                  Enter your soil data and get instant recommendations
                </p>
              </div>
            ) : recommendations.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🤔</div>
                <p className="text-gray-600 font-semibold mb-2">No recommendations found</p>
                <p className="text-sm text-gray-500">
                  Try adjusting your soil parameters
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {recommendations.map((crop, idx) => (
                  <div
                    key={idx}
                    className={`border-2 rounded-lg p-4 transition-all ${
                      idx === 0
                        ? 'border-emerald-400 bg-emerald-50'
                        : idx === 1
                        ? 'border-blue-300 bg-blue-50'
                        : 'border-gray-300 bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">
                          {idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉'}
                        </span>
                        <div>
                          <p className="font-bold text-lg text-gray-900 capitalize">
                            {crop.crop}
                          </p>
                          <p className="text-sm text-gray-600">
                            {idx === 0 ? 'Best Match' : idx === 1 ? 'Good Match' : 'Alternative'}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-emerald-600">
                          {(crop.confidence * 100).toFixed(1)}%
                        </p>
                        <p className="text-xs text-gray-500">Confidence</p>
                      </div>
                    </div>

                    {/* Confidence Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          idx === 0
                            ? 'bg-emerald-500'
                            : idx === 1
                            ? 'bg-blue-500'
                            : 'bg-gray-500'
                        }`}
                        style={{ width: `${crop.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                ))}

                {/* Call to Action */}
                <div className="mt-8 p-6 bg-gradient-to-r from-emerald-100 to-blue-100 border-2 border-emerald-300 rounded-lg">
                  <div className="text-center mb-4">
                    <p className="text-xl font-bold text-gray-900 mb-2">
                      🎯 Ready to grow your crop?
                    </p>
                    <p className="text-gray-700 text-sm mb-4">
                      Start a full RINDM cycle to track nutrients, monitor weather, 
                      and optimize your harvest!
                    </p>
                  </div>
                  <button
                    onClick={handleStartCycle}
                    className="w-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
                  >
                    <span>🚀</span>
                    <span>Start Full Cycle</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className="bg-white rounded-lg shadow-sm p-4 text-center">
            <div className="text-3xl mb-2">⚡</div>
            <p className="font-semibold text-gray-900">Quick Results</p>
            <p className="text-xs text-gray-600 mt-1">
              Get instant recommendations in seconds
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 text-center">
            <div className="text-3xl mb-2">🎯</div>
            <p className="font-semibold text-gray-900">AI-Powered</p>
            <p className="text-xs text-gray-600 mt-1">
              Advanced ML models for accurate predictions
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 text-center">
            <div className="text-3xl mb-2">🌍</div>
            <p className="font-semibold text-gray-900">Location-Based</p>
            <p className="text-xs text-gray-600 mt-1">
              Weather data integrated for best results
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
