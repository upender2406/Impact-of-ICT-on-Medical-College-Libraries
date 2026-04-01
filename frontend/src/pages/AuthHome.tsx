import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LogIn, UserPlus, Shield, BarChart3 } from 'lucide-react';

export function AuthHome() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-600 rounded-full mb-6">
            <BarChart3 className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            ICT Impact Assessment Platform
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            AI-Powered Analysis for Medical College Libraries
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* User Login */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/login')}>
            <CardContent className="p-8">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
                  <LogIn className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold">User Login</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Access your dashboard, submit surveys, and view your data
                </p>
                <Button className="w-full mt-4">
                  Sign In as User
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Admin Login */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/login')}>
            <CardContent className="p-8">
              <div className="flex flex-col items-center text-center space-y-4">
                <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center">
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold">Admin Login</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Manage users, view analytics, and configure system settings
                </p>
                <Button className="w-full mt-4" variant="outline">
                  Sign In as Admin
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sign Up Option */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="flex items-center gap-4 mb-4 md:mb-0">
                <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
                  <UserPlus className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-lg">New to the platform?</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Create a free account to get started
                  </p>
                </div>
              </div>
              <Button onClick={() => navigate('/signup')} variant="outline">
                Create Account
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Test Accounts Info */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-gray-800 rounded-lg">
          <p className="text-sm font-semibold mb-2 text-center">Test Accounts:</p>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium">Admin Account:</p>
              <p className="text-gray-600 dark:text-gray-400">admin@ictsurvey.com / admin123</p>
            </div>
            <div>
              <p className="font-medium">User Account:</p>
              <p className="text-gray-600 dark:text-gray-400">user@ictsurvey.com / user123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
