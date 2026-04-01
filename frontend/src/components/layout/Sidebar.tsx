import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useStore } from '@/store/store';
import {
  Home,
  FileText,
  BarChart3,
  Brain,
  FileDown,
  TrendingUp,
  Shield,
} from 'lucide-react';

const userMenuItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/data-entry', label: 'Data Entry', icon: FileText },
  { path: '/analysis', label: 'Analysis', icon: BarChart3 },
  { path: '/prediction-lab', label: 'Prediction Lab', icon: Brain },
  { path: '/reports', label: 'Reports', icon: FileDown },
];

const adminMenuItems = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/data-entry', label: 'Data Entry', icon: FileText },
  { path: '/analysis', label: 'Analysis', icon: BarChart3 },
  { path: '/prediction-lab', label: 'Prediction Lab', icon: Brain },
  { path: '/reports', label: 'Reports', icon: FileDown },
  { path: '/admin', label: 'Admin Panel', icon: Shield },
];

export function Sidebar() {
  const location = useLocation();
  const { user } = useStore();
  
  const menuItems = user?.role === 'admin' ? adminMenuItems : userMenuItems;

  return (
    <aside className="hidden lg:block w-64 border-r border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 fixed left-0 top-16 h-[calc(100vh-4rem)] overflow-y-auto z-30">
      <div className="p-4">
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'flex items-center space-x-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-8 rounded-lg bg-gradient-to-br from-primary-50 to-secondary-50 p-4 dark:from-primary-900/20 dark:to-secondary-900/20">
          <TrendingUp className="mb-2 h-6 w-6 text-primary-600" />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            {user?.role === 'admin' ? 'Admin Access' : 'Quick Stats'}
          </h3>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            {user?.role === 'admin' 
              ? 'Full system access and controls' 
              : 'View real-time insights and trends'}
          </p>
        </div>
      </div>
    </aside>
  );
}
