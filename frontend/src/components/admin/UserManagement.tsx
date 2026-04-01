import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { API_BASE_URL } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Users, Trash2, UserCheck, UserX, Eye } from 'lucide-react';
import toast from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  response_count: number;
}

export function UserManagement() {
  const queryClient = useQueryClient();
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Fetch users
  const { data: usersData, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch users');
      return response.json();
    },
    refetchInterval: 30000,
  });

  // Delete user mutation
  const deleteUserMutation = useMutation({
    mutationFn: async (userId: number) => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete user');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast.success(data.message || 'User deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Update user status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ userId, isActive }: { userId: number; isActive: boolean }) => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/users/${userId}/status?is_active=${isActive}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update user status');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast.success(data.message || 'User status updated successfully');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const handleDeleteUser = (user: User) => {
    if (user.role === 'admin') {
      toast.error('Cannot delete admin users');
      return;
    }

    if (confirm(`Are you sure you want to delete user ${user.email} and all their ${user.response_count} responses? This action cannot be undone.`)) {
      deleteUserMutation.mutate(user.id);
    }
  };

  const handleToggleStatus = (user: User) => {
    updateStatusMutation.mutate({ userId: user.id, isActive: !user.is_active });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Loading users...</div>
        </div>
      </div>
    );
  }

  const users = usersData?.users || [];

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-4">
        <div className="bg-blue-50 p-3 rounded-lg dark:bg-blue-900/20">
          <div className="flex items-center justify-between">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-blue-600 dark:text-blue-400">
                Total Users
              </p>
              <p className="text-lg sm:text-xl font-bold text-blue-900 dark:text-blue-300">
                {usersData?.total_count || 0}
              </p>
            </div>
            <Users className="h-5 w-5 text-blue-500 flex-shrink-0" />
          </div>
        </div>

        <div className="bg-green-50 p-3 rounded-lg dark:bg-green-900/20">
          <div className="flex items-center justify-between">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-green-600 dark:text-green-400">
                Active Users
              </p>
              <p className="text-lg sm:text-xl font-bold text-green-900 dark:text-green-300">
                {users.filter((u: User) => u.is_active).length}
              </p>
            </div>
            <UserCheck className="h-5 w-5 text-green-500 flex-shrink-0" />
          </div>
        </div>

        <div className="bg-orange-50 p-3 rounded-lg dark:bg-orange-900/20">
          <div className="flex items-center justify-between">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-orange-600 dark:text-orange-400">
                Admin Users
              </p>
              <p className="text-lg sm:text-xl font-bold text-orange-900 dark:text-orange-300">
                {users.filter((u: User) => u.role === 'admin').length}
              </p>
            </div>
            <UserCheck className="h-5 w-5 text-orange-500 flex-shrink-0" />
          </div>
        </div>

        <div className="bg-purple-50 p-3 rounded-lg dark:bg-purple-900/20">
          <div className="flex items-center justify-between">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-purple-600 dark:text-purple-400">
                Total Responses
              </p>
              <p className="text-lg sm:text-xl font-bold text-purple-900 dark:text-purple-300">
                {users.reduce((sum: number, u: User) => sum + u.response_count, 0)}
              </p>
            </div>
            <Eye className="h-5 w-5 text-purple-500 flex-shrink-0" />
          </div>
        </div>
      </div>

      {/* Users Table */}
      {/* Mobile-friendly responsive layout */}
      <div className="space-y-4 lg:hidden">
        {users.map((user: User) => (
          <div key={user.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {user.full_name || user.username}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {user.email}
                </div>
              </div>
              <div className="flex space-x-2">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.role === 'admin'
                    ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                  {user.role}
                </span>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.is_active
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-500 dark:text-gray-400">Responses</div>
                <div className="text-gray-900 dark:text-white">{user.response_count}</div>
              </div>
              <div>
                <div className="text-gray-500 dark:text-gray-400">Created</div>
                <div className="text-gray-900 dark:text-white">
                  {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-gray-500 dark:text-gray-400">Last Login</div>
                <div className="text-gray-900 dark:text-white">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleToggleStatus(user)}
                disabled={updateStatusMutation.isPending}
                className="text-xs"
              >
                {user.is_active ? (
                  <>
                    <UserX className="h-3 w-3 mr-1" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <UserCheck className="h-3 w-3 mr-1" />
                    Activate
                  </>
                )}
              </Button>
              {user.role !== 'admin' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteUser(user)}
                  disabled={deleteUserMutation.isPending}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs"
                >
                  <Trash2 className="h-3 w-3 mr-1" />
                  Delete
                </Button>
              )}
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
                  Role
                </th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Status
                </th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Responses
                </th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Created
                </th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Last Login
                </th>
                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-400">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
              {users.map((user: User) => (
                <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-2 py-3">
                    <div className="min-w-0 flex-1">
                      <div className="text-xs font-medium text-gray-900 dark:text-white truncate">
                        {user.full_name || user.username}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {user.email}
                      </div>
                    </div>
                  </td>
                  <td className="px-2 py-3">
                    <span className={`inline-flex px-1 py-0.5 text-xs font-semibold rounded ${user.role === 'admin'
                        ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                      }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-2 py-3">
                    <span className={`inline-flex px-1 py-0.5 text-xs font-semibold rounded ${user.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                      }`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-2 py-3 text-xs text-gray-900 dark:text-white">
                    {user.response_count}
                  </td>
                  <td className="px-2 py-3 text-xs text-gray-500 dark:text-gray-400">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-2 py-3 text-xs text-gray-500 dark:text-gray-400">
                    {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-2 py-3">
                    <div className="flex flex-col space-y-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleStatus(user)}
                        disabled={updateStatusMutation.isPending}
                        className="text-xs px-1 py-0.5 h-6"
                      >
                        {user.is_active ? (
                          <>
                            <UserX className="h-3 w-3 mr-1" />
                            Deactivate
                          </>
                        ) : (
                          <>
                            <UserCheck className="h-3 w-3 mr-1" />
                            Activate
                          </>
                        )}
                      </Button>
                      {user.role !== 'admin' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteUser(user)}
                          disabled={deleteUserMutation.isPending}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs px-1 py-0.5 h-6"
                        >
                          <Trash2 className="h-3 w-3 mr-1" />
                          Delete
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {users.length === 0 && (
        <div className="text-center py-8">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No users found</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Users will appear here once they register.
          </p>
        </div>
      )}
    </div>
  );
}