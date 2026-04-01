import { API_BASE_URL } from './constants';
import type {
  SurveyResponse,
  SummaryStatistics,
  PredictionRequest,
  SatisfactionPrediction,
  EfficiencyPrediction,
  ScenarioSimulation,
  CollegeCluster,
  Recommendation,
  FilterState,
  ReportOptions,
} from '@/types';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = localStorage.getItem('token');
    
    const headers: Record<string, string> = {
      ...options?.headers as Record<string, string>,
    };
    
    // Add Content-Type only if not FormData
    if (!(options?.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    
    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Data endpoints
  async submitResponse(data: Partial<SurveyResponse>): Promise<SurveyResponse> {
    return this.request<SurveyResponse>('/api/data/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getAllResponses(filters?: FilterState): Promise<SurveyResponse[]> {
    const params = new URLSearchParams();
    if (filters?.collegeIds) {
      filters.collegeIds.forEach(id => params.append('college_id', id));
    }
    if (filters?.respondentTypes) {
      filters.respondentTypes.forEach(type => params.append('respondent_type', type));
    }
    if (filters?.dateRange) {
      params.append('start_date', filters.dateRange.start);
      params.append('end_date', filters.dateRange.end);
    }
    
    const query = params.toString();
    return this.request<SurveyResponse[]>(`/api/data/all${query ? `?${query}` : ''}`);
  }

  async getSummaryStatistics(): Promise<SummaryStatistics> {
    return this.request<SummaryStatistics>('/api/data/summary');
  }

  async updateResponse(id: string, data: Partial<SurveyResponse>): Promise<SurveyResponse> {
    return this.request<SurveyResponse>(`/api/data/update/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteResponse(id: string): Promise<void> {
    return this.request<void>(`/api/data/delete/${id}`, {
      method: 'DELETE',
    });
  }

  async bulkImport(file: File): Promise<{ imported: number; errors: any[] }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseUrl}/api/data/bulk-import`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Bulk import failed');
    }

    return response.json();
  }

  // Analysis endpoints
  async getInfrastructureAnalysis(): Promise<any> {
    return this.request('/api/analysis/infrastructure');
  }

  async getSatisfactionAnalysis(): Promise<any> {
    return this.request('/api/analysis/satisfaction');
  }

  async getBarrierAnalysis(): Promise<any> {
    return this.request('/api/analysis/barriers');
  }

  async getCorrelationMatrix(): Promise<number[][]> {
    return this.request<number[][]>('/api/analysis/correlation');
  }

  async getHypothesisTests(): Promise<any> {
    return this.request('/api/analysis/hypothesis-tests');
  }

  // Prediction endpoints
  async predictSatisfaction(request: PredictionRequest): Promise<SatisfactionPrediction> {
    const response = await this.request<any>('/api/predict/satisfaction', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    
    // Handle different response formats
    if (response.status === 'success' && response.prediction) {
      return response.prediction;
    }
    return response;
  }

  async predictEfficiency(request: PredictionRequest): Promise<EfficiencyPrediction> {
    const response = await this.request<any>('/api/predict/efficiency', {
      method: 'POST',
      body: JSON.stringify(request),
    });
    
    // Handle different response formats
    if (response.status === 'success' && response.prediction) {
      return response.prediction;
    }
    return response;
  }

  async simulateScenario(current: PredictionRequest, proposed: PredictionRequest): Promise<ScenarioSimulation> {
    const response = await this.request<any>('/api/predict/scenario', {
      method: 'POST',
      body: JSON.stringify({ current, proposed }),
    });
    
    // Handle different response formats
    if (response.status === 'success' && response.simulation) {
      return response.simulation;
    }
    return response;
  }

  async getCollegeClusters(): Promise<CollegeCluster[]> {
    const response = await this.request<any>('/api/predict/clusters');
    
    // Handle different response formats
    if (response.status === 'success' && response.clusters) {
      return response.clusters;
    }
    return response.clusters || response;
  }

  async getRecommendations(collegeId: string): Promise<{ recommendations: Recommendation[] }> {
    const response = await this.request<any>(`/api/predict/recommendations?college_id=${collegeId}`);
    
    // Handle different response formats
    if (response.status === 'success' && response.recommendations) {
      return { recommendations: response.recommendations };
    }
    return response;
  }

  // Report endpoints
  async generateReport(options: ReportOptions): Promise<{ reportId: string; downloadUrl: string }> {
    return this.request<{ reportId: string; downloadUrl: string }>('/api/reports/generate', {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }

  async getReportTemplates(): Promise<any[]> {
    return this.request('/api/reports/templates');
  }

  async downloadReport(reportId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/reports/download/${reportId}`);
    if (!response.ok) {
      throw new Error('Failed to download report');
    }
    return response.blob();
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
