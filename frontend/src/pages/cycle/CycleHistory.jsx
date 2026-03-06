import React, { useState } from 'react';
import { useCycleHistory } from '../../hooks/useCycle';

export const CycleHistory = () => {
  const { data: historyData, isLoading } = useCycleHistory();
  const [selectedCycle, setSelectedCycle] = useState(null);

  const cycles = historyData?.cycles || [];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading cycle history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">📈 Cycle History</h1>
          <p className="text-gray-600 mt-2">
            View all your crop cycles ({historyData?.total || 0} total)
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {cycles && cycles.length > 0 ? (
              <div className="space-y-4">
                {cycles.map((cycle) => (
                  <div
                    key={cycle.cycle_id}
                    onClick={() => setSelectedCycle(selectedCycle?.cycle_id === cycle.cycle_id ? null : cycle)}
                    className={`bg-white rounded-lg shadow-md p-6 cursor-pointer transition border-2 ${
                      selectedCycle?.cycle_id === cycle.cycle_id
                        ? 'border-emerald-500 bg-emerald-50'
                        : 'border-gray-200 hover:border-emerald-300'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-bold text-gray-900 capitalize">
                            {cycle.crop_name}
                          </h3>
                          <span className="text-gray-500 text-sm">
                            Cycle #{cycle.cycle_number}
                          </span>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${
                              cycle.status === 'completed'
                                ? 'bg-green-100 text-green-800'
                                : cycle.status === 'active'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {cycle.status}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 text-sm">
                          <div>
                            <p className="text-gray-500 text-xs">Start Date</p>
                            <p className="font-semibold text-gray-900">
                              {new Date(cycle.start_date).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">End Date</p>
                            <p className="font-semibold text-gray-900">
                              {cycle.actual_end_date 
                                ? new Date(cycle.actual_end_date).toLocaleDateString()
                                : '—'}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Rainfall Events</p>
                            <p className="font-semibold text-gray-900">
                              {cycle.rainfall_event_count || 0}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-500 text-xs">Cycle ID</p>
                            <p className="font-semibold text-gray-400">
                              #{cycle.cycle_id}
                            </p>
                          </div>
                        </div>
                      </div>
                      <svg
                        className={`w-5 h-5 text-gray-400 transition transform ${
                          selectedCycle?.cycle_id === cycle.cycle_id ? 'rotate-90' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>

                    {/* Expanded Details */}
                    {selectedCycle?.cycle_id === cycle.cycle_id && (
                      <div className="mt-6 pt-6 border-t border-emerald-200 space-y-6">
                        {/* Initial Nutrients */}
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-3">Initial Nutrients (kg/ha)</h4>
                          <div className="grid grid-cols-3 gap-3">
                            <div className="bg-blue-50 rounded-lg p-3 text-center">
                              <p className="text-blue-600 text-xs font-medium">Nitrogen (N)</p>
                              <p className="text-xl font-bold text-blue-800">
                                {parseFloat(cycle.initial_n_kg_ha || 0).toFixed(1)}
                              </p>
                            </div>
                            <div className="bg-green-50 rounded-lg p-3 text-center">
                              <p className="text-green-600 text-xs font-medium">Phosphorus (P)</p>
                              <p className="text-xl font-bold text-green-800">
                                {parseFloat(cycle.initial_p_kg_ha || 0).toFixed(1)}
                              </p>
                            </div>
                            <div className="bg-orange-50 rounded-lg p-3 text-center">
                              <p className="text-orange-600 text-xs font-medium">Potassium (K)</p>
                              <p className="text-xl font-bold text-orange-800">
                                {parseFloat(cycle.initial_k_kg_ha || 0).toFixed(1)}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Final Nutrients (if completed) */}
                        {cycle.status === 'completed' && cycle.final_n_kg_ha && (
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-3">Final Nutrients (kg/ha)</h4>
                            <div className="grid grid-cols-3 gap-3">
                              <div className="bg-blue-100 rounded-lg p-3 text-center">
                                <p className="text-blue-600 text-xs font-medium">Nitrogen (N)</p>
                                <p className="text-xl font-bold text-blue-800">
                                  {parseFloat(cycle.final_n_kg_ha || 0).toFixed(1)}
                                </p>
                              </div>
                              <div className="bg-green-100 rounded-lg p-3 text-center">
                                <p className="text-green-600 text-xs font-medium">Phosphorus (P)</p>
                                <p className="text-xl font-bold text-green-800">
                                  {parseFloat(cycle.final_p_kg_ha || 0).toFixed(1)}
                                </p>
                              </div>
                              <div className="bg-orange-100 rounded-lg p-3 text-center">
                                <p className="text-orange-600 text-xs font-medium">Potassium (K)</p>
                                <p className="text-xl font-bold text-orange-800">
                                  {parseFloat(cycle.final_k_kg_ha || 0).toFixed(1)}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Rainfall Loss */}
                        {(parseFloat(cycle.total_rainfall_loss_n) > 0 || 
                          parseFloat(cycle.total_rainfall_loss_p) > 0 || 
                          parseFloat(cycle.total_rainfall_loss_k) > 0) && (
                          <div>
                            <h4 className="font-semibold text-red-600 mb-3">Total Rainfall Loss (kg/ha)</h4>
                            <div className="grid grid-cols-3 gap-3">
                              <div className="bg-red-50 rounded-lg p-3 text-center">
                                <p className="text-red-600 text-xs font-medium">N Loss</p>
                                <p className="text-xl font-bold text-red-800">
                                  -{parseFloat(cycle.total_rainfall_loss_n || 0).toFixed(2)}
                                </p>
                              </div>
                              <div className="bg-red-50 rounded-lg p-3 text-center">
                                <p className="text-red-600 text-xs font-medium">P Loss</p>
                                <p className="text-xl font-bold text-red-800">
                                  -{parseFloat(cycle.total_rainfall_loss_p || 0).toFixed(2)}
                                </p>
                              </div>
                              <div className="bg-red-50 rounded-lg p-3 text-center">
                                <p className="text-red-600 text-xs font-medium">K Loss</p>
                                <p className="text-xl font-bold text-red-800">
                                  -{parseFloat(cycle.total_rainfall_loss_k || 0).toFixed(2)}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* No rainfall loss message */}
                        {parseFloat(cycle.total_rainfall_loss_n || 0) === 0 && 
                         parseFloat(cycle.total_rainfall_loss_p || 0) === 0 && 
                         parseFloat(cycle.total_rainfall_loss_k || 0) === 0 && (
                          <div className="bg-gray-50 rounded-lg p-4 text-center">
                            <p className="text-gray-600 text-sm">
                              ✓ No rainfall-induced nutrient loss recorded
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <p className="text-5xl mb-4">📋</p>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">No Cycles Yet</h2>
                <p className="text-gray-600">
                  You haven't started any crop cycles yet. Start a new cycle to begin tracking.
                </p>
              </div>
            )}
          </div>

          {/* Sidebar Stats */}
          <div className="lg:col-span-1">
            {/* Summary Stats */}
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24 space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-600 mb-2">TOTAL CYCLES</h3>
                <p className="text-4xl font-bold text-gray-900">{historyData?.total || cycles.length}</p>
              </div>

              <hr className="border-gray-200" />

              <div>
                <h3 className="text-sm font-semibold text-gray-600 mb-2">ACTIVE</h3>
                <p className="text-3xl font-bold text-blue-600">
                  {cycles.filter((c) => c.status === 'active').length}
                </p>
              </div>

              <hr className="border-gray-200" />

              <div>
                <h3 className="text-sm font-semibold text-gray-600 mb-2">COMPLETED</h3>
                <p className="text-3xl font-bold text-green-600">
                  {cycles.filter((c) => c.status === 'completed').length}
                </p>
              </div>

              <hr className="border-gray-200" />

              <div>
                <h3 className="text-sm font-semibold text-gray-600 mb-2">TOTAL RAINFALL EVENTS</h3>
                <p className="text-3xl font-bold text-cyan-600">
                  {cycles.reduce((sum, c) => sum + (c.rainfall_event_count || 0), 0)}
                </p>
              </div>

              <hr className="border-gray-200" />

              {/* Top Crops */}
              {cycles.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-600 mb-3">TOP CROPS</h3>
                  <div className="space-y-2">
                    {getTopCrops(cycles).map((crop, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-gray-700 capitalize">{crop.name}</span>
                        <span className="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-semibold">
                          {crop.count}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to get top crops
const getTopCrops = (cycles) => {
  const cropCount = {};
  cycles.forEach((c) => {
    const cropName = c.crop_name || c.crop;
    if (cropName) {
      cropCount[cropName] = (cropCount[cropName] || 0) + 1;
    }
  });

  return Object.entries(cropCount)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);
};
