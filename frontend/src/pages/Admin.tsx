import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { API_BASE_URL } from '@/lib/constants';
import { useStore } from '@/store/store';
import toast from 'react-hot-toast';
import { UserManagement } from '@/components/admin/UserManagement';
import { EntryManagement } from '@/components/admin/EntryManagement';
import {
  Users,
  Database,
  RefreshCw,
  Activity,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  BarChart3,
  FileCheck,
} from 'lucide-react';

export function Admin() {
  const { user } = useStore();
  const queryClient = useQueryClient();
  const [isRetraining, setIsRetraining] = useState(false);

  // Fetch training status
  const { data: trainingStatus } = useQuery({
    queryKey: ['training-status'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/admin/training/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch training status');
      return response.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Fetch summary statistics for real data count
  const { data: summary } = useQuery({
    queryKey: ['summary'],
    queryFn: () => apiClient.getSummaryStatistics(),
    refetchInterval: 10000,
  });

  // Fetch all responses to get actual count
  const { data: responses = [] } = useQuery({
    queryKey: ['responses'],
    queryFn: () => apiClient.getAllResponses(),
    refetchInterval: 30000,
  });

  // Retrain models mutation
  const retrainMutation = useMutation({
    mutationFn: async (force: boolean = false) => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/training/retrain?force=${force}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          },
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to retrain models');
      }
      return response.json();
    },
    onSuccess: (data) => {
      if (data.status === 'success') {
        toast.success('Model retraining completed successfully!');
      } else if (data.status === 'skipped') {
        toast('Retraining not needed yet', { icon: 'ℹ️' });
      }
      queryClient.invalidateQueries({ queryKey: ['training-status'] });
      setIsRetraining(false);
    },
    onError: (error: Error) => {
      toast.error(error.message);
      setIsRetraining(false);
    },
  });

  const handleRetrain = (force: boolean = false) => {
    if (isRetraining) return;
    setIsRetraining(true);
    retrainMutation.mutate(force);
  };

  const status = trainingStatus?.data;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="w-full px-4 sm:px-6 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
            Admin Panel
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            System management and AI model controls
          </p>
        </div>

        {/* System Overview */}
        <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 mb-6">
          <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">
                  Total Responses
                </p>
                <p className="mt-1 text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
                  {summary?.totalResponses || 0}
                </p>
              </div>
              <Database className="h-5 w-5 sm:h-6 sm:w-6 text-blue-500 flex-shrink-0" />
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">
                  Dataset Size
                </p>
                <p className="mt-1 text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
                  {status?.current_data_count || 0}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  records in system
                </p>
              </div>
              <BarChart3 className="h-5 w-5 sm:h-6 sm:w-6 text-green-500 flex-shrink-0" />
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">
                  New Entries
                </p>
                <p className="mt-1 text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
                  {status?.new_entries_since_training || 0}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  since last training
                </p>
              </div>
              <TrendingUp className="h-5 w-5 sm:h-6 sm:w-6 text-purple-500 flex-shrink-0" />
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <div className="min-w-0 flex-1">
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 truncate">
                  Training Status
                </p>
                <p className="mt-1 text-sm sm:text-lg font-bold text-gray-900 dark:text-white">
                  {status?.should_retrain ? 'Needs Retrain' : 'Up to Date'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  {status?.entries_until_retrain || 0} until auto-retrain
                </p>
              </div>
              {status?.should_retrain ? (
                <AlertCircle className="h-5 w-5 sm:h-6 sm:w-6 text-orange-500 flex-shrink-0" />
              ) : (
                <CheckCircle className="h-5 w-5 sm:h-6 sm:w-6 text-green-500 flex-shrink-0" />
              )}
            </div>
          </div>
        </div>

        {/* AI Model Management */}
        <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900 mb-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4">
            AI Model Management
          </h2>

          <div className="space-y-4">
            {/* Training Info */}
            <div className="grid gap-3 sm:gap-4 grid-cols-1 lg:grid-cols-2">
              <div className="rounded-lg bg-gray-50 p-3 sm:p-4 dark:bg-gray-800">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                    Last Training
                  </h3>
                </div>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  {status?.last_training_time
                    ? new Date(status.last_training_time).toLocaleString()
                    : 'Never trained'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Data count: {status?.last_training_data_count || 0}
                </p>
              </div>

              <div className="rounded-lg bg-gray-50 p-3 sm:p-4 dark:bg-gray-800">
                <div className="flex items-center space-x-2 mb-2">
                  <Activity className="h-4 w-4 text-gray-600 dark:text-gray-400 flex-shrink-0" />
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                    Training Metrics
                  </h3>
                </div>
                {status?.last_training_metrics?.satisfaction_classifier ? (
                  <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    <p>Classifier Accuracy: {(status.last_training_metrics.satisfaction_classifier.testing_accuracy * 100).toFixed(1)}%</p>
                    <p>Regressor R²: {(status.last_training_metrics.efficiency_regressor?.testing_r2 || 0).toFixed(3)}</p>
                  </div>
                ) : (
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    No metrics available
                  </p>
                )}
              </div>
            </div>

            {/* Retrain Controls */}
            <div className="rounded-lg border-2 border-dashed border-gray-300 p-3 sm:p-4 dark:border-gray-700">
              <div className="flex flex-col space-y-3 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                    Model Retraining
                  </h3>
                  <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                    {status?.should_retrain
                      ? 'Retraining recommended: sufficient new data available'
                      : `${status?.entries_until_retrain || 0} more entries needed for auto-retrain`}
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-2 sm:ml-4">
                  <button
                    onClick={() => handleRetrain(false)}
                    disabled={isRetraining || !status?.should_retrain}
                    className="flex items-center justify-center space-x-2 rounded-lg bg-blue-600 px-3 py-2 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <RefreshCw className={`h-3 w-3 ${isRetraining ? 'animate-spin' : ''}`} />
                    <span>{isRetraining ? 'Retraining...' : 'Retrain'}</span>
                  </button>
                  <button
                    onClick={() => handleRetrain(true)}
                    disabled={isRetraining}
                    className="flex items-center justify-center space-x-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
                  >
                    <RefreshCw className={`h-3 w-3 ${isRetraining ? 'animate-spin' : ''}`} />
                    <span>Force Retrain</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Dataset Control */}
            <div className="rounded-lg bg-blue-50 p-3 sm:p-4 dark:bg-blue-900/20">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-1">
                    Dataset Configuration
                  </h3>
                  <p className="text-xs sm:text-sm text-blue-800 dark:text-blue-400">
                    AI models use all available data for training and inference. Current dataset: {status?.current_data_count || 0} records.
                    Models automatically retrain after every 100 new entries.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Entry Management */}
        <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900 mb-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4">
            <FileCheck className="inline mr-2 h-4 w-4 sm:h-5 sm:w-5" />
            Entry Verification & Management
          </h2>
          <EntryManagement />
        </div>

        {/* User Management */}
        <div className="rounded-lg border border-gray-200 bg-white p-3 sm:p-4 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4">
            User Management
          </h2>
          <UserManagement />
        </div>
      </div>
    </div>
  );
}
