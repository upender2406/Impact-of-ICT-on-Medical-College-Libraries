import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { API_BASE_URL } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  CheckCircle,
  XCircle,
  Trash2,
  Eye,
  Filter,
  Clock,
  User,
  Building2,
  Calendar
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Entry {
  id: number;
  user_id: number;
  user_email: string;
  user_name: string;
  college: string;
  status: string;
  submitted_at: string;
  reviewed_at: string | null;
  reviewer_id: number | null;
  infrastructure_score: number;
  overall_satisfaction: number;
  service_efficiency: number;
  comments: string | null;
}

export function EntryManagement() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedEntries, setSelectedEntries] = useState<number[]>([]);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [entryToReject, setEntryToReject] = useState<number | null>(null);

  // Fetch entries
  const { data: entriesData, isLoading } = useQuery({
    queryKey: ['admin-entries', statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }

      const response = await fetch(
        `${API_BASE_URL}/api/admin/entries?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) throw new Error('Failed to fetch entries');
      return response.json();
    },
    refetchInterval: 30000,
  });

  // Approve entry mutation
  const approveMutation = useMutation({
    mutationFn: async (entryId: number) => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/entries/${entryId}/approve`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to approve entry');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast.success(data.message || 'Entry approved successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-entries'] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Reject entry mutation
  const rejectMutation = useMutation({
    mutationFn: async ({ entryId, reason }: { entryId: number; reason: string }) => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/entries/${entryId}/reject?reason=${encodeURIComponent(reason)}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to reject entry');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast.success(data.message || 'Entry rejected successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-entries'] });
      setShowRejectModal(false);
      setRejectReason('');
      setEntryToReject(null);
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Delete entry mutation
  const deleteMutation = useMutation({
    mutationFn: async (entryId: number) => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/entries/${entryId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete entry');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast.success(data.message || 'Entry deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-entries'] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const handleApprove = (entryId: number) => {
    approveMutation.mutate(entryId);
  };

  const handleReject = (entryId: number) => {
    setEntryToReject(entryId);
    setShowRejectModal(true);
  };

  const handleRejectConfirm = () => {
    if (entryToReject && rejectReason.trim()) {
      rejectMutation.mutate({ entryId: entryToReject, reason: rejectReason.trim() });
    } else {
      toast.error('Please provide a reason for rejection');
    }
  };

  const handleDelete = (entryId: number) => {
    if (confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
      deleteMutation.mutate(entryId);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'pending':
      default:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Loading entries...</div>
        </div>
      </div>
    );
  }

  const entries = entriesData?.entries || [];

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Entries
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {entriesData?.total_count || 0}
                </p>
              </div>
              <Eye className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-600 dark:text-yellow-400">
                  Pending
                </p>
                <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-300">
                  {entriesData?.pending_count || 0}
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600 dark:text-green-400">
                  Approved
                </p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-300">
                  {entriesData?.approved_count || 0}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600 dark:text-red-400">
                  Rejected
                </p>
                <p className="text-2xl font-bold text-red-900 dark:text-red-300">
                  {entriesData?.rejected_count || 0}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="mr-2 h-5 w-5" />
            Filter Entries
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Button
              variant={statusFilter === 'all' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('all')}
            >
              All
            </Button>
            <Button
              variant={statusFilter === 'pending' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('pending')}
            >
              Pending
            </Button>
            <Button
              variant={statusFilter === 'approved' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('approved')}
            >
              Approved
            </Button>
            <Button
              variant={statusFilter === 'rejected' ? 'default' : 'outline'}
              onClick={() => setStatusFilter('rejected')}
            >
              Rejected
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Entries Table */}
      <Card>
        <CardHeader>
          <CardTitle>User Entries</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Mobile-friendly responsive layout */}
          <div className="space-y-4 lg:hidden">
            {entries.map((entry: Entry) => (
              <div key={entry.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-gray-400" />
                    <div>
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {entry.user_name}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {entry.user_email}
                      </div>
                    </div>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(entry.status)}`}>
                    {entry.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="flex items-center space-x-1 text-gray-500 dark:text-gray-400">
                      <Building2 className="h-3 w-3" />
                      <span>College</span>
                    </div>
                    <div className="text-gray-900 dark:text-white">{entry.college}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 dark:text-gray-400">Submitted</div>
                    <div className="text-gray-900 dark:text-white">
                      {entry.submitted_at ? new Date(entry.submitted_at).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                </div>

                <div className="text-sm">
                  <div className="text-gray-500 dark:text-gray-400 mb-1">Scores</div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>Infra: {entry.infrastructure_score.toFixed(1)}</div>
                    <div>Satisfaction: {entry.overall_satisfaction}</div>
                    <div>Efficiency: {entry.service_efficiency}</div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {entry.status === 'pending' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => handleApprove(entry.id)}
                        disabled={approveMutation.isPending}
                        className="bg-green-600 hover:bg-green-700 text-xs"
                      >
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleReject(entry.id)}
                        disabled={rejectMutation.isPending}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs"
                      >
                        <XCircle className="h-3 w-3 mr-1" />
                        Reject
                      </Button>
                    </>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDelete(entry.id)}
                    disabled={deleteMutation.isPending}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs"
                  >
                    <Trash2 className="h-3 w-3 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Desktop table layout */}
          <div className="hidden lg:block">
            <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700">
              <table className="w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                      User
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                      College
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                      Scores
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                      Status
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                      Date
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
                  {entries.map((entry: Entry) => (
                    <tr key={entry.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="px-2 py-3">
                        <div className="flex items-center">
                          <User className="h-3 w-3 text-gray-400 mr-1 flex-shrink-0" />
                          <div className="min-w-0 flex-1">
                            <div className="text-xs font-medium text-gray-900 dark:text-white truncate">
                              {entry.user_name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                              {entry.user_email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-2 py-3">
                        <div className="flex items-center">
                          <Building2 className="h-3 w-3 text-gray-400 mr-1 flex-shrink-0" />
                          <span className="text-xs text-gray-900 dark:text-white truncate">
                            {entry.college}
                          </span>
                        </div>
                      </td>
                      <td className="px-2 py-3">
                        <div className="text-xs text-gray-900 dark:text-white">
                          <div>I: {entry.infrastructure_score.toFixed(1)}</div>
                          <div>S: {entry.overall_satisfaction}</div>
                          <div>E: {entry.service_efficiency}</div>
                        </div>
                      </td>
                      <td className="px-2 py-3">
                        <span className={`inline-flex px-1 py-0.5 text-xs font-semibold rounded ${getStatusColor(entry.status)}`}>
                          {entry.status}
                        </span>
                      </td>
                      <td className="px-2 py-3">
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {entry.submitted_at ? new Date(entry.submitted_at).toLocaleDateString() : 'N/A'}
                        </div>
                      </td>
                      <td className="px-2 py-3">
                        <div className="flex flex-col space-y-1">
                          {entry.status === 'pending' && (
                            <div className="flex space-x-1">
                              <Button
                                size="sm"
                                onClick={() => handleApprove(entry.id)}
                                disabled={approveMutation.isPending}
                                className="bg-green-600 hover:bg-green-700 text-xs px-1 py-0.5 h-6"
                              >
                                <CheckCircle className="h-3 w-3" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleReject(entry.id)}
                                disabled={rejectMutation.isPending}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs px-1 py-0.5 h-6"
                              >
                                <XCircle className="h-3 w-3" />
                              </Button>
                            </div>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDelete(entry.id)}
                            disabled={deleteMutation.isPending}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs px-1 py-0.5 h-6"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {entries.length === 0 && (
            <div className="text-center py-8">
              <Eye className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No entries found</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {statusFilter === 'all' ? 'No user entries available.' : `No ${statusFilter} entries found.`}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Reject Entry
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Please provide a reason for rejecting this entry:
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              rows={4}
              placeholder="Enter rejection reason..."
            />
            <div className="flex justify-end space-x-3 mt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                  setEntryToReject(null);
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={handleRejectConfirm}
                disabled={!rejectReason.trim() || rejectMutation.isPending}
                className="bg-red-600 hover:bg-red-700"
              >
                {rejectMutation.isPending ? 'Rejecting...' : 'Reject Entry'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}