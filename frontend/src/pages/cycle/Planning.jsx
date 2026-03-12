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
    expectedRainfall: 600,
    seasonIndex: 0,
  });
  
  // Selected crops for analysis
  const [selectedCrops, setSelectedCrops] = useState(['rice', 'wheat', 'maize']);
  const [numSeasons, setNumSeasons] = useState(5);
  
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
      toast.info('Nutrients loaded from active cycle');
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
        toast.info('Nutrients loaded from last completed cycle');
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
    if (selectedCrops.length === 0) {
      toast.warning('Please select at least one crop');
      return;
    }
    
    setLoadingCompare(true);
    try {
      const result = await planningService.compareCrops(
        nutrients.N,
        nutrients.P,
        nutrients.K,
        nutrients.soilType,
        nutrients.seasonIndex,
        nutrients.expectedRainfall,
        selectedCrops
      );
      setCompareResults(result);
      toast.success('Crop comparison complete!');
    } catch (error) {
      toast.error(handleApiError(error));
    } finally {
      setLoadingCompare(false);
    }
  };
  
  const handleProfitRiskReport = async () => {
    if (selectedCrops.length === 0) {
      toast.warning('Please select at least one crop');
      return;
    }
    
    setLoadingRisk(true);
    try {
      const result = await planningService.profitRiskReport(
        nutrients.N,
        nutrients.P,
        nutrients.K,
        nutrients.soilType,
        nutrients.expectedRainfall,
        selectedCrops
      );
      setRiskResults(result);
      toast.success('Risk analysis complete!');
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
        nutrients.expectedRainfall,
        nutrients.seasonIndex,
        numSeasons
      );
      setRotationResults(result);
      toast.success('Rotation plan generated!');
    } catch (error) {
      toast.error(handleApiError(error));
    } finally {
      setLoadingRotation(false);
    }
  };
  
  const toggleCropSelection = (crop) => {
    setSelectedCrops(prev => 
      prev.includes(crop) 
        ? prev.filter(c => c !== crop)
        : [...prev, crop]
    );
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
            Values auto-loaded from your active cycle or last completed cycle. Adjust if needed.
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
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
            {/* Expected Rainfall */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Rainfall (mm)</label>
              <input
                type="number"
                value={nutrients.expectedRainfall}
                onChange={(e) => setNutrients({...nutrients, expectedRainfall: parseFloat(e.target.value) || 0})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
            {/* Season */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Season</label>
              <select
                value={nutrients.seasonIndex}
                onChange={(e) => setNutrients({...nutrients, seasonIndex: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                {SEASONS.map((season, idx) => (
                  <option key={idx} value={idx}>{season}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          {[
            { id: 'compare', label: 'Compare Crops', icon: '🌾' },
            { id: 'risk', label: 'Risk Analysis', icon: '📊' },
            { id: 'rotation', label: 'Rotation Plan', icon: '🔄' },
            { id: 'history', label: 'Financial History', icon: '💰' },
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
            {/* Crop Selection */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Crops to Compare</h3>
              <div className="flex flex-wrap gap-2 mb-4">
                {CROPS.slice(0, 12).map(crop => (
                  <button
                    key={crop}
                    onClick={() => toggleCropSelection(crop)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                      selectedCrops.includes(crop)
                        ? 'bg-emerald-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {crop.charAt(0).toUpperCase() + crop.slice(1)}
                  </button>
                ))}
              </div>
              <button
                onClick={handleCompareCrops}
                disabled={loadingCompare}
                className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50"
              >
                {loadingCompare ? 'Analyzing...' : 'Compare Crops (LSTM + Formula)'}
              </button>
            </div>
            
            {/* Results */}
            {compareResults && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Comparison Results</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    compareResults.prediction_method === 'lstm_blended' 
                      ? 'bg-purple-100 text-purple-800' 
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {compareResults.prediction_method === 'lstm_blended' 
                      ? '60% LSTM + 40% Formula' 
                      : 'Formula Only'}
                  </span>
                </div>
                
                {/* Results Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Crop</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Season</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Final N</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Final P</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Final K</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Immediate Reward</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Total Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {compareResults.options?.map((opt, idx) => (
                        <tr key={idx} className={`border-b border-gray-100 ${idx === 0 ? 'bg-emerald-50' : ''}`}>
                          <td className="py-3 px-4 font-medium text-gray-900 capitalize">
                            {idx === 0 && <span className="mr-2">🏆</span>}
                            {opt.crop}
                          </td>
                          <td className="py-3 px-4 text-center text-gray-600 capitalize">{opt.season}</td>
                          <td className="py-3 px-4 text-center text-blue-600 font-semibold">{opt.final_state?.N?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-green-600 font-semibold">{opt.final_state?.P?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-orange-600 font-semibold">{opt.final_state?.K?.toFixed(1)}</td>
                          <td className="py-3 px-4 text-center text-gray-900">₹{opt.immediate_reward?.toLocaleString()}</td>
                          <td className="py-3 px-4 text-center text-emerald-600 font-bold">₹{opt.total_value?.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Visual Chart - Nutrient Comparison */}
                <div className="mt-6">
                  <h4 className="font-semibold text-gray-800 mb-3">Nutrient Depletion Comparison</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {['N', 'P', 'K'].map((nutrient, nIdx) => (
                      <div key={nutrient} className="bg-gray-50 rounded-lg p-4">
                        <p className="text-sm font-medium text-gray-600 mb-2">
                          {nutrient === 'N' ? 'Nitrogen' : nutrient === 'P' ? 'Phosphorus' : 'Potassium'}
                        </p>
                        <div className="space-y-2">
                          {compareResults.options?.map((opt, idx) => {
                            const initial = nutrients[nutrient];
                            const final = opt.final_state?.[nutrient] || 0;
                            const percent = Math.max(0, Math.min(100, (final / initial) * 100));
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
                                <span className="w-10 text-xs text-gray-600">{final.toFixed(0)}</span>
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
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Monte Carlo Risk Analysis</h3>
              <p className="text-sm text-gray-500 mb-4">
                Simulates 2000 scenarios with varying rainfall and market prices
              </p>
              <div className="flex flex-wrap gap-2 mb-4">
                {CROPS.slice(0, 12).map(crop => (
                  <button
                    key={crop}
                    onClick={() => toggleCropSelection(crop)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                      selectedCrops.includes(crop)
                        ? 'bg-emerald-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {crop.charAt(0).toUpperCase() + crop.slice(1)}
                  </button>
                ))}
              </div>
              <button
                onClick={handleProfitRiskReport}
                disabled={loadingRisk}
                className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50"
              >
                {loadingRisk ? 'Analyzing...' : 'Generate Risk Report'}
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
                        <div className="flex justify-between">
                          <span className="text-gray-600">5th - 95th %ile:</span>
                          <span className="font-semibold text-gray-800">
                            ₹{profile.percentile_5?.toLocaleString()} - ₹{profile.percentile_95?.toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Loss Probability:</span>
                          <span className={`font-semibold ${profile.prob_loss > 0.1 ? 'text-red-600' : 'text-green-600'}`}>
                            {(profile.prob_loss * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Sharpe Ratio:</span>
                          <span className="font-semibold text-blue-600">{profile.sharpe_ratio?.toFixed(2)}</span>
                        </div>
                      </div>
                      
                      {/* Risk Score Bar */}
                      <div className="mt-4">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span>Risk-Adjusted Score</span>
                          <span>{(profile.risk_adjusted_score * 100).toFixed(0)}%</span>
                        </div>
                        <div className="bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              profile.risk_adjusted_score > 0.8 ? 'bg-emerald-500' :
                              profile.risk_adjusted_score > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${profile.risk_adjusted_score * 100}%` }}
                          />
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
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Loss Prob</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Sharpe</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Risk Score</th>
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
                          <td className={`py-3 px-4 text-center font-semibold ${
                            profile.prob_loss > 0.1 ? 'text-red-600' : 'text-green-600'
                          }`}>
                            {(profile.prob_loss * 100).toFixed(1)}%
                          </td>
                          <td className="py-3 px-4 text-center text-blue-600 font-semibold">
                            {profile.sharpe_ratio?.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                              profile.risk_adjusted_score > 0.8 ? 'bg-emerald-100 text-emerald-800' :
                              profile.risk_adjusted_score > 0.6 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {(profile.risk_adjusted_score * 100).toFixed(0)}%
                            </span>
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
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Q-Learning Rotation Planner</h3>
              <p className="text-sm text-gray-500 mb-4">
                AI-optimized crop sequence for maximum long-term profit and soil health
              </p>
              
              <div className="flex items-center gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Number of Seasons</label>
                  <select
                    value={numSeasons}
                    onChange={(e) => setNumSeasons(parseInt(e.target.value))}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  >
                    {[3, 4, 5, 6, 7, 8].map(n => (
                      <option key={n} value={n}>{n} Seasons</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <button
                onClick={handleSeasonalPlan}
                disabled={loadingRotation}
                className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50"
              >
                {loadingRotation ? 'Planning...' : 'Generate Optimal Rotation'}
              </button>
            </div>
            
            {rotationResults && rotationResults.plan && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Optimal Rotation Plan</h3>
                  <div className="bg-emerald-100 text-emerald-800 px-4 py-2 rounded-lg font-semibold">
                    Total Reward: ₹{rotationResults.plan.total_reward?.toLocaleString()}
                  </div>
                </div>
                
                {/* Rotation Timeline */}
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                  
                  <div className="space-y-6">
                    {rotationResults.plan.seasons?.map((season, idx) => (
                      <div key={idx} className="relative pl-12">
                        {/* Timeline Dot */}
                        <div 
                          className="absolute left-2 top-1 w-5 h-5 rounded-full border-2 border-white"
                          style={{ backgroundColor: SEASON_COLORS[idx % 4] }}
                        />
                        
                        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <span 
                                className="px-3 py-1 rounded-full text-white text-xs font-semibold"
                                style={{ backgroundColor: SEASON_COLORS[idx % 4] }}
                              >
                                Season {season.season_num}
                              </span>
                              <span className="text-sm text-gray-500 capitalize">{season.season_name}</span>
                            </div>
                            <span className="font-semibold text-emerald-600">₹{season.reward?.toLocaleString()}</span>
                          </div>
                          
                          <div className="flex items-center gap-6">
                            <div>
                              <p className="text-2xl font-bold text-gray-900 capitalize">{season.crop}</p>
                            </div>
                            
                            <div className="flex-1 grid grid-cols-3 gap-4 text-center">
                              <div className="bg-white rounded p-2">
                                <p className="text-xs text-gray-500">Start NPK</p>
                                <p className="font-semibold text-sm">
                                  {season.start_state?.N?.toFixed(0)} / {season.start_state?.P?.toFixed(0)} / {season.start_state?.K?.toFixed(0)}
                                </p>
                              </div>
                              <div className="text-2xl text-gray-400 flex items-center justify-center">→</div>
                              <div className="bg-white rounded p-2">
                                <p className="text-xs text-gray-500">End NPK</p>
                                <p className="font-semibold text-sm">
                                  {season.end_state?.N?.toFixed(0)} / {season.end_state?.P?.toFixed(0)} / {season.end_state?.K?.toFixed(0)}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Summary */}
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h4 className="font-semibold text-gray-800 mb-3">Rotation Summary</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-blue-600">Total Seasons</p>
                      <p className="text-2xl font-bold text-blue-800">{rotationResults.plan.seasons?.length}</p>
                    </div>
                    <div className="bg-emerald-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-emerald-600">Total Profit</p>
                      <p className="text-2xl font-bold text-emerald-800">₹{rotationResults.plan.total_reward?.toLocaleString()}</p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-purple-600">Avg/Season</p>
                      <p className="text-2xl font-bold text-purple-800">
                        ₹{Math.round(rotationResults.plan.total_reward / (rotationResults.plan.seasons?.length || 1)).toLocaleString()}
                      </p>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-orange-600">Unique Crops</p>
                      <p className="text-2xl font-bold text-orange-800">
                        {new Set(rotationResults.plan.seasons?.map(s => s.crop)).size}
                      </p>
                    </div>
                  </div>
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
