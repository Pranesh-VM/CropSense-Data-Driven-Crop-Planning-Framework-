import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useGetRecommendations, useNutrientStatus } from '../../hooks/useNutrients';
import { useStartCycle } from '../../hooks/useCycle';
import { CROPS, SOIL_TYPES } from '../../utils/constants';

export const NewCycle = () => {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      nitrogen: 50,
      phosphorus: 20,
      potassium: 50,
      ph: 7.0,
      latitude: 28.6139,
      longitude: 77.2090,
    },
  });

  const [step, setStep] = useState(1); // 1: Input, 2: Recommendations, 3: Confirm
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [selectedSoilType, setSelectedSoilType] = useState(null);
  const [formData, setFormData] = useState(null);

  const getRecommendations = useGetRecommendations();
  const startCycle = useStartCycle();

  const nitrogen = watch('nitrogen');
  const phosphorus = watch('phosphorus');
  const potassium = watch('potassium');

  const nitrogenStatus = useNutrientStatus(nitrogen, 'nitrogen');
  const phosphorusStatus = useNutrientStatus(phosphorus, 'phosphorus');
  const potassiumStatus = useNutrientStatus(potassium, 'potassium');

  const onSubmitStep1 = async (data) => {
    try {
      setFormData(data);
      const result = await getRecommendations.mutateAsync({
        n: parseFloat(data.nitrogen),
        p: parseFloat(data.phosphorus),
        k: parseFloat(data.potassium),
        ph: parseFloat(data.ph),
        latitude: parseFloat(data.latitude),
        longitude: parseFloat(data.longitude),
      });

      if (result && result.recommendations) {
        setStep(2);
        toast.success('Recommendations fetched successfully!');
      }
    } catch (error) {
      toast.error('Failed to fetch recommendations. Please try again.');
    }
  };

  const onConfirmCycle = async () => {
    if (!selectedCrop || !selectedSoilType) {
      toast.warning('Please select both crop and soil type');
      return;
    }

    try {
      const recommendationId = getRecommendations.data?.recommendation_id || 1; // Use recommendation_id from backend

      const result = await startCycle.mutateAsync({
        recommendationId,
        selectedCrop,
        soilType: selectedSoilType,
      });

      if (result) {
        toast.success('Cycle started successfully!');
        navigate('/cycle/active');
      }
    } catch (error) {
      toast.error('Failed to start cycle. Please try again.');
    }
  };

  const recommendations = getRecommendations.data?.recommendations?.top_3_crops || [];
  const hasRecommendations = recommendations && recommendations.length > 0;

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">🌾 Start New Cycle</h1>
          <p className="text-gray-600 mt-2">
            Enter soil nutrient levels to get crop recommendations
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8 flex items-center justify-between">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition ${
                  s <= step
                    ? 'bg-emerald-500 text-white'
                    : 'bg-gray-300 text-gray-900'
                }`}
              >
                {s}
              </div>
              {s < 3 && (
                <div
                  className={`h-1 flex-1 mx-2 transition ${
                    s < step ? 'bg-emerald-500' : 'bg-gray-300'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Input Form */}
        {step === 1 && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Soil Analysis</h2>

            <form onSubmit={handleSubmit(onSubmitStep1)} className="space-y-6">
              {/* Nutrient Inputs */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Nitrogen */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nitrogen (N) - kg/ha
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.nitrogen ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('nitrogen', {
                      required: 'Nitrogen is required',
                      min: { value: 0, message: 'Must be positive' },
                    })}
                  />
                  {errors.nitrogen && (
                    <p className="text-red-500 text-xs mt-1">{errors.nitrogen.message}</p>
                  )}
                  <div
                    className="mt-2 p-2 rounded text-white text-xs font-semibold text-center"
                    style={{ backgroundColor: nitrogenStatus.color }}
                  >
                    {nitrogenStatus.status}
                  </div>
                </div>

                {/* Phosphorus */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phosphorus (P) - kg/ha
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.phosphorus ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('phosphorus', {
                      required: 'Phosphorus is required',
                      min: { value: 0, message: 'Must be positive' },
                    })}
                  />
                  {errors.phosphorus && (
                    <p className="text-red-500 text-xs mt-1">{errors.phosphorus.message}</p>
                  )}
                  <div
                    className="mt-2 p-2 rounded text-white text-xs font-semibold text-center"
                    style={{ backgroundColor: phosphorusStatus.color }}
                  >
                    {phosphorusStatus.status}
                  </div>
                </div>

                {/* Potassium */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Potassium (K) - kg/ha
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.potassium ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('potassium', {
                      required: 'Potassium is required',
                      min: { value: 0, message: 'Must be positive' },
                    })}
                  />
                  {errors.potassium && (
                    <p className="text-red-500 text-xs mt-1">{errors.potassium.message}</p>
                  )}
                  <div
                    className="mt-2 p-2 rounded text-white text-xs font-semibold text-center"
                    style={{ backgroundColor: potassiumStatus.color }}
                  >
                    {potassiumStatus.status}
                  </div>
                </div>
              </div>

              {/* pH Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  pH Level
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="14"
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                    errors.ph ? 'border-red-500' : 'border-gray-300'
                  }`}
                  {...register('ph', {
                    required: 'pH is required',
                    min: { value: 0, message: 'pH must be between 0 and 14' },
                    max: { value: 14, message: 'pH must be between 0 and 14' },
                  })}
                />
                {errors.ph && <p className="text-red-500 text-xs mt-1">{errors.ph.message}</p>}
              </div>

              {/* Location */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.latitude ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('latitude', {
                      required: 'Latitude is required',
                      min: { value: -90, message: 'Invalid latitude' },
                      max: { value: 90, message: 'Invalid latitude' },
                    })}
                  />
                  {errors.latitude && (
                    <p className="text-red-500 text-xs mt-1">{errors.latitude.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                      errors.longitude ? 'border-red-500' : 'border-gray-300'
                    }`}
                    {...register('longitude', {
                      required: 'Longitude is required',
                      min: { value: -180, message: 'Invalid longitude' },
                      max: { value: 180, message: 'Invalid longitude' },
                    })}
                  />
                  {errors.longitude && (
                    <p className="text-red-500 text-xs mt-1">{errors.longitude.message}</p>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => navigate('/dashboard')}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-3 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={getRecommendations.isPending}
                  className="flex-1 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition"
                >
                  {getRecommendations.isPending ? 'Getting Recommendations...' : 'Get Recommendations'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: Recommendations */}
        {step === 2 && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Crop Recommendations</h2>

            {getRecommendations.isPending ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading recommendations...</p>
              </div>
            ) : hasRecommendations ? (
              <div className="space-y-4 mb-6">
                {recommendations.map((cropItem, idx) => (
                  <label
                    key={idx}
                    className={`block p-4 border-2 rounded-lg cursor-pointer transition ${
                      selectedCrop === cropItem.crop
                        ? 'border-emerald-500 bg-emerald-50'
                        : 'border-gray-200 hover:border-emerald-300'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <input
                        type="radio"
                        name="crop"
                        value={cropItem.crop}
                        checked={selectedCrop === cropItem.crop}
                        onChange={(e) => setSelectedCrop(e.target.value)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <p className="font-bold text-gray-900 text-lg capitalize">{cropItem.crop}</p>
                        <p className="text-gray-600 text-sm mt-1">
                          Confidence: {(cropItem.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-600 py-8">No recommendations available</p>
            )}

            {/* Soil Type Selection */}
            {selectedCrop && (
              <div className="mt-8 p-6 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Soil Type</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {SOIL_TYPES.map((soil) => (
                    <button
                      key={soil}
                      onClick={() => setSelectedSoilType(soil)}
                      className={`p-3 rounded-lg font-medium transition capitalize ${
                        selectedSoilType === soil
                          ? 'bg-emerald-500 text-white'
                          : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
                      }`}
                    >
                      {soil}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 pt-8">
              <button
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-3 rounded-lg transition"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={!selectedCrop || !selectedSoilType}
                className="flex-1 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition"
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Confirmation */}
        {step === 3 && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Confirm Cycle Details</h2>

            <div className="space-y-4 mb-8">
              <div className="border border-gray-200 rounded-lg p-4">
                <p className="text-gray-600 text-sm mb-1">Selected Crop</p>
                <p className="text-2xl font-bold text-gray-900 capitalize">{selectedCrop}</p>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <p className="text-gray-600 text-sm mb-1">Soil Type</p>
                <p className="text-2xl font-bold text-gray-900 capitalize">{selectedSoilType}</p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Nitrogen</p>
                  <p className="text-lg font-bold text-gray-900">{formData?.nitrogen}</p>
                </div>
                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Phosphorus</p>
                  <p className="text-lg font-bold text-gray-900">{formData?.phosphorus}</p>
                </div>
                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Potassium</p>
                  <p className="text-lg font-bold text-gray-900">{formData?.potassium}</p>
                </div>
              </div>
            </div>

            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-8">
              <p className="text-emerald-900">
                ✅ Everything looks good! Click <strong>Start Cycle</strong> to begin your crop management.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => setStep(2)}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-3 rounded-lg transition"
              >
                Back
              </button>
              <button
                onClick={onConfirmCycle}
                disabled={startCycle.isPending}
                className="flex-1 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition"
              >
                {startCycle.isPending ? 'Starting Cycle...' : 'Start Cycle'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
