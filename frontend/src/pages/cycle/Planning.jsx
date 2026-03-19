import React, { useState, useEffect } from 'react';
import { useActiveCycle, useCycleHistory } from '../../hooks/useCycle';
import { planningService, handleApiError } from '../../services/api';
import { toast } from 'react-toastify';
import { CROPS, SOIL_TYPES } from '../../utils/constants';

// SVG Icons
const ChartIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
  </svg>
);

const SEASONS = ['Kharif (Monsoon)', 'Rabi (Winter)', 'Zaid (Summer)', 'Summer'];
const SEASON_COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'];

export const Planning = () => {
  const { data: activeCycleData } = useActiveCycle();
  const { data: historyData } = useCycleHistory();
  
  // State for nutrient values (auto-populated from active cycle or last cycle)
  const [nutrients, setNutrients] = useState({
    N: 90,
    P: 42,
    K: 43,
    soilType: 'loamy',
  });
  
  // Selected crops for analysis
  const [selectedCrops, setSelectedCrops] = useState(['rice', 'wheat', 'maize']);
  
  // Results states
  const [compareResults, setCompareResults] = useState(null);
  const [riskResults, setRiskResults] = useState(null);
  const [rotationResults, setRotationResults] = useState(null);
  const [financialHistory, setFinancialHistory] = useState(null);
  
  // Loading states
  const [loadingCompare, setLoadingCompare] = useState(false);
  const [loadingRisk, setLoadingRisk] = useState(false);
  const [loadingRotation, setLoadingRotation] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // Active tab
  const [activeTab, setActiveTab] = useState('compare');
  
  // Auto-populate nutrients from active cycle or last completed cycle
  useEffect(() => {
    const activeCycle = activeCycleData?.cycle;
    const cycles = historyData?.cycles || [];
    
    if (activeCycle && activeCycle.current_nutrients) {
      setNutrients(prev => ({
        ...prev,
        N: Math.round(activeCycle.current_nutrients.N || 90),
        P: Math.round(activeCycle.current_nutrients.P || 42),
        K: Math.round(activeCycle.current_nutrients.K || 43),
        soilType: activeCycle.soil_type || 'loamy',
      }));
      toast.info('Using current season data');
    } else if (cycles.length > 0) {
      const lastCycle = cycles[0];
      if (lastCycle.final_n_kg_ha) {
        setNutrients(prev => ({
          ...prev,
          N: Math.round(parseFloat(lastCycle.final_n_kg_ha) || 90),
          P: Math.round(parseFloat(lastCycle.final_p_kg_ha) || 42),
          K: Math.round(parseFloat(lastCycle.final_k_kg_ha) || 43),
          soilType: lastCycle.soil_type || 'loamy',
        }));
        toast.info('Using data from your last season');
      }
    }
  }, [activeCycleData, historyData]);
  
  // Load financial history on mount
  useEffect(() => {
    fetchFinancialHistory();
  }, []);
  
  const fetchFinancialHistory = async () => {
    setLoadingHistory(true);
    try {
      const result = await planningService.getFinancialHistory();
      setFinancialHistory(result);
    } catch (error) {
      console.error('Failed to fetch financial history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };
  
  const handleCompareCrops = async () => {
    setLoadingCompare(true);
    try {
      // Use auto-fetch mode: Ensemble model gets top 3 crops automatically
      const result = await planningService.compareCropsAutoFetch(
        nutrients.N,
        nutrients.P,
        nutrients.K,
        nutrients.soilType,
        6.5, // ph
        25,  // temperature
        60,  // humidity
        100  // rainfall
      );
      
      setCompareResults(result);
      
      // Auto-populate selected crops from results if available
      if (result.crops && result.crops.length > 0) {
        const autoSelectedCrops = result.crops.map(opt => opt.crop);
        setSelectedCrops(autoSelectedCrops);
        toast.success(`Found ${result.crops.length} recommended crops suitable for your soil`);
      } else {
        toast.warning('No crops matched your soil conditions. Try adjusting nutrient levels.');
      }
    } catch (error) {
      toast.error(handleApiError(error));
    } finally {
      setLoadingCompare(false);
    }
  };
  
  const handleProfitRiskReport = async () => {
    // Use crops from previous analysis (auto-fetched top 3)
    const cropsToAnalyze = selectedCrops.length > 0 ? selectedCrops : ['rice', 'wheat', 'maize'];
    
    setLoadingRisk(true);
    try {
      const result = await planningService.profitRiskReport(
        nutrients.N,
        nutrients.P,
        nutrients.K,
        nutrients.soilType,
        600, // default rainfall
        cropsToAnalyze
      );
      setRiskResults(result);
      toast.success('Risk profile analyzed for your crops');
    } catch (error) {
      toast.error(handleApiError(error));
    } finally {
      setLoadingRisk(false);
    }
  };
  
  const handleSeasonalPlan = async () => {
    setLoadingRotation(true);
    try {
      const result = await planningService.seasonalRotationPlan(
        nutrients.N,
        nutrients.P,
        nutrients.K,
        nutrients.soilType,
        600, // default rainfall
        0 // default season index
      );
      setRotationResults(result);
      toast.success('Compared all crop rotation sequences for your field');
    } catch (error) {
      toast.error(handleApiError(error));
    } finally {
      setLoadingRotation(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            <ChartIcon className="w-10 h-10 inline-block mr-2 text-emerald-600" />
            Crop Planning & Analysis
          </h1>
          <p className="text-gray-600 mt-2">
            AI-powered crop recommendations, risk analysis, and rotation planning
          </p>
        </div>
        
        {/* Nutrient Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Current Soil Status</h2>
          <p className="text-sm text-gray-500 mb-4">
            Values auto-filled from your current season or last one. Edit if you've added fertilizer recently.
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* N */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">N (kg/ha)</label>
              <input
                type="number"
                value={nutrients.N}
                onChange={(e) => setNutrients({...nutrients, N: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
            {/* P */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">P (kg/ha)</label>
              <input
                type="number"
                value={nutrients.P}
                onChange={(e) => setNutrients({...nutrients, P: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
            {/* K */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">K (kg/ha)</label>
              <input
                type="number"
                value={nutrients.K}
                onChange={(e) => setNutrients({...nutrients, K: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
            {/* Soil Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Soil Type</label>
              <select
                value={nutrients.soilType}
                onChange={(e) => setNutrients({...nutrients, soilType: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                {SOIL_TYPES.map(soil => (
                  <option key={soil} value={soil}>{soil.charAt(0).toUpperCase() + soil.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          {[
            { id: 'compare', label: 'Yield Analysis', icon: '🌾' },
            { id: 'risk', label: 'Risk Assessment', icon: '📊' },
            { id: 'rotation', label: 'Rotation Strategy', icon: '🔄' },
            { id: 'history', label: 'Financial Summary', icon: '💰' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 font-medium text-sm transition ${
                activeTab === tab.id
                  ? 'text-emerald-600 border-b-2 border-emerald-500 bg-emerald-50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
        
        {/* Compare Crops Tab */}
        {activeTab === 'compare' && (
          <div className="space-y-6">
            {/* Auto-Analysis Section */}
            <div className="bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg shadow-md p-6 border border-emerald-200">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">🎯 Auto-Fetch Top 3 Crops</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    The AI Ensemble Model will automatically identify the 3 best crop options for your current soil conditions. 
                    We'll predict nutrient depletion over 30 days for each crop to help you make an informed decision.
                  </p>
                  <button
                    onClick={handleCompareCrops}
                    disabled={loadingCompare}
                    className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50 flex items-center gap-2"
                  >
                    {loadingCompare ? (
                      <>
                        <span className="animate-spin">⏳</span>
                        Checking crops...
                      </>
                    ) : (
                      <>
                        <span>✨</span>
                        Analyze Yield Potential
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
            
            {/* Results */}
            {compareResults && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">Top 3 Crop Analysis</h3>
                    <p className="text-sm text-gray-500">30-day nutrient depletion prediction</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500">
                      Analyzed: {compareResults.crops?.length || 0} crops
                    </span>
                  </div>
                </div>
                
                {/* Results Table - Simplified */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Crop</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Initial N</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Initial P</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Initial K</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Final N</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Final P</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Final K</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700 bg-red-50">Depletion N</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700 bg-red-50">Depletion P</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700 bg-red-50">Depletion K</th>
                      </tr>
                    </thead>
                    <tbody>
                      {compareResults.crops?.map((opt, idx) => (
                        <tr key={idx} className={`border-b border-gray-100 ${idx === 0 ? 'bg-emerald-50' : ''}`}>
                          <td className="py-3 px-4 font-medium text-gray-900 capitalize">
                            {idx === 0 && <span className="mr-2">🏆</span>}
                            {opt.crop}
                          </td>
                          <td className="py-3 px-4 text-center text-blue-600">{opt.initial?.N?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-green-600">{opt.initial?.P?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-orange-600">{opt.initial?.K?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-blue-500">{opt.final?.N?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-green-500">{opt.final?.P?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-orange-500">{opt.final?.K?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center font-semibold text-red-600 bg-red-50">{opt.depletion?.N?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center font-semibold text-red-600 bg-red-50">{opt.depletion?.P?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center font-semibold text-red-600 bg-red-50">{opt.depletion?.K?.toFixed(1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Visual Chart - Depletion Comparison */}
                <div className="mt-6">
                  <h4 className="font-semibold text-gray-800 mb-3">Nutrient Depletion Comparison (kg/ha)</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['N', 'P', 'K'].map((nutrient, nIdx) => (
                      <div key={nutrient} className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm font-medium text-gray-600 mb-2">
                          {nutrient === 'N' ? 'Nitrogen Depletion' : nutrient === 'P' ? 'Phosphorus Depletion' : 'Potassium Depletion'}
                        </p>
                        <div className="space-y-2">
                          {compareResults.crops?.map((opt, idx) => {
                            const depletion = opt.depletion?.[nutrient] || 0;
                            const maxDepletion = Math.max(...compareResults.crops.map(c => c.depletion?.[nutrient] || 0));
                            const percent = maxDepletion > 0 ? (depletion / maxDepletion) * 100 : 0;
                            return (
                              <div key={idx} className="flex items-center gap-2">
                                <span className="w-16 text-xs text-gray-600 capitalize truncate">{opt.crop}</span>
                                <div className="flex-1 bg-gray-200 rounded-full h-3">
                                  <div 
                                    className={`h-3 rounded-full ${
                                      nIdx === 0 ? 'bg-blue-500' : nIdx === 1 ? 'bg-green-500' : 'bg-orange-500'
                                    }`}
                                    style={{ width: `${percent}%` }}
                                  />
                                </div>
                                <span className="w-12 text-xs text-gray-600 text-right">{depletion.toFixed(1)}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Risk Analysis Tab */}
        {activeTab === 'risk' && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg shadow-md p-6 border border-blue-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">📊 Monte Carlo Risk Assessment</h3>
              <p className="text-sm text-gray-600 mb-4">
                Simulates 2000 scenarios with varying rainfall and market prices to assess profit risk and variability.
              </p>
              
              {selectedCrops.length > 0 ? (
                <div className="mb-4 p-3 bg-blue-100 border border-blue-300 rounded-lg">
                  <p className="text-sm font-medium text-blue-900">
                    Analyzing crops: <span className="font-semibold">{selectedCrops.join(', ')}</span>
                  </p>
                </div>
              ) : (
                <div className="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    💡 Start with "Yield Analysis" to see which crops work best, then check their risk profile.
                  </p>
                </div>
              )}
              
              <button
                onClick={handleProfitRiskReport}
                disabled={loadingRisk}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50 flex items-center gap-2"
              >
                {loadingRisk ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    Analyzing Risks...
                  </>
                ) : (
                  <>
                    <span>🎲</span>
                    Analyze Risk Profile
                  </>
                )}
              </button>
            </div>
            
            {riskResults && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Profiles</h3>
                
                {/* Risk Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  {riskResults.risk_profiles?.map((profile, idx) => (
                    <div key={idx} className={`rounded-lg p-4 border-2 ${
                      idx === 0 ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 bg-white'
                    }`}>
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-bold text-gray-900 capitalize text-lg">{profile.crop}</h4>
                        {idx === 0 && <span className="text-emerald-600 text-xl">🏆</span>}
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Mean Profit:</span>
                          <span className="font-semibold text-emerald-600">₹{profile.mean_profit?.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Std Dev:</span>
                          <span className="font-semibold text-gray-800">±₹{profile.std_profit?.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Min / Max:</span>
                          <span className="font-semibold text-gray-800">
                            ₹{profile.min_profit?.toLocaleString()} - ₹{profile.max_profit?.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Risk Summary Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Crop</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Mean Profit</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Std Dev</th>
                      </tr>
                    </thead>
                    <tbody>
                      {riskResults.risk_profiles?.map((profile, idx) => (
                        <tr key={idx} className="border-b border-gray-100">
                          <td className="py-3 px-4 font-medium text-gray-900 capitalize">{profile.crop}</td>
                          <td className="py-3 px-4 text-center text-emerald-600 font-semibold">
                            ₹{profile.mean_profit?.toLocaleString()}
                          </td>
                          <td className="py-3 px-4 text-center text-gray-600">
                            ±₹{profile.std_profit?.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Rotation Plan Tab */}
        {activeTab === 'rotation' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Crop Rotation Optimizer</h3>
              <p className="text-sm text-gray-500 mb-4">
                Compare all possible 3-crop rotation sequences. See profit returns and nutrient depletion for each order.
              </p>
              
              <button
                onClick={handleSeasonalPlan}
                disabled={loadingRotation}
                className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50"
              >
                {loadingRotation ? 'Analyzing Rotations...' : 'Analyze Rotation Plans'}
              </button>
            </div>

            {loadingRotation && (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-500 mx-auto mb-3"></div>
                <p className="text-gray-600">Simulating crop rotation sequences...</p>
              </div>
            )}
            
            {rotationResults && rotationResults.rotation_sequences && rotationResults.rotation_sequences.length > 0 && (
              <div className="space-y-4">
                {/* Top Crops Info */}
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Top Recommended Crops:</p>
                  <div className="flex gap-2 flex-wrap">
                    {rotationResults.top_3_crops?.map((crop, idx) => (
                      <span key={idx} className="bg-white px-3 py-1 rounded-full text-sm font-semibold text-purple-600 border border-purple-200">
                        {idx + 1}. {crop}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Rotation Sequences Comparison */}
                <div className="bg-white rounded-lg shadow-md overflow-hidden">
                  <div className="p-6 border-b border-gray-200">
                    <h4 className="text-lg font-semibold text-gray-900">Rotation Sequences ({rotationResults.rotation_sequences.length} options)</h4>
                  </div>

                  <div className="space-y-4 p-6">
                    {rotationResults.rotation_sequences.map((result, idx) => (
                      <div key={idx} className={`rounded-lg border-2 p-4 ${
                        idx === 0 ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 bg-white'
                      }`}>
                        {/* Sequence Title */}
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <span className="text-2xl font-bold text-gray-600">#{idx + 1}</span>
                            <div>
                              <div className="flex items-center gap-2">
                                {result.sequence.map((crop, cidx) => (
                                  <div key={cidx} className="flex items-center">
                                    <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold capitalize">
                                      {crop}
                                    </span>
                                    {cidx < result.sequence.length - 1 && (
                                      <span className="mx-2 text-gray-400 text-xl">→</span>
                                    )}
                                  </div>
                                ))}
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                Season 1 → Season 2 → Season 3
                              </p>
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            {idx === 0 && <span className="text-emerald-600 text-lg font-bold">🏆 Top Ranked</span>}
                            <div className="flex gap-2">
                              <div className="text-center">
                                <p className="text-xs text-gray-500">Q-Score</p>
                                <p className="font-bold text-sm text-blue-600">{result.q_learning_score || 50}/100</p>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Profit Info */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 p-4 bg-white bg-opacity-50 rounded-lg">
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Total Profit (3 seasons)</p>
                            <p className="text-2xl font-bold text-emerald-600">
                              ₹{result.total_profit?.toLocaleString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Profit by Season</p>
                            <div className="flex gap-2">
                              {result.profit_by_season?.map((profit, pidx) => (
                                <div key={pidx} className="flex-1 bg-emerald-100 rounded px-2 py-1 text-center">
                                  <p className="text-xs text-emerald-700">S{pidx + 1}</p>
                                  <p className="font-semibold text-emerald-800 text-sm">
                                    ₹{(profit / 1000).toFixed(0)}K
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* Nutrient Depletion Info */}
                        <div className="grid grid-cols-3 gap-3">
                          <div className="bg-blue-50 rounded-lg p-3 text-center">
                            <p className="text-xs text-blue-600 font-semibold mb-1">Nitrogen (N)</p>
                            <p className="text-sm text-gray-600">
                              {result.initial_nutrients?.N} → {result.final_nutrients?.N}
                            </p>
                            <p className="text-lg font-bold text-red-600">
                              -{result.total_depletion?.N}
                            </p>
                            <p className="text-xs text-gray-500">
                              ({result.total_depletion_percent?.N}% depleted)
                            </p>
                          </div>
                          <div className="bg-green-50 rounded-lg p-3 text-center">
                            <p className="text-xs text-green-600 font-semibold mb-1">Phosphorus (P)</p>
                            <p className="text-sm text-gray-600">
                              {result.initial_nutrients?.P} → {result.final_nutrients?.P}
                            </p>
                            <p className="text-lg font-bold text-red-600">
                              -{result.total_depletion?.P}
                            </p>
                            <p className="text-xs text-gray-500">
                              ({result.total_depletion_percent?.P}% depleted)
                            </p>
                          </div>
                          <div className="bg-yellow-50 rounded-lg p-3 text-center">
                            <p className="text-xs text-yellow-600 font-semibold mb-1">Potassium (K)</p>
                            <p className="text-sm text-gray-600">
                              {result.initial_nutrients?.K} → {result.final_nutrients?.K}
                            </p>
                            <p className="text-lg font-bold text-red-600">
                              -{result.total_depletion?.K}
                            </p>
                            <p className="text-xs text-gray-500">
                              ({result.total_depletion_percent?.K}% depleted)
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendation */}
                <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg p-4 border border-emerald-200">
                  <p className="text-sm font-semibold text-gray-700 mb-2">💡 Recommendation:</p>
                  <p className="text-sm text-gray-600">
                    Sequence #1 ({rotationResults.rotation_sequences[0].sequence.join(' → ')}) ranks best based on{' '}
                    <span className="font-bold">70% profit</span> + <span className="font-bold">30% soil health</span>.{' '}
                    Profit: <span className="font-bold text-emerald-600">₹{rotationResults.rotation_sequences[0].total_profit?.toLocaleString()}</span>,{' '}
                    Q-Learning Score: <span className="font-bold text-blue-600">{rotationResults.rotation_sequences[0].q_learning_score || 50}/100</span>
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Financial History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Financial History</h3>
                  <p className="text-sm text-gray-500">Track profits, investments, and expenses across cycles</p>
                </div>
                <button
                  onClick={fetchFinancialHistory}
                  disabled={loadingHistory}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg transition disabled:opacity-50"
                >
                  {loadingHistory ? 'Loading...' : 'Refresh'}
                </button>
              </div>
              
              {loadingHistory ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500 mx-auto"></div>
                </div>
              ) : financialHistory?.records?.length > 0 ? (
                <>
                  {/* Summary Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-emerald-50 rounded-lg p-4">
                      <p className="text-sm text-emerald-600">Total Profit</p>
                      <p className="text-2xl font-bold text-emerald-800">
                        ₹{financialHistory.summary?.total_profit?.toLocaleString() || 0}
                      </p>
                    </div>
                    <div className="bg-red-50 rounded-lg p-4">
                      <p className="text-sm text-red-600">Total Investment</p>
                      <p className="text-2xl font-bold text-red-800">
                        ₹{financialHistory.summary?.total_investment?.toLocaleString() || 0}
                      </p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-sm text-blue-600">Net Return</p>
                      <p className="text-2xl font-bold text-blue-800">
                        ₹{financialHistory.summary?.net_return?.toLocaleString() || 0}
                      </p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-purple-600">Total Cycles</p>
                      <p className="text-2xl font-bold text-purple-800">
                        {financialHistory.records?.length || 0}
                      </p>
                    </div>
                  </div>
                  
                  {/* History Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-200 bg-gray-50">
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Cycle</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Crop</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Duration</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Seed Cost</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Fertilizer</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Labour</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Total Cost</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Revenue</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Profit</th>
                        </tr>
                      </thead>
                      <tbody>
                        {financialHistory.records.map((record, idx) => (
                          <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4 text-gray-600">#{record.cycle_id}</td>
                            <td className="py-3 px-4 font-medium text-gray-900 capitalize">{record.crop_name}</td>
                            <td className="py-3 px-4 text-gray-600">
                              {record.start_date ? new Date(record.start_date).toLocaleDateString() : '-'} - 
                              {record.end_date ? new Date(record.end_date).toLocaleDateString() : 'Active'}
                            </td>
                            <td className="py-3 px-4 text-right text-red-600">
                              ₹{record.seed_cost?.toLocaleString() || 0}
                            </td>
                            <td className="py-3 px-4 text-right text-red-600">
                              ₹{record.fertilizer_cost?.toLocaleString() || 0}
                            </td>
                            <td className="py-3 px-4 text-right text-red-600">
                              ₹{record.labour_cost?.toLocaleString() || 0}
                            </td>
                            <td className="py-3 px-4 text-right text-red-700 font-semibold">
                              ₹{record.total_cost?.toLocaleString() || 0}
                            </td>
                            <td className="py-3 px-4 text-right text-emerald-600 font-semibold">
                              ₹{record.revenue?.toLocaleString() || 0}
                            </td>
                            <td className={`py-3 px-4 text-right font-bold ${
                              record.profit >= 0 ? 'text-emerald-600' : 'text-red-600'
                            }`}>
                              ₹{record.profit?.toLocaleString() || 0}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-5xl mb-3">📊</p>
                  <p className="text-gray-500">No financial history available yet.</p>
                  <p className="text-sm text-gray-400 mt-2">Complete crop cycles to see your financial data here.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
