import React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useActiveCycle, useCheckWeather, useCompleteCycle } from '../../hooks/useCycle';

export const ActiveCycle = () => {
  const navigate = useNavigate();
  const { data: activeCycleData, isLoading } = useActiveCycle();
  const checkWeather = useCheckWeather();
  const completeCycle = useCompleteCycle();
  const [showCompleteModal, setShowCompleteModal] = React.useState(false);

  // Extract cycle data from nested structure
  const activeCycle = activeCycleData?.cycle || null;
  const hasActiveCycle = activeCycleData?.has_active_cycle && activeCycle;

  const handleCheckWeather = async () => {
    if (!activeCycle?.cycle_id) {
      toast.error('No active cycle found');
      return;
    }

    try {
      const result = await checkWeather.mutateAsync(activeCycle.cycle_id);
      toast.success('Weather data updated successfully!');
    } catch (error) {
      toast.error('Failed to fetch weather data');
    }
  };

  const handleCompleteCycle = async () => {
    if (!activeCycle?.cycle_id) {
      toast.error('No active cycle found');
      return;
    }

    try {
      const result = await completeCycle.mutateAsync(activeCycle.cycle_id);
      toast.success('Cycle completed successfully!');
      setShowCompleteModal(false);
      navigate('/cycle/history');
    } catch (error) {
      toast.error('Failed to complete cycle');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading active cycle...</p>
        </div>
      </div>
    );
  }

  if (!hasActiveCycle) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-5xl mb-4">🌱</p>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">No Active Cycle</h1>
            <p className="text-gray-600 mb-6">
              You don't have an active cycle right now. Start a new one to begin monitoring.
            </p>
            <button
              onClick={() => navigate('/cycle/new')}
              className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3 px-8 rounded-lg transition"
            >
              Start New Cycle
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">🌾 Active Cycle</h1>
          <p className="text-gray-600 mt-2">Monitor your crop and nutrient levels</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Cycle Overview */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Cycle Overview</h2>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Crop</p>
                  <p className="text-lg font-bold text-gray-900 capitalize">{activeCycle.crop || 'N/A'}</p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Cycle Number</p>
                  <p className="text-lg font-bold text-gray-900">
                    #{activeCycle.cycle_number || 1}
                  </p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Progress</p>
                  <p className="text-lg font-bold text-gray-900">{activeCycle.progress?.percent_complete || 0}%</p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <p className="text-gray-600 text-sm mb-1">Status</p>
                  <p className="inline-block px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-sm font-semibold capitalize">
                    {activeCycle.status || 'active'}
                  </p>
                </div>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Days Elapsed</p>
                  <p className="text-gray-900 font-semibold">
                    {activeCycle.progress?.days_elapsed || 0} days
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Days Remaining</p>
                  <p className="text-gray-900 font-semibold">
                    {activeCycle.progress?.days_remaining || 0} days
                  </p>
                </div>
              </div>
            </div>

            {/* Nutrient Status */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Nutrient Status</h2>

              <div className="space-y-4">
                <NutrientBar
                  name="Nitrogen (N)"
                  value={activeCycle.current_nutrients?.N}
                  unit="kg/ha"
                  type="nitrogen"
                />
                <NutrientBar
                  name="Phosphorus (P)"
                  value={activeCycle.current_nutrients?.P}
                  unit="kg/ha"
                  type="phosphorus"
                />
                <NutrientBar
                  name="Potassium (K)"
                  value={activeCycle.current_nutrients?.K}
                  unit="kg/ha"
                  type="potassium"
                />
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-900 text-sm">
                  💡 <strong>Tip:</strong> Monitor nutrient levels weekly for optimal crop yield.
                  Consider applying supplements if levels are critically low.
                </p>
              </div>
            </div>

            {/* Recent Measurements */}
            {activeCycle.measurements &&activeCycle.measurements.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Measurements</h2>

                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {activeCycle.measurements.map((measurement, idx) => (
                    <div
                      key={idx}
                      className="border border-gray-200 rounded-lg p-4 flex justify-between items-start"
                    >
                      <div>
                        <p className="font-semibold text-gray-900">
                          {measurement.measurement_type}
                        </p>
                        <p className="text-gray-600 text-sm mt-1">
                          {new Date(measurement.recorded_at).toLocaleString()}
                        </p>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          measurement.below_threshold
                            ? 'bg-red-100 text-red-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {measurement.below_threshold ? 'Low' : 'Normal'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>

              <div className="space-y-3">
                <button
                  onClick={handleCheckWeather}
                  disabled={checkWeather.isPending}
                  className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  {checkWeather.isPending ? 'Checking...' : '🌡️ Check Weather'}
                </button>

                <button
                  onClick={() => setShowCompleteModal(true)}
                  className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition"
                >
                  ✓ End Cycle
                </button>
              </div>
            </div>

            {/* Weather Summary */}
            {activeCycle.weather && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">🌦️ Weather</h3>

                <div className="space-y-3">
                  <div>
                    <p className="text-gray-600 text-sm">Temperature</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {activeCycle.weather.temperature || 'N/A'}°C
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Humidity</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {activeCycle.weather.humidity || 'N/A'}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Rainfall</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {activeCycle.weather.rainfall || 'N/A'} mm
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Location Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">📍 Location</h3>

              <div className="space-y-2 text-sm">
                <p>
                  <span className="text-gray-600">Latitude:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {activeCycle.latitude?.toFixed(4) || 'N/A'}
                  </span>
                </p>
                <p>
                  <span className="text-gray-600">Longitude:</span>
                  <span className="font-semibold text-gray-900 ml-2">
                    {activeCycle.longitude?.toFixed(4) || 'N/A'}
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Complete Cycle Modal */}
      {showCompleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">End This Cycle?</h2>

            <p className="text-gray-600 mb-6">
              Are you sure you want to end this cycle? This action cannot be undone.
            </p>

            <div className="space-y-3">
              <button
                onClick={() => setShowCompleteModal(false)}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-2 px-4 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleCompleteCycle}
                disabled={completeCycle.isPending}
                className="w-full bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                {completeCycle.isPending ? 'Ending Cycle...' : 'Yes, End Cycle'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Nutrient Progress Bar Component
const NutrientBar = ({ name, value, unit, type }) => {
  // Handle undefined or null values
  const safeValue = value ?? 0;
  
  const thresholds = {
    nitrogen: { min: 40, optimal: 80, max: 150 },
    phosphorus: { min: 15, optimal: 40, max: 80 },
    potassium: { min: 40, optimal: 100, max: 200 },
  };

  const config = thresholds[type] || thresholds.nitrogen;

  let statusColor = '#22C55E'; // Green - optimal
  let statusText = 'Optimal';

  if (safeValue < config.min) {
    statusColor = '#DC2626'; // Dark red - critical
    statusText = 'Critical';
  } else if (safeValue < config.optimal) {
    statusColor = '#EF4444'; // Red - low
    statusText = 'Low';
  } else if (safeValue > config.max) {
    statusColor = '#EAB308'; // Yellow - high
    statusText = 'High';
  }

  const percentage = (safeValue / config.max) * 100;
  const clampedPercentage = Math.min(percentage, 100);

  return (
    <div className="pb-4 border-b border-gray-200 last:border-0">
      <div className="flex justify-between items-center mb-2">
        <div>
          <p className="font-semibold text-gray-900">{name}</p>
          <p className="text-gray-600 text-sm">
            {safeValue.toFixed(1)} {unit}
          </p>
        </div>
        <div className="text-right">
          <span
            className="px-3 py-1 rounded-full text-sm font-semibold text-white"
            style={{ backgroundColor: statusColor }}
          >
            {statusText}
          </span>
        </div>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className="h-full transition-all duration-300 rounded-full"
          style={{
            width: `${clampedPercentage}%`,
            backgroundColor: statusColor,
          }}
        />
      </div>

      <p className="text-xs text-gray-500 mt-1">
        Optimal: {config.optimal} | Max: {config.max}
      </p>
    </div>
  );
};
