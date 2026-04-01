import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface StatsCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  trend?: number;
  icon?: React.ReactNode;
  format?: 'number' | 'percentage' | 'currency';
  color?: 'primary' | 'secondary' | 'accent';
}

export function StatsCard({
  title,
  value,
  subtitle,
  trend,
  icon,
  format = 'number',
  color = 'primary',
}: StatsCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (typeof value === 'number') {
      const target = value;
      const duration = 2000;
      const steps = 60;
      const increment = target / steps;
      let current = 0;

      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          setDisplayValue(target);
          clearInterval(timer);
        } else {
          setDisplayValue(current);
        }
      }, duration / steps);

      return () => clearInterval(timer);
    } else {
      setDisplayValue(value as any);
    }
  }, [value]);

  const formatValue = (val: number | string): string => {
    if (typeof val === 'string') return val;
    
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'currency':
        return `₹${val.toLocaleString('en-IN')}`;
      default:
        return val.toFixed(1);
    }
  };

  const colorClasses = {
    primary: 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-300',
    secondary: 'bg-secondary-50 text-secondary-700 dark:bg-secondary-900/20 dark:text-secondary-300',
    accent: 'bg-accent-50 text-accent-700 dark:bg-accent-900/20 dark:text-accent-300',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="h-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </CardTitle>
          {icon && <div className={colorClasses[color]}>{icon}</div>}
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-gray-900 dark:text-white">
            {formatValue(displayValue)}
          </div>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
          {trend !== undefined && (
            <div className="mt-2 flex items-center text-xs">
              {trend > 0 ? (
                <>
                  <TrendingUp className="mr-1 h-4 w-4 text-green-600" />
                  <span className="text-green-600">+{trend.toFixed(1)}%</span>
                </>
              ) : trend < 0 ? (
                <>
                  <TrendingDown className="mr-1 h-4 w-4 text-red-600" />
                  <span className="text-red-600">{trend.toFixed(1)}%</span>
                </>
              ) : (
                <>
                  <Minus className="mr-1 h-4 w-4 text-gray-400" />
                  <span className="text-gray-400">No change</span>
                </>
              )}
              <span className="ml-1 text-gray-500">vs last period</span>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
