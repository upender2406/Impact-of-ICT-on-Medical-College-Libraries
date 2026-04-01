import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(d);
}

export function formatNumber(num: number, decimals: number = 2): string {
  return num.toFixed(decimals);
}

export function calculateInfrastructureScore(infrastructure: {
  hardwareQuality: number;
  softwareAvailability: number;
  internetSpeed: number;
  digitalCollection: number;
}): number {
  const sum =
    infrastructure.hardwareQuality +
    infrastructure.softwareAvailability +
    infrastructure.internetSpeed +
    infrastructure.digitalCollection;
  return sum / 4;
}

export function calculateBarrierScore(barriers: {
  financialBarrier: number;
  technicalBarrier: number;
  trainingBarrier: number;
  policyBarrier: number;
}): number {
  const sum =
    barriers.financialBarrier +
    barriers.technicalBarrier +
    barriers.trainingBarrier +
    barriers.policyBarrier;
  return sum / 4;
}

export function getSatisfactionCategory(score: number): 'Low' | 'Medium' | 'High' {
  if (score <= 4) return 'Low';
  if (score <= 7) return 'Medium';
  return 'High';
}

export function getClusterColor(cluster: 'High' | 'Medium' | 'Low'): string {
  switch (cluster) {
    case 'High':
      return '#059669'; // green
    case 'Medium':
      return '#f59e0b'; // yellow
    case 'Low':
      return '#ef4444'; // red
    default:
      return '#6b7280'; // gray
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function downloadJSON(data: any, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function downloadCSV(data: any[], filename: string) {
  if (data.length === 0) return;
  
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(',')),
  ].join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
