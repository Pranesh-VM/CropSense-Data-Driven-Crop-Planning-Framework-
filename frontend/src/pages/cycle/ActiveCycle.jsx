import React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useActiveCycle, useCheckWeather, useCompleteCycle } from '../../hooks/useCycle';

export const ActiveCycle = () => {
  const navigate = useNavigate();
  const { data: activeCycleData, isLoading, refetch } = useActiveCycle();
  const checkWeather = useCheckWeather();
  const completeCycle = useCompleteCycle();
  const [showCompleteModal, setShowCompleteModal] = React.useState(false);
  const [showWeatherModal, setShowWeatherModal] = React.useState(false);
  const [showCompletionResultModal, setShowCompletionResultModal] = React.useState(false);
  const [weatherResult, setWeatherResult] = React.useState(null);
  const [completionResult, setCompletionResult] = React.useState(null);

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
      setWeatherResult(result);
      setShowWeatherModal(true);
      // Refetch cycle data if rainfall was detected (nutrients may have changed)
      if (result.rainfall_detected) {
        refetch();
      }
      toast.success('Weather data fetched successfully!');
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
      setCompletionResult(result);
      setShowCompletionResultModal(true);
    } catch (error) {
      toast.error('Failed to complete cycle');
    }
  };

  const handleStartNewCycle = () => {
    // Navigate to new cycle page with final nutrients pre-filled
    const nextCycleData = completionResult?.next_cycle_data;
    if (nextCycleData?.final_nutrients) {
      navigate('/cycle/new', { 
        state: { 
          prefillNutrients: nextCycleData.final_nutrients,
          fromCompletedCycle: true
        } 
      });
    } else {
      navigate('/cycle/new');
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
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Start Date</p>
                  <p className="text-gray-900 font-semibold">
                    {activeCycle.start_date ? new Date(activeCycle.start_date).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Expected End</p>
                  <p className="text-gray-900 font-semibold">
                    {activeCycle.expected_end_date ? new Date(activeCycle.expected_end_date).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm mb-1">Days Elapsed</p>
                  <p className="text-gray-900 font-semibold">
                    {activeCycle.progress?.days_elapsed || 0} / {activeCycle.progress?.total_days || 0} days
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

            {/* Crop Requirements */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Crop Requirements</h2>
              <p className="text-gray-600 text-sm mb-4">Nutrient uptake needed by <span className="font-semibold capitalize">{activeCycle.crop}</span> over the full cycle</p>
              
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                  <p className="text-blue-600 text-sm font-medium">Nitrogen (N)</p>
                  <p className="text-2xl font-bold text-blue-800">{activeCycle.crop_requirements?.N?.toFixed(1) || 0}</p>
                  <p className="text-blue-600 text-xs">kg/ha</p>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                  <p className="text-green-600 text-sm font-medium">Phosphorus (P)</p>
                  <p className="text-2xl font-bold text-green-800">{activeCycle.crop_requirements?.P?.toFixed(1) || 0}</p>
                  <p className="text-green-600 text-xs">kg/ha</p>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
                  <p className="text-orange-600 text-sm font-medium">Potassium (K)</p>
                  <p className="text-2xl font-bold text-orange-800">{activeCycle.crop_requirements?.K?.toFixed(1) || 0}</p>
                  <p className="text-orange-600 text-xs">kg/ha</p>
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

              {/* Initial vs Current Comparison */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Initial vs Current</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 text-gray-600 font-medium">Nutrient</th>
                        <th className="text-right py-2 text-gray-600 font-medium">Initial</th>
                        <th className="text-right py-2 text-gray-600 font-medium">Current</th>
                        <th className="text-right py-2 text-gray-600 font-medium">Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-100">
                        <td className="py-2 font-medium text-gray-900">Nitrogen (N)</td>
                        <td className="text-right py-2 text-gray-600">{activeCycle.initial_nutrients?.N?.toFixed(1) || 0}</td>
                        <td className="text-right py-2 text-gray-900 font-semibold">{activeCycle.current_nutrients?.N?.toFixed(1) || 0}</td>
                        <td className={`text-right py-2 font-semibold ${(activeCycle.current_nutrients?.N - activeCycle.initial_nutrients?.N) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {((activeCycle.current_nutrients?.N || 0) - (activeCycle.initial_nutrients?.N || 0)).toFixed(1)}
                        </td>
                      </tr>
                      <tr className="border-b border-gray-100">
                        <td className="py-2 font-medium text-gray-900">Phosphorus (P)</td>
                        <td className="text-right py-2 text-gray-600">{activeCycle.initial_nutrients?.P?.toFixed(1) || 0}</td>
                        <td className="text-right py-2 text-gray-900 font-semibold">{activeCycle.current_nutrients?.P?.toFixed(1) || 0}</td>
                        <td className={`text-right py-2 font-semibold ${(activeCycle.current_nutrients?.P - activeCycle.initial_nutrients?.P) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {((activeCycle.current_nutrients?.P || 0) - (activeCycle.initial_nutrients?.P || 0)).toFixed(1)}
                        </td>
                      </tr>
                      <tr>
                        <td className="py-2 font-medium text-gray-900">Potassium (K)</td>
                        <td className="text-right py-2 text-gray-600">{activeCycle.initial_nutrients?.K?.toFixed(1) || 0}</td>
                        <td className="text-right py-2 text-gray-900 font-semibold">{activeCycle.current_nutrients?.K?.toFixed(1) || 0}</td>
                        <td className={`text-right py-2 font-semibold ${(activeCycle.current_nutrients?.K - activeCycle.initial_nutrients?.K) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {((activeCycle.current_nutrients?.K || 0) - (activeCycle.initial_nutrients?.K || 0)).toFixed(1)}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
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

            {/* Soil Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">🌱 Soil Info</h3>

              <div className="space-y-3">
                <div>
                  <p className="text-gray-600 text-sm">Soil Type</p>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {activeCycle.soil_type || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Soil pH</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {activeCycle.ph?.toFixed(1) || 'N/A'}
                  </p>
                </div>
              </div>
            </div>

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

      {/* Weather Result Modal */}
      {showWeatherModal && weatherResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                {weatherResult.rainfall_detected ? '🌧️' : '☀️'} Weather Report
              </h2>
              <button
                onClick={() => setShowWeatherModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            {/* Location Info */}
            {weatherResult.location && (
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-600 mb-1">Location</p>
                <p className="text-lg font-semibold text-gray-900">
                  {weatherResult.location.name}{weatherResult.location.country ? `, ${weatherResult.location.country}` : ''}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {weatherResult.location.latitude?.toFixed(4)}, {weatherResult.location.longitude?.toFixed(4)}
                </p>
              </div>
            )}

            {/* Weather Details */}
            {weatherResult.weather && (
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <p className="text-blue-600 text-xs font-medium">Temperature</p>
                  <p className="text-2xl font-bold text-blue-800">{weatherResult.weather.temperature?.toFixed(1)}°C</p>
                  <p className="text-blue-600 text-xs">Feels like {weatherResult.weather.feels_like?.toFixed(1)}°C</p>
                </div>
                <div className="bg-cyan-50 rounded-lg p-3 text-center">
                  <p className="text-cyan-600 text-xs font-medium">Humidity</p>
                  <p className="text-2xl font-bold text-cyan-800">{weatherResult.weather.humidity}%</p>
                </div>
                <div className="bg-indigo-50 rounded-lg p-3 text-center">
                  <p className="text-indigo-600 text-xs font-medium">Pressure</p>
                  <p className="text-2xl font-bold text-indigo-800">{weatherResult.weather.pressure}</p>
                  <p className="text-indigo-600 text-xs">hPa</p>
                </div>
                <div className={`rounded-lg p-3 text-center ${weatherResult.weather.rainfall > 0 ? 'bg-blue-100' : 'bg-green-50'}`}>
                  <p className={`text-xs font-medium ${weatherResult.weather.rainfall > 0 ? 'text-blue-600' : 'text-green-600'}`}>Rainfall</p>
                  <p className={`text-2xl font-bold ${weatherResult.weather.rainfall > 0 ? 'text-blue-800' : 'text-green-800'}`}>{weatherResult.weather.rainfall || 0}</p>
                  <p className={`text-xs ${weatherResult.weather.rainfall > 0 ? 'text-blue-600' : 'text-green-600'}`}>mm</p>
                </div>
              </div>
            )}

            {/* Weather Description */}
            {weatherResult.weather?.description && (
              <div className="text-center mb-4">
                <span className="inline-block px-4 py-2 bg-gray-100 rounded-full text-gray-700 text-sm capitalize">
                  {weatherResult.weather.description}
                </span>
              </div>
            )}

            {/* Rainfall Impact Section */}
            {weatherResult.rainfall_detected ? (
              <div className="border-t border-gray-200 pt-4">
                <h3 className="text-lg font-semibold text-red-600 mb-3 flex items-center gap-2">
                  ⚠️ Rainfall Impact on Nutrients
                </h3>
                
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                  <p className="text-red-800 text-sm mb-2">
                    <strong>{weatherResult.rainfall_mm} mm</strong> of rainfall detected
                  </p>
                  <p className="text-red-700 text-xs">{weatherResult.message}</p>
                </div>

                {/* Nutrient Loss */}
                {weatherResult.nutrient_loss && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Nutrient Loss (kg/ha)</p>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-red-100 rounded-lg p-2 text-center">
                        <p className="text-red-600 text-xs">N Loss</p>
                        <p className="text-lg font-bold text-red-800">-{weatherResult.nutrient_loss.N?.toFixed(2)}</p>
                      </div>
                      <div className="bg-red-100 rounded-lg p-2 text-center">
                        <p className="text-red-600 text-xs">P Loss</p>
                        <p className="text-lg font-bold text-red-800">-{weatherResult.nutrient_loss.P?.toFixed(2)}</p>
                      </div>
                      <div className="bg-red-100 rounded-lg p-2 text-center">
                        <p className="text-red-600 text-xs">K Loss</p>
                        <p className="text-lg font-bold text-red-800">-{weatherResult.nutrient_loss.K?.toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Updated Nutrients */}
                {weatherResult.updated_nutrients && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Updated Nutrient Levels (kg/ha)</p>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-blue-50 rounded-lg p-2 text-center">
                        <p className="text-blue-600 text-xs">Nitrogen</p>
                        <p className="text-lg font-bold text-blue-800">{weatherResult.updated_nutrients.N?.toFixed(1)}</p>
                      </div>
                      <div className="bg-green-50 rounded-lg p-2 text-center">
                        <p className="text-green-600 text-xs">Phosphorus</p>
                        <p className="text-lg font-bold text-green-800">{weatherResult.updated_nutrients.P?.toFixed(1)}</p>
                      </div>
                      <div className="bg-orange-50 rounded-lg p-2 text-center">
                        <p className="text-orange-600 text-xs">Potassium</p>
                        <p className="text-lg font-bold text-orange-800">{weatherResult.updated_nutrients.K?.toFixed(1)}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Warning */}
                {weatherResult.warning && (
                  <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <p className="text-yellow-800 text-sm font-medium">🔬 Soil Test Recommended</p>
                    <p className="text-yellow-700 text-xs mt-1">Nutrient levels are below optimal. Consider conducting a soil test.</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="border-t border-gray-200 pt-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                  <p className="text-green-800 font-medium">✓ No Rainfall Detected</p>
                  <p className="text-green-600 text-sm mt-1">Your nutrient levels remain unchanged.</p>
                </div>
              </div>
            )}

            {/* Timestamp */}
            {weatherResult.weather?.timestamp && (
              <p className="text-xs text-gray-400 text-center mt-4">
                Data as of: {new Date(weatherResult.weather.timestamp).toLocaleString()}
              </p>
            )}

            {/* Close Button */}
            <button
              onClick={() => setShowWeatherModal(false)}
              className="w-full mt-6 bg-gray-800 hover:bg-gray-900 text-white font-semibold py-3 px-4 rounded-lg transition"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Cycle Completion Result Modal */}
      {showCompletionResultModal && completionResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="text-center mb-6">
              <div className="text-5xl mb-3">🎉</div>
              <h2 className="text-2xl font-bold text-gray-900">Cycle Completed!</h2>
              <p className="text-gray-600 mt-2">Here's your harvest summary and next steps</p>
            </div>

            {/* Final Nutrients Summary */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Final Soil Nutrients</h3>
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                  <p className="text-blue-600 text-sm font-medium">Nitrogen (N)</p>
                  <p className="text-2xl font-bold text-blue-800">
                    {completionResult.next_cycle_data?.final_nutrients?.N || completionResult.final_nutrients?.N?.toFixed(1) || 0}
                  </p>
                  <p className="text-blue-600 text-xs">kg/ha</p>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                  <p className="text-green-600 text-sm font-medium">Phosphorus (P)</p>
                  <p className="text-2xl font-bold text-green-800">
                    {completionResult.next_cycle_data?.final_nutrients?.P || completionResult.final_nutrients?.P?.toFixed(1) || 0}
                  </p>
                  <p className="text-green-600 text-xs">kg/ha</p>
                </div>
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-center">
                  <p className="text-orange-600 text-sm font-medium">Potassium (K)</p>
                  <p className="text-2xl font-bold text-orange-800">
                    {completionResult.next_cycle_data?.final_nutrients?.K || completionResult.final_nutrients?.K?.toFixed(1) || 0}
                  </p>
                  <p className="text-orange-600 text-xs">kg/ha</p>
                </div>
              </div>
            </div>

            {/* Fertilizer Recommendations (if nutrients too low) */}
            {completionResult.next_cycle_data?.nutrients_too_low && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-yellow-800 mb-2 flex items-center gap-2">
                  ⚠️ Fertilizer Recommendations
                </h3>
                <p className="text-yellow-700 text-sm mb-4">
                  {completionResult.next_cycle_data.message}
                </p>
                
                <div className="space-y-3">
                  {completionResult.next_cycle_data.fertilizer_recommendations?.map((rec, idx) => (
                    <div key={idx} className="bg-white border border-yellow-300 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-semibold text-gray-900">{rec.nutrient}</span>
                        <span className="text-sm text-red-600">
                          Current: {rec.current_level} kg/ha
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">
                        Add approximately <strong>{rec.recommended_addition} kg/ha</strong>
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {rec.fertilizer_options?.map((opt, i) => (
                          <span key={i} className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                            {opt}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Success message when nutrients are good */}
            {!completionResult.next_cycle_data?.nutrients_too_low && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 text-center">
                <p className="text-green-800 font-medium">✓ Your soil is ready for a new crop cycle!</p>
                <p className="text-green-600 text-sm mt-1">Start a new cycle to get crop recommendations.</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 mt-6">
              {completionResult.next_cycle_data?.nutrients_too_low ? (
                <button
                  onClick={handleStartNewCycle}
                  className="flex-1 bg-amber-500 hover:bg-amber-600 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2"
                >
                  🧪 Replenish Soil & Start Cycle
                </button>
              ) : (
                <button
                  onClick={handleStartNewCycle}
                  className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3 px-6 rounded-lg transition flex items-center justify-center gap-2"
                >
                  🌾 Start New Cycle
                </button>
              )}
              <button
                onClick={() => {
                  setShowCompletionResultModal(false);
                  navigate('/cycle/history');
                }}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-3 px-6 rounded-lg transition"
              >
                View History
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
