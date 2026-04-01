import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { SurveyResponse } from '@/types';

interface SatisfactionChartProps {
  data: SurveyResponse[];
}

const COLORS = ['#ef4444', '#f59e0b', '#10b981'];

export function SatisfactionChart({ data }: SatisfactionChartProps) {
  // Handle empty or undefined data
  if (!data || data.length === 0) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Satisfaction Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              No data available
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Satisfaction Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              No data available
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Create histogram bins
  const bins = Array.from({ length: 10 }, (_, i) => ({
    range: `${i + 1}`,
    count: 0,
  }));

  // Filter and process valid data
  const validData = data.filter(response => 
    response && 
    response.serviceQuality && 
    typeof response.serviceQuality.overallSatisfaction === 'number'
  );

  validData.forEach((response) => {
    const score = Math.floor(response.serviceQuality.overallSatisfaction);
    if (score >= 1 && score <= 10) {
      bins[score - 1].count += 1;
    }
  });

  // Categorize satisfaction
  const categories = {
    Low: validData.filter((r) => r.serviceQuality.overallSatisfaction <= 4).length,
    Medium: validData.filter((r) => r.serviceQuality.overallSatisfaction > 4 && r.serviceQuality.overallSatisfaction <= 7).length,
    High: validData.filter((r) => r.serviceQuality.overallSatisfaction > 7).length,
  };

  const categoryData = Object.entries(categories).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Satisfaction Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={bins}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Satisfaction Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value">
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
