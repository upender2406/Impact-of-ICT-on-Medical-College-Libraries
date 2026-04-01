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
import { COLLEGES } from '@/lib/constants';
import type { SurveyResponse } from '@/types';
import { calculateInfrastructureScore } from '@/lib/utils';

interface InfrastructureChartProps {
  data: SurveyResponse[];
}

export function InfrastructureChart({ data }: InfrastructureChartProps) {
  // Handle empty or undefined data
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Infrastructure Assessment by College</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[400px] text-gray-500">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  // Group data by college and calculate average infrastructure scores
  const collegeData = COLLEGES.map((college) => {
    const collegeResponses = data.filter((r) => 
      r && 
      r.collegeId === college.id && 
      r.infrastructure &&
      typeof r.infrastructure.hardwareQuality === 'number'
    );
    
    if (collegeResponses.length === 0) {
      return null; // Will be filtered out
    }

    const avgScore =
      collegeResponses.reduce(
        (sum, r) => sum + calculateInfrastructureScore(r.infrastructure),
        0
      ) / collegeResponses.length;

    return {
      name: college.code,
      score: Number(avgScore.toFixed(2)),
      count: collegeResponses.length,
      hardware: collegeResponses.reduce((sum, r) => sum + r.infrastructure.hardwareQuality, 0) / collegeResponses.length,
      software: collegeResponses.reduce((sum, r) => sum + r.infrastructure.softwareAvailability, 0) / collegeResponses.length,
      internet: collegeResponses.reduce((sum, r) => sum + r.infrastructure.internetSpeed, 0) / collegeResponses.length,
      digital: collegeResponses.reduce((sum, r) => sum + r.infrastructure.digitalCollection, 0) / collegeResponses.length,
    };
  }).filter((d) => d !== null); // Remove null entries

  return (
    <Card>
      <CardHeader>
        <CardTitle>Infrastructure Assessment by College</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={collegeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 5]} />
            <Tooltip />
            <Legend />
            <Bar dataKey="hardware" fill="#3b82f6" name="Hardware" />
            <Bar dataKey="software" fill="#10b981" name="Software" />
            <Bar dataKey="internet" fill="#f59e0b" name="Internet" />
            <Bar dataKey="digital" fill="#ef4444" name="Digital Collection" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
