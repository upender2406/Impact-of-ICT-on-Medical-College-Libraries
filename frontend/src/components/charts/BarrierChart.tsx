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
} from 'recharts';
import type { SurveyResponse } from '@/types';
import { calculateBarrierScore } from '@/lib/utils';

interface BarrierChartProps {
  data: SurveyResponse[];
}

export function BarrierChart({ data }: BarrierChartProps) {
  // Handle empty or undefined data
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Barrier Assessment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px] text-gray-500">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  // Filter valid data
  const validData = data.filter(response => 
    response && 
    response.barriers && 
    typeof response.barriers.financialBarrier === 'number'
  );

  if (validData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Barrier Assessment</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[300px] text-gray-500">
            No valid barrier data available
          </div>
        </CardContent>
      </Card>
    );
  }

  const barrierData = [
    {
      name: 'Financial',
      average: validData.reduce((sum, r) => sum + r.barriers.financialBarrier, 0) / validData.length,
    },
    {
      name: 'Technical',
      average: validData.reduce((sum, r) => sum + r.barriers.technicalBarrier, 0) / validData.length,
    },
    {
      name: 'Training',
      average: validData.reduce((sum, r) => sum + r.barriers.trainingBarrier, 0) / validData.length,
    },
    {
      name: 'Policy',
      average: validData.reduce((sum, r) => sum + r.barriers.policyBarrier, 0) / validData.length,
    },
  ].map((item) => ({
    ...item,
    average: Number(item.average.toFixed(2)),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Barrier Assessment</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barrierData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 5]} />
            <YAxis dataKey="name" type="category" />
            <Tooltip />
            <Legend />
            <Bar dataKey="average" fill="#ef4444" name="Average Score" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
