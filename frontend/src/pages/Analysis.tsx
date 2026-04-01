import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { TrendingUp, BarChart3, PieChart as PieChartIcon, Activity, Users, Building2 } from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export function Analysis() {
  const [activeTab, setActiveTab] = useState<'infrastructure' | 'satisfaction' | 'barriers' | 'correlation'>('infrastructure');

  // Fetch data
  const { data: responses = [], isLoading } = useQuery({
    queryKey: ['responses'],
    queryFn: () => apiClient.getAllResponses(),
  });

  const { data: summary } = useQuery({
    queryKey: ['summary'],
    queryFn: () => apiClient.getSummaryStatistics(),
  });

  // Process data for different analyses
  const processInfrastructureData = () => {
    const collegeData = responses.reduce((acc: any, response: any) => {
      const college = response.collegeName || 'Unknown';
      if (!acc[college]) {
        acc[college] = {
          name: college,
          hardware: [],
          software: [],
          internet: [],
          digital: [],
          overall: []
        };
      }
      acc[college].hardware.push(response.infrastructure?.hardwareQuality || 0);
      acc[college].software.push(response.infrastructure?.softwareAvailability || 0);
      acc[college].internet.push(response.infrastructure?.internetSpeed || 0);
      acc[college].digital.push(response.infrastructure?.digitalCollection || 0);
      acc[college].overall.push(
        ((response.infrastructure?.hardwareQuality || 0) +
         (response.infrastructure?.softwareAvailability || 0) +
         (response.infrastructure?.internetSpeed || 0) +
         (response.infrastructure?.digitalCollection || 0)) / 4
      );
      return acc;
    }, {});

    return Object.values(collegeData).map((college: any) => ({
      name: college.name.split(' ')[0], // Shorten names
      hardware: college.hardware.reduce((a: number, b: number) => a + b, 0) / college.hardware.length,
      software: college.software.reduce((a: number, b: number) => a + b, 0) / college.software.length,
      internet: college.internet.reduce((a: number, b: number) => a + b, 0) / college.internet.length,
      digital: college.digital.reduce((a: number, b: number) => a + b, 0) / college.digital.length,
      overall: college.overall.reduce((a: number, b: number) => a + b, 0) / college.overall.length,
    }));
  };

  const processSatisfactionData = () => {
    const satisfactionLevels = responses.reduce((acc: any, response: any) => {
      const satisfaction = response.serviceQuality?.overallSatisfaction || 0;
      let level = 'Low';
      if (satisfaction >= 7) level = 'High';
      else if (satisfaction >= 4) level = 'Medium';
      
      acc[level] = (acc[level] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(satisfactionLevels).map(([name, value]) => ({
      name,
      value,
      percentage: ((value as number) / responses.length * 100).toFixed(1)
    }));
  };

  const processBarriersData = () => {
    return responses.map((response: any, index: number) => ({
      id: index,
      financial: response.barriers?.financialBarrier || 0,
      technical: response.barriers?.technicalBarrier || 0,
      training: response.barriers?.trainingBarrier || 0,
      policy: response.barriers?.policyBarrier || 0,
      overall: ((response.barriers?.financialBarrier || 0) +
                (response.barriers?.technicalBarrier || 0) +
                (response.barriers?.trainingBarrier || 0) +
                (response.barriers?.policyBarrier || 0)) / 4
    }));
  };

  const processCorrelationData = () => {
    return responses.map((response: any) => ({
      infrastructure: ((response.infrastructure?.hardwareQuality || 0) +
                      (response.infrastructure?.softwareAvailability || 0) +
                      (response.infrastructure?.internetSpeed || 0) +
                      (response.infrastructure?.digitalCollection || 0)) / 4,
      satisfaction: response.serviceQuality?.overallSatisfaction || 0,
      efficiency: response.serviceQuality?.serviceEfficiency || 0,
      barriers: ((response.barriers?.financialBarrier || 0) +
                (response.barriers?.technicalBarrier || 0) +
                (response.barriers?.trainingBarrier || 0) +
                (response.barriers?.policyBarrier || 0)) / 4
    }));
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Loading analysis...</div>
          <div className="text-sm text-gray-400">Processing data</div>
        </div>
      </div>
    );
  }

  const infrastructureData = processInfrastructureData();
  const satisfactionData = processSatisfactionData();
  const barriersData = processBarriersData();
  const correlationData = processCorrelationData();

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Advanced Analysis
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Deep insights into ICT infrastructure and service quality
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Responses
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {responses.length}
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Avg Infrastructure
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {summary?.averageInfrastructureScore?.toFixed(1) || '0.0'}
                </p>
              </div>
              <Building2 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Avg Satisfaction
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {summary?.averageSatisfaction?.toFixed(1) || '0.0'}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Critical Barriers
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {summary?.criticalBarriersCount || 0}
                </p>
              </div>
              <Activity className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis Tabs */}
      <div className="flex space-x-2">
        <Button
          variant={activeTab === 'infrastructure' ? 'default' : 'outline'}
          onClick={() => setActiveTab('infrastructure')}
        >
          <BarChart3 className="mr-2 h-4 w-4" />
          Infrastructure
        </Button>
        <Button
          variant={activeTab === 'satisfaction' ? 'default' : 'outline'}
          onClick={() => setActiveTab('satisfaction')}
        >
          <PieChartIcon className="mr-2 h-4 w-4" />
          Satisfaction
        </Button>
        <Button
          variant={activeTab === 'barriers' ? 'default' : 'outline'}
          onClick={() => setActiveTab('barriers')}
        >
          <Activity className="mr-2 h-4 w-4" />
          Barriers
        </Button>
        <Button
          variant={activeTab === 'correlation' ? 'default' : 'outline'}
          onClick={() => setActiveTab('correlation')}
        >
          <TrendingUp className="mr-2 h-4 w-4" />
          Correlation
        </Button>
      </div>

      {/* Analysis Content */}
      {activeTab === 'infrastructure' && (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Infrastructure Analysis by College</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={infrastructureData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="hardware" fill="#8884d8" name="Hardware Quality" />
                  <Bar dataKey="software" fill="#82ca9d" name="Software Availability" />
                  <Bar dataKey="internet" fill="#ffc658" name="Internet Speed" />
                  <Bar dataKey="digital" fill="#ff7300" name="Digital Collection" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Overall Infrastructure Scores</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={infrastructureData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="overall" stroke="#8884d8" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'satisfaction' && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Satisfaction Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={satisfactionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {satisfactionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Satisfaction Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {satisfactionData.map((item, index) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-4 h-4 rounded-full" 
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      <span className="font-medium">{item.name} Satisfaction</span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{item.value}</div>
                      <div className="text-sm text-gray-500">{item.percentage}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'barriers' && (
        <Card>
          <CardHeader>
            <CardTitle>Barriers Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart data={barriersData}>
                <CartesianGrid />
                <XAxis dataKey="financial" name="Financial" />
                <YAxis dataKey="technical" name="Technical" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Barriers" data={barriersData} fill="#8884d8" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {activeTab === 'correlation' && (
        <Card>
          <CardHeader>
            <CardTitle>Infrastructure vs Satisfaction Correlation</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart data={correlationData}>
                <CartesianGrid />
                <XAxis dataKey="infrastructure" name="Infrastructure Score" />
                <YAxis dataKey="satisfaction" name="Satisfaction Score" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Correlation" data={correlationData} fill="#8884d8" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
