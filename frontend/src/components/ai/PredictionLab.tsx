import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Select } from '@/components/ui/select';
import { COLLEGES, AUTOMATION_SYSTEMS } from '@/lib/constants';
import { apiClient } from '@/lib/api';
import type { PredictionRequest, SatisfactionPrediction, EfficiencyPrediction } from '@/types';
import { Brain, TrendingUp, Target, Zap, BarChart3, PieChart } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

const COLORS = ['#ef4444', '#f59e0b', '#10b981'];

export function PredictionLab() {
  const [activeTab, setActiveTab] = useState<'satisfaction' | 'efficiency' | 'scenario' | 'recommendations'>('satisfaction');
  const [satisfactionPrediction, setSatisfactionPrediction] = useState<SatisfactionPrediction | null>(null);
  const [efficiencyPrediction, setEfficiencyPrediction] = useState<EfficiencyPrediction | null>(null);
  const [scenarioResults, setScenarioResults] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<PredictionRequest>({
    infrastructureScore: 3,
    barrierScore: 3,
    collegeId: '1',
    automationSystem: 'None',
    awarenessLevel: 5,
  });

  const [scenarioData, setScenarioData] = useState({
    current: { ...formData },
    proposed: { 
      infrastructureScore: 4,
      barrierScore: 2,
      collegeId: '1',
      automationSystem: 'KOHA',
      awarenessLevel: 7,
    }
  });

  const handlePredictSatisfaction = async () => {
    setLoading(true);
    try {
      const prediction = await apiClient.predictSatisfaction(formData);
      setSatisfactionPrediction(prediction);
    } catch (error) {
      console.error('Prediction error:', error);
      toast.error('Failed to generate prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePredictEfficiency = async () => {
    setLoading(true);
    try {
      const prediction = await apiClient.predictEfficiency(formData);
      setEfficiencyPrediction(prediction);
    } catch (error) {
      console.error('Prediction error:', error);
      toast.error('Failed to generate prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioSimulation = async () => {
    setLoading(true);
    try {
      const results = await apiClient.simulateScenario(scenarioData.current, scenarioData.proposed);
      setScenarioResults(results);
    } catch (error) {
      console.error('Scenario simulation error:', error);
      toast.error('Failed to simulate scenario. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGetRecommendations = async () => {
    setLoading(true);
    try {
      const response = await apiClient.getRecommendations(formData.collegeId);
      setRecommendations(response.recommendations || []);
    } catch (error) {
      console.error('Recommendations error:', error);
      toast.error('Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderInputForm = (data: PredictionRequest, onChange: (data: PredictionRequest) => void, title: string = "Input Parameters") => (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Slider
          label="Infrastructure Score"
          value={data.infrastructureScore}
          onValueChange={(val) => onChange({ ...data, infrastructureScore: val })}
          min={1}
          max={5}
        />
        <Slider
          label="Barrier Score"
          value={data.barrierScore}
          onValueChange={(val) => onChange({ ...data, barrierScore: val })}
          min={1}
          max={5}
        />
        <div>
          <label className="mb-2 block text-sm font-medium">College</label>
          <Select
            options={COLLEGES.map((c) => ({ value: c.id, label: c.name }))}
            value={data.collegeId}
            onChange={(value) => onChange({ ...data, collegeId: value })}
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium">Automation System</label>
          <Select
            options={AUTOMATION_SYSTEMS.map((s) => ({ value: s, label: s }))}
            value={data.automationSystem}
            onChange={(value) => onChange({ ...data, automationSystem: value })}
          />
        </div>
        <Slider
          label="Awareness Level"
          value={data.awarenessLevel}
          onValueChange={(val) => onChange({ ...data, awarenessLevel: val })}
          min={1}
          max={10}
        />
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Prediction Lab</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Advanced AI-powered predictions and scenario analysis
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2">
        <Button
          variant={activeTab === 'satisfaction' ? 'default' : 'outline'}
          onClick={() => setActiveTab('satisfaction')}
        >
          <Brain className="mr-2 h-4 w-4" />
          Satisfaction
        </Button>
        <Button
          variant={activeTab === 'efficiency' ? 'default' : 'outline'}
          onClick={() => setActiveTab('efficiency')}
        >
          <TrendingUp className="mr-2 h-4 w-4" />
          Efficiency
        </Button>
        <Button
          variant={activeTab === 'scenario' ? 'default' : 'outline'}
          onClick={() => setActiveTab('scenario')}
        >
          <Target className="mr-2 h-4 w-4" />
          Scenario
        </Button>
        <Button
          variant={activeTab === 'recommendations' ? 'default' : 'outline'}
          onClick={() => setActiveTab('recommendations')}
        >
          <Zap className="mr-2 h-4 w-4" />
          Recommendations
        </Button>
      </div>

      {/* Satisfaction Prediction */}
      {activeTab === 'satisfaction' && (
        <div className="grid gap-6 md:grid-cols-2">
          {renderInputForm(formData, setFormData)}
          
          <div className="space-y-4">
            <Button onClick={handlePredictSatisfaction} disabled={loading} className="w-full">
              {loading ? 'Predicting...' : 'Predict Satisfaction'}
            </Button>

            {satisfactionPrediction && (
              <Card>
                <CardHeader>
                  <CardTitle>Prediction Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="mb-2 text-sm text-gray-600">Predicted Category</div>
                    <div
                      className={`inline-block rounded-full px-4 py-2 text-lg font-semibold ${
                        satisfactionPrediction.prediction === 'High'
                          ? 'bg-green-100 text-green-800'
                          : satisfactionPrediction.prediction === 'Medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {satisfactionPrediction.prediction}
                    </div>
                  </div>
                  
                  <div>
                    <div className="mb-2 text-sm text-gray-600">Confidence Score</div>
                    <div className="h-4 w-full overflow-hidden rounded-full bg-gray-200">
                      <motion.div
                        className="h-full bg-blue-600"
                        initial={{ width: 0 }}
                        animate={{ width: `${satisfactionPrediction.confidence * 100}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                    <div className="mt-1 text-sm text-gray-600">
                      {satisfactionPrediction.confidence ? (satisfactionPrediction.confidence * 100).toFixed(1) : 'N/A'}%
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 text-sm text-gray-600">Probability Distribution</div>
                    <ResponsiveContainer width="100%" height={200}>
                      <RechartsPieChart>
                        <Pie
                          data={satisfactionPrediction.probabilities ? Object.entries(satisfactionPrediction.probabilities).map(([name, value]) => ({
                            name,
                            value: value * 100,
                          })) : []}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value?.toFixed(1) || 'N/A'}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {satisfactionPrediction.probabilities ? Object.keys(satisfactionPrediction.probabilities).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index]} />
                          )) : null}
                        </Pie>
                        <Tooltip />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </div>

                  {satisfactionPrediction.featureImportance && satisfactionPrediction.featureImportance.length > 0 && (
                    <div>
                      <div className="mb-2 text-sm text-gray-600">Key Influencing Factors</div>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart
                          data={satisfactionPrediction.featureImportance
                            ?.filter(item => item && typeof item.importance === 'number')
                            ?.sort((a, b) => (b.importance || 0) - (a.importance || 0))
                            ?.slice(0, 5) || []}
                        >
                          <XAxis dataKey="feature" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="importance" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Efficiency Prediction */}
      {activeTab === 'efficiency' && (
        <div className="grid gap-6 md:grid-cols-2">
          {renderInputForm(formData, setFormData)}
          
          <div className="space-y-4">
            <Button onClick={handlePredictEfficiency} disabled={loading} className="w-full">
              {loading ? 'Predicting...' : 'Predict Efficiency'}
            </Button>

            {efficiencyPrediction && (
              <Card>
                <CardHeader>
                  <CardTitle>Efficiency Prediction</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-blue-600">
                      {efficiencyPrediction.predictedScore?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-600">Predicted Efficiency Score</div>
                  </div>
                  
                  <div>
                    <div className="mb-2 text-sm text-gray-600">Confidence Interval</div>
                    <div className="flex justify-between items-center bg-gray-100 p-3 rounded">
                      <span className="font-medium">{efficiencyPrediction.confidenceInterval?.lower?.toFixed(1) || 'N/A'}</span>
                      <span className="text-sm text-gray-500">to</span>
                      <span className="font-medium">{efficiencyPrediction.confidenceInterval?.upper?.toFixed(1) || 'N/A'}</span>
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 text-sm text-gray-600">Improvement Potential</div>
                    <div className="text-2xl font-bold text-green-600">
                      +{efficiencyPrediction.improvementPotential?.toFixed(1) || 'N/A'} points
                    </div>
                  </div>

                  {efficiencyPrediction.suggestions && efficiencyPrediction.suggestions.length > 0 && (
                    <div>
                      <div className="mb-2 text-sm text-gray-600">Improvement Suggestions</div>
                      <ul className="space-y-2">
                        {efficiencyPrediction.suggestions.map((suggestion, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                            <span className="text-sm text-gray-700">{suggestion}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Scenario Simulation */}
      {activeTab === 'scenario' && (
        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {renderInputForm(scenarioData.current, (data) => setScenarioData({...scenarioData, current: data}), "Current State")}
            {renderInputForm(scenarioData.proposed, (data) => setScenarioData({...scenarioData, proposed: data}), "Proposed State")}
          </div>
          
          <div className="text-center">
            <Button onClick={handleScenarioSimulation} disabled={loading} size="lg">
              {loading ? 'Simulating...' : 'Run Scenario Simulation'}
            </Button>
          </div>

          {scenarioResults && (
            <Card>
              <CardHeader>
                <CardTitle>Scenario Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600">
                      {scenarioResults.currentScore?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-500">Current Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {scenarioResults.predictedScore?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-500">Predicted Score</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      +{scenarioResults.improvement?.toFixed(1) || 'N/A'}
                    </div>
                    <div className="text-sm text-gray-500">Improvement</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {scenarioResults.improvementPercentage?.toFixed(1) || 'N/A'}%
                    </div>
                    <div className="text-sm text-gray-500">% Increase</div>
                  </div>
                </div>
                
                <div className="mt-6 grid gap-4 md:grid-cols-3">
                  <div className="bg-gray-50 p-4 rounded">
                    <div className="text-lg font-semibold">Estimated Cost</div>
                    <div className="text-xl text-orange-600">₹{scenarioResults.estimatedCost?.toLocaleString() || 'N/A'}</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <div className="text-lg font-semibold">ROI</div>
                    <div className="text-xl text-green-600">{scenarioResults.roi?.toFixed(2) || 'N/A'}x</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <div className="text-lg font-semibold">Timeline</div>
                    <div className="text-xl text-blue-600">{scenarioResults.timelineMonths || 'N/A'} months</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {renderInputForm(formData, setFormData)}
            
            <div className="space-y-4">
              <Button onClick={handleGetRecommendations} disabled={loading} className="w-full">
                {loading ? 'Generating...' : 'Get AI Recommendations'}
              </Button>

              {recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>AI-Powered Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recommendations.map((rec, idx) => (
                        <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="font-semibold text-gray-900">{rec.area || 'Unknown Area'}</div>
                              <div className="text-sm text-gray-600 mt-1">{rec.action || 'No action specified'}</div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm font-medium text-blue-600">
                                Priority: {rec.priority || 0}/10
                              </div>
                              <div className="text-xs text-gray-500">
                                Impact: +{rec.expectedImpact || 0}
                              </div>
                            </div>
                          </div>
                          <div className="mt-2 flex justify-between text-xs text-gray-500">
                            <span>Cost: ₹{rec.estimatedCost?.toLocaleString() || 'N/A'}</span>
                            <span>Timeline: {rec.timeline || 'N/A'}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
