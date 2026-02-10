import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useActiveCycle, useCycleHistory } from '../../hooks/useCycle';
import { toast } from 'react-toastify';

export const Dashboard = () => {
  const { user } = useAuth();
  const { data: activeCycleData, isLoading: cycleLoading, error: cycleError } = useActiveCycle();
  const { data: cycleHistory, isLoading: historyLoading } = useCycleHistory();

  // Extract cycle data from nested structure
  const activeCycle = activeCycleData?.cycle || null;
  const hasActiveCycle = activeCycleData?.has_active_cycle && activeCycle;

  // Handle errors
  React.useEffect(() => {
    if (cycleError) {
      console.log('No active cycle:', cycleError);
    }
  }, [cycleError]);

  const totalCycles = cycleHistory?.cycles?.length || 0;

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
          Welcome back, <span className="text-emerald-600">{user?.username}</span>!
        </h1>
        <p className="text-gray-600 mt-2">Manage your crop cycles and monitor nutrient levels</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Active Cycle & Quick Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Cycle Card */}
          {hasActiveCycle ? (
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-emerald-500">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🌾 Active Cycle</h2>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-gray-600 text-sm">Crop</p>
                  <p className="text-lg font-semibold text-gray-900 capitalize">{activeCycle.crop || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Cycle #</p>
                  <p className="text-lg font-semibold text-gray-900">#{activeCycle.cycle_number || 1}</p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Status</p>
                  <p className="inline-block px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-sm font-semibold capitalize">
                    {activeCycle.status || 'active'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 text-sm">Progress</p>
                  <p className="text-lg font-semibold text-gray-900">{activeCycle.progress?.percent_complete || 0}%</p>
                </div>
              </div>

              {/* Nutrient Status Grid */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Nutrient Status</h3>
                <div className="grid grid-cols-3 gap-3">
                  <NutrientBadge
                    name="N (Nitrogen)"
                    value={activeCycle.current_nutrients?.N}
                    type="nitrogen"
                  />
                  <NutrientBadge
                    name="P (Phosphorus)"
                    value={activeCycle.current_nutrients?.P}
                    type="phosphorus"
                  />
                  <NutrientBadge
                    name="K (Potassium)"
                    value={activeCycle.current_nutrients?.K}
                    type="potassium"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Link
                  to="/cycle/active"
                  className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-2 px-4 rounded-lg transition text-center"
                >
                  View Details
                </Link>
                <button
                  onClick={() => toast.info('Complete cycle functionality coming soon!')}
                  className="flex-1 bg-red-50 hover:bg-red-100 text-red-600 font-semibold py-2 px-4 rounded-lg transition"
                >
                  End Cycle
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg shadow-md p-8 border-2 border-dashed border-emerald-300 text-center">
              <p className="text-5xl mb-3">🌱</p>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">No Active Cycle</h2>
              <p className="text-gray-600 mb-4">
                Start a new crop cycle to begin nutrient management and monitoring
              </p>
              <Link
                to="/cycle/new"
                className="inline-block bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-3 px-6 rounded-lg transition"
              >
                Start New Cycle
              </Link>
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Total Cycles</p>
                  <p className="text-3xl font-bold text-gray-900">{totalCycles}</p>
                </div>
                <div className="text-4xl">📊</div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm mb-1">Completed</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {cycleHistory?.completed_count || 0}
                  </p>
                </div>
                <div className="text-4xl">✅</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Recent Activity */}
        <div className="lg:col-span-1">
          {/* Recent Cycles */}
          <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
            <h2 className="text-xl font-bold text-gray-900 mb-4">📈 Recent Cycles</h2>

            {historyLoading ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500 mx-auto"></div>
              </div>
            ) : cycleHistory?.cycles && cycleHistory.cycles.length > 0 ? (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {cycleHistory.cycles.slice(0, 5).map((cycle, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 rounded-lg p-3 hover:border-emerald-300 hover:bg-emerald-50 transition cursor-pointer"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold text-gray-900">{cycle.crop}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(cycle.start_date).toLocaleDateString()}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          cycle.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {cycle.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No cycles yet</p>
            )}

            <Link
              to="/cycle/history"
              className="mt-4 block w-full bg-gray-100 hover:bg-gray-200 text-gray-900 font-semibold py-2 px-4 rounded-lg transition text-center"
            >
              View All History
            </Link>
          </div>
        </div>
      </div>

      {/* Information Cards */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-900 text-sm">
            💡 <strong>Tip:</strong> Monitor nutrient levels regularly for optimal crop yield.
          </p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-900 text-sm">
            🌡️ <strong>Weather:</strong> Check weather updates for your active cycle.
          </p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-900 text-sm">
            📋 <strong>Tasks:</strong> Review and manage your field data regularly.
          </p>
        </div>
      </div>
    </div>
  );
};

// Nutrient Badge Component
const NutrientBadge = ({ name, value, type }) => {
  // Handle undefined or null values
  const safeValue = value ?? 0;
  
  const thresholds = {
    nitrogen: { min: 40, optimal: 80, max: 150 },
    phosphorus: { min: 15, optimal: 40, max: 80 },
    potassium: { min: 40, optimal: 100, max: 200 },
  };

  const config = thresholds[type] || thresholds.nitrogen;
  let status = 'optimal';
  let bgColor = 'bg-green-100';
  let textColor = 'text-green-800';

  if (safeValue < config.min) {
    status = 'Critical';
    bgColor = 'bg-red-100';
    textColor = 'text-red-800';
  } else if (safeValue < config.optimal) {
    status = 'Low';
    bgColor = 'bg-yellow-100';
    textColor = 'text-yellow-800';
  } else if (safeValue > config.max) {
    status = 'High';
    bgColor = 'bg-orange-100';
    textColor = 'text-orange-800';
  }

  return (
    <div className={`${bgColor} rounded-lg p-3 text-center`}>
      <p className="text-xs text-gray-600 font-medium">{name}</p>
      <p className={`text-lg font-bold ${textColor}`}>{safeValue.toFixed(1)}</p>
      <p className={`text-xs font-semibold ${textColor}`}>{status}</p>
    </div>
  );
};
