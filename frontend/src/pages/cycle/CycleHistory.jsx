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
          <p className="text-gray-600 mt-2">View all your past crop cycles</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {cycles && cycles.length > 0 ? (
              <div className="space-y-4">
                {cycles.map((cycle, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelectedCycle(cycle)}
                    className={`bg-white rounded-lg shadow-md p-6 cursor-pointer transition border-2 ${
                      selectedCycle?.id === cycle.id
                        ? 'border-emerald-500 bg-emerald-50'
                        : 'border-gray-200 hover:border-emerald-300'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 capitalize">
                          {cycle.crop}
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
                          <div>
                            <p className="text-gray-600">Soil Type</p>
                            <p className="font-semibold text-gray-900 capitalize">
                              {cycle.soil_type}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">pH</p>
                            <p className="font-semibold text-gray-900">{cycle.ph}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Start Date</p>
                            <p className="font-semibold text-gray-900">
                              {new Date(cycle.start_date).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-gray-600">Status</p>
                            <p className="font-semibold">
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                  cycle.status === 'completed'
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-yellow-100 text-yellow-800'
                                }`}
                              >
                                {cycle.status}
                              </span>
                            </p>
                          </div>
                        </div>
                      </div>
                      <svg
                        className={`w-5 h-5 text-gray-400 transition transform ${
                          selectedCycle?.id === cycle.id ? 'rotate-90' : ''
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
                    {selectedCycle?.id === cycle.id && (
                      <div className="mt-6 pt-6 border-t border-emerald-200 space-y-4">
                        <h4 className="font-semibold text-gray-900">Nutrient Data</h4>
                        <div className="grid grid-cols-3 gap-4">
                          <div className="bg-blue-50 rounded-lg p-3">
                            <p className="text-gray-600 text-sm">Nitrogen</p>
                            <p className="text-lg font-bold text-blue-600">
                              {cycle.nitrogen_kg_ha?.toFixed(1)} kg/ha
                            </p>
                          </div>
                          <div className="bg-green-50 rounded-lg p-3">
                            <p className="text-gray-600 text-sm">Phosphorus</p>
                            <p className="text-lg font-bold text-green-600">
                              {cycle.phosphorus_kg_ha?.toFixed(1)} kg/ha
                            </p>
                          </div>
                          <div className="bg-yellow-50 rounded-lg p-3">
                            <p className="text-gray-600 text-sm">Potassium</p>
                            <p className="text-lg font-bold text-yellow-600">
                              {cycle.potassium_kg_ha?.toFixed(1)} kg/ha
                            </p>
                          </div>
                        </div>

                        {cycle.end_date && (
                          <div>
                            <h4 className="font-semibold text-gray-900 mt-4">Duration</h4>
                            <p className="text-gray-600">
                              {new Date(cycle.start_date).toLocaleDateString()} to{' '}
                              {new Date(cycle.end_date).toLocaleDateString()}
                            </p>
                            <p className="text-gray-600 text-sm">
                              {Math.floor(
                                (new Date(cycle.end_date) - new Date(cycle.start_date)) /
                                  (1000 * 60 * 60 * 24)
                              )}{' '}
                              days
                            </p>
                          </div>
                        )}

                        {cycle.notes && (
                          <div>
                            <h4 className="font-semibold text-gray-900 mt-4">Notes</h4>
                            <p className="text-gray-600">{cycle.notes}</p>
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
                  You haven't completed any crop cycles yet. Start a new cycle to begin tracking.
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
                <p className="text-4xl font-bold text-gray-900">{cycles.length}</p>
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
                <h3 className="text-sm font-semibold text-gray-600 mb-2">AVG DURATION</h3>
                <p className="text-3xl font-bold text-blue-600">
                  {cycles.length > 0
                    ? Math.round(
                        cycles
                          .filter((c) => c.end_date)
                          .reduce((sum, c) => {
                            const days = Math.floor(
                              (new Date(c.end_date) - new Date(c.start_date)) / (1000 * 60 * 60 * 24)
                            );
                            return sum + days;
                          }, 0) / cycles.filter((c) => c.end_date).length
                      )
                    : 0}{' '}
                  days
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
    cropCount[c.crop] = (cropCount[c.crop] || 0) + 1;
  });

  return Object.entries(cropCount)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);
};
