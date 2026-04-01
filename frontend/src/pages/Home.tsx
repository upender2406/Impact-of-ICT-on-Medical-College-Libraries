import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { InfrastructureChart } from '@/components/charts/InfrastructureChart';
import { SatisfactionChart } from '@/components/charts/SatisfactionChart';
import { BarrierChart } from '@/components/charts/BarrierChart';
import { CorrelationMatrix } from '@/components/charts/CorrelationMatrix';
import { Users, Building2, TrendingUp, AlertTriangle } from 'lucide-react';
import { useStore } from '@/store/store';
import { useEffect } from 'react';
import toast from 'react-hot-toast';

export function Home() {
  const { setResponses } = useStore();

  // Fetch responses with auto-refresh every 30 seconds
  const { data: responses = [], isLoading, error: responsesError, refetch: refetchResponses } = useQuery({
    queryKey: ['responses'],
    queryFn: () => apiClient.getAllResponses(),
    retry: 2,
    refetchOnWindowFocus: true,
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });

  // Fetch summary with auto-refresh
  const { data: summary, error: summaryError, refetch: refetchSummary } = useQuery({
    queryKey: ['summary'],
    queryFn: () => apiClient.getSummaryStatistics(),
    retry: 2,
    refetchOnWindowFocus: true,
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });

  // Update store when responses change
  useEffect(() => {
    if (responses.length > 0) {
      setResponses(responses);
    }
  }, [responses, setResponses]);

  // Manual refresh function for real-time updates
  const handleRefresh = async () => {
    try {
      await Promise.all([
        refetchResponses(),
        refetchSummary()
      ]);
      toast.success('Data refreshed successfully!');
    } catch (error) {
      toast.error('Failed to refresh data');
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Loading dashboard...</div>
          <div className="text-sm text-gray-400">Fetching data from server</div>
        </div>
      </div>
    );
  }

  if (responsesError || summaryError) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-2">Error loading dashboard</div>
          <div className="text-sm text-gray-400">
            {responsesError?.message || summaryError?.message || 'Failed to load data'}
          </div>
          <button
            onClick={handleRefresh}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            ICT Impact Assessment Dashboard
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Real-time insights and analysis for medical college libraries in Bihar
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center space-x-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          <TrendingUp className="h-4 w-4" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Responses"
          value={summary?.totalResponses || 0}
          icon={<Users className="h-5 w-5" />}
          color="primary"
        />
        <StatsCard
          title="Average Infrastructure Score"
          value={summary?.averageInfrastructureScore || 0}
          subtitle="Out of 5.0"
          icon={<Building2 className="h-5 w-5" />}
          color="secondary"
          format="number"
        />
        <StatsCard
          title="Average Satisfaction"
          value={summary?.averageSatisfaction || 0}
          subtitle="Out of 10.0"
          icon={<TrendingUp className="h-5 w-5" />}
          color="accent"
          format="number"
        />
        <StatsCard
          title="Critical Barriers"
          value={summary?.criticalBarriersCount || 0}
          icon={<AlertTriangle className="h-5 w-5" />}
          color="primary"
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6">
        <InfrastructureChart data={responses} />
        <SatisfactionChart data={responses} />
        <BarrierChart data={responses} />
        <CorrelationMatrix />
      </div>
    </div>
  );
}
