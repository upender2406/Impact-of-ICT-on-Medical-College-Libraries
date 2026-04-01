import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { API_BASE_URL } from '@/lib/constants';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import toast from 'react-hot-toast';
import {
  FileDown,
  FileText,
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  Building2,
  Calendar,
  Filter,
  Download
} from 'lucide-react';
import { format as formatDate } from 'date-fns';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  type: 'summary' | 'detailed' | 'comparative' | 'trend';
}

const REPORT_TEMPLATES: ReportTemplate[] = [
  {
    id: 'executive-summary',
    name: 'Executive Summary',
    description: 'High-level overview of ICT infrastructure and satisfaction metrics',
    icon: <FileText className="h-6 w-6" />,
    type: 'summary'
  },
  {
    id: 'infrastructure-analysis',
    name: 'Infrastructure Analysis',
    description: 'Detailed analysis of hardware, software, and connectivity infrastructure',
    icon: <Building2 className="h-6 w-6" />,
    type: 'detailed'
  },
  {
    id: 'satisfaction-report',
    name: 'User Satisfaction Report',
    description: 'Comprehensive analysis of user satisfaction and service quality',
    icon: <Users className="h-6 w-6" />,
    type: 'detailed'
  },
  {
    id: 'comparative-analysis',
    name: 'College Comparison',
    description: 'Side-by-side comparison of different medical colleges',
    icon: <BarChart3 className="h-6 w-6" />,
    type: 'comparative'
  },
  {
    id: 'trend-analysis',
    name: 'Trend Analysis',
    description: 'Time-based analysis showing trends and patterns',
    icon: <TrendingUp className="h-6 w-6" />,
    type: 'trend'
  },
  {
    id: 'barriers-report',
    name: 'Barriers Assessment',
    description: 'Analysis of barriers to ICT adoption and implementation',
    icon: <PieChart className="h-6 w-6" />,
    type: 'detailed'
  }
];

export function Reports() {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    dateRange: 'all',
    colleges: 'all',
    respondentType: 'all'
  });
  const [generatingReport, setGeneratingReport] = useState(false);

  // Fetch data for reports
  const { data: responses = [], isLoading } = useQuery({
    queryKey: ['responses'],
    queryFn: () => apiClient.getAllResponses(),
  });

  const { data: summary } = useQuery({
    queryKey: ['summary'],
    queryFn: () => apiClient.getSummaryStatistics(),
  });

  const generateReport = async (templateId: string, exportFormat: string = 'json') => {
    setGeneratingReport(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/generate?format=${exportFormat}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: templateId,
          college_ids: [],
          sections: ['summary', 'data', 'charts'],
          include_charts: true,
          language: 'en'
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to generate report' }));
        throw new Error(errorData.detail || 'Failed to generate report');
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Get filename from response headers or create default
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `${templateId}-report-${formatDate(new Date(), 'yyyy-MM-dd')}.${exportFormat}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success(`${exportFormat.toUpperCase()} report downloaded successfully!`);

    } catch (error: any) {
      console.error('Error generating report:', error);
      toast.error(error.message || 'Failed to generate report. Please try again.');
    } finally {
      setGeneratingReport(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Loading reports...</div>
          <div className="text-sm text-gray-400">Preparing data</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Reports & Analytics
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Generate comprehensive reports and export data insights
          </p>
        </div>
        <Button onClick={() => {
          toast.success('Schedule Report feature coming soon!');
        }}>
          <Calendar className="mr-2 h-4 w-4" />
          Schedule Report
        </Button>
      </div>

      {/* Report Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Available Data
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {responses.length}
                </p>
                <p className="text-xs text-gray-500">survey responses</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Colleges Covered
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {summary?.collegesCount || 0}
                </p>
                <p className="text-xs text-gray-500">medical colleges</p>
              </div>
              <Building2 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Report Templates
                </p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">
                  {REPORT_TEMPLATES.length}
                </p>
                <p className="text-xs text-gray-500">available formats</p>
              </div>
              <BarChart3 className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Last Updated
                </p>
                <p className="mt-2 text-lg font-bold text-gray-900 dark:text-white">
                  {formatDate(new Date(), 'MMM dd')}
                </p>
                <p className="text-xs text-gray-500">data refresh</p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="mr-2 h-5 w-5" />
            Report Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="block text-sm font-medium mb-2">Date Range</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={filters.dateRange}
                onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
              >
                <option value="all">All Time</option>
                <option value="last-month">Last Month</option>
                <option value="last-quarter">Last Quarter</option>
                <option value="last-year">Last Year</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Colleges</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={filters.colleges}
                onChange={(e) => setFilters({ ...filters, colleges: e.target.value })}
              >
                <option value="all">All Colleges</option>
                <option value="tier-1">Tier 1 Colleges</option>
                <option value="tier-2">Tier 2 Colleges</option>
                <option value="tier-3">Tier 3 Colleges</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Respondent Type</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                value={filters.respondentType}
                onChange={(e) => setFilters({ ...filters, respondentType: e.target.value })}
              >
                <option value="all">All Respondents</option>
                <option value="librarian">Librarians</option>
                <option value="user">Users</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report Templates */}
      <div>
        <h2 className="text-xl font-bold mb-4">Available Report Templates</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {REPORT_TEMPLATES.map((template) => (
            <Card
              key={template.id}
              className={`cursor-pointer transition-all hover:shadow-lg ${selectedTemplate === template.id ? 'ring-2 ring-blue-500' : ''
                }`}
              onClick={() => setSelectedTemplate(template.id)}
            >
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                      {template.icon}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {template.name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      {template.description}
                    </p>
                    <div className="mt-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${template.type === 'summary' ? 'bg-green-100 text-green-800' :
                        template.type === 'detailed' ? 'bg-blue-100 text-blue-800' :
                          template.type === 'comparative' ? 'bg-purple-100 text-purple-800' :
                            'bg-orange-100 text-orange-800'
                        }`}>
                        {template.type}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex space-x-2">
                  <Button
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      generateReport(template.id, 'json');
                    }}
                    disabled={generatingReport}
                  >
                    {generatingReport ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        <Download className="mr-2 h-4 w-4" />
                        JSON
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      generateReport(template.id, 'excel');
                    }}
                    disabled={generatingReport}
                  >
                    {generatingReport ? 'Generating...' : 'Excel'}
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      generateReport(template.id, 'pdf');
                    }}
                    disabled={generatingReport}
                  >
                    {generatingReport ? 'Generating...' : 'PDF'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Quick Export Options */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Export Options</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <Button
              variant="outline"
              className="h-20 flex-col"
              onClick={() => generateReport('executive-summary', 'json')}
              disabled={generatingReport}
            >
              <FileDown className="h-6 w-6 mb-2" />
              {generatingReport ? 'Generating...' : 'Export JSON'}
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col"
              onClick={() => generateReport('executive-summary', 'excel')}
              disabled={generatingReport}
            >
              <FileText className="h-6 w-6 mb-2" />
              {generatingReport ? 'Generating...' : 'Export Excel'}
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col"
              onClick={() => generateReport('executive-summary', 'pdf')}
              disabled={generatingReport}
            >
              <BarChart3 className="h-6 w-6 mb-2" />
              {generatingReport ? 'Generating...' : 'Export PDF'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}