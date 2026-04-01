import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { ResponsiveContainer, Cell } from 'recharts';

export function CorrelationMatrix() {
  const [matrix, setMatrix] = useState<number[][]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .getCorrelationMatrix()
      .then(setMatrix)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const features = [
    'Hardware',
    'Software',
    'Internet',
    'Digital',
    'Satisfaction',
    'Efficiency',
    'Financial',
    'Technical',
    'Training',
    'Policy',
  ];

  const getColor = (value: number) => {
    const absValue = Math.abs(value);
    if (absValue < 0.3) return '#e5e7eb';
    if (absValue < 0.5) return value > 0 ? '#93c5fd' : '#fca5a5';
    if (absValue < 0.7) return value > 0 ? '#60a5fa' : '#f87171';
    return value > 0 ? '#3b82f6' : '#ef4444';
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Correlation Matrix</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-96 items-center justify-center">
            <div className="text-gray-500">Loading correlation matrix...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature Correlation Matrix</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="border border-gray-300 p-2 text-left text-xs font-medium dark:border-gray-700"></th>
                {features.map((feature) => (
                  <th
                    key={feature}
                    className="border border-gray-300 p-2 text-xs font-medium dark:border-gray-700"
                  >
                    {feature}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row, i) => (
                <tr key={i}>
                  <td className="border border-gray-300 p-2 text-xs font-medium dark:border-gray-700">
                    {features[i]}
                  </td>
                  {row.map((value, j) => (
                    <td
                      key={j}
                      className="border border-gray-300 p-2 text-center text-xs dark:border-gray-700"
                      style={{
                        backgroundColor: getColor(value),
                        color: Math.abs(value) > 0.5 ? 'white' : 'black',
                      }}
                    >
                      {value.toFixed(2)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
