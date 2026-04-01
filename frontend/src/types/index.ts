export interface College {
  id: string;
  name: string;
  code: string;
  district: string;
}

export interface Respondent {
  type: 'librarian' | 'user';
  name: string;
  position: string;
  email?: string;
}

export interface InfrastructureAssessment {
  hardwareQuality: number; // 1-5
  softwareAvailability: number; // 1-5
  internetSpeed: number; // 1-5
  digitalCollection: number; // 1-5
  automationSystem: 'None' | 'KOHA' | 'SOUL' | 'Other';
}

export interface ServiceQuality {
  overallSatisfaction: number; // 1-10
  serviceEfficiency: number; // 1-10
  staffHelpfulness: number; // 1-10
}

export interface BarriersAssessment {
  financialBarrier: number; // 1-5
  technicalBarrier: number; // 1-5
  trainingBarrier: number; // 1-5
  policyBarrier: number; // 1-5
}

export interface AdditionalInfo {
  weeklyVisits: number;
  ictTrainingReceived: boolean;
  remoteAccessAvailable: boolean;
  comments?: string;
}

export interface SurveyResponse {
  id: string;
  collegeId: string;
  collegeName: string;
  respondent: Respondent;
  infrastructure: InfrastructureAssessment;
  serviceQuality: ServiceQuality;
  barriers: BarriersAssessment;
  additionalInfo: AdditionalInfo;
  submittedAt: string;
  updatedAt?: string;
}

export interface SummaryStatistics {
  totalResponses: number;
  averageInfrastructureScore: number;
  averageSatisfaction: number;
  criticalBarriersCount: number;
  collegesCount: number;
  responsesByCollege: Record<string, number>;
  responsesByType: {
    librarian: number;
    user: number;
  };
}

export interface PredictionRequest {
  infrastructureScore: number;
  barrierScore: number;
  collegeId: string;
  automationSystem: string;
  awarenessLevel: number;
}

export interface SatisfactionPrediction {
  prediction: 'Low' | 'Medium' | 'High';
  confidence: number;
  probabilities: {
    Low: number;
    Medium: number;
    High: number;
  };
  featureImportance: Array<{
    feature: string;
    importance: number;
  }>;
}

export interface EfficiencyPrediction {
  predictedScore: number;
  confidenceInterval: {
    lower: number;
    upper: number;
  };
  improvementPotential: number;
  suggestions: string[];
}

export interface ScenarioSimulation {
  currentScore: number;
  predictedScore: number;
  improvement: number;
  improvementPercentage: number;
  estimatedCost: number;
  roi: number;
  timelineMonths: number;
}

export interface CollegeCluster {
  collegeId: string;
  collegeName: string;
  cluster: 'High' | 'Medium' | 'Low';
  coordinates: {
    x: number;
    y: number;
  };
  peers: string[];
  recommendations: string[];
}

export interface Recommendation {
  area: string;
  priority: number;
  action: string;
  expectedImpact: number;
  estimatedCost: number;
  timeline: string;
}

export interface FilterState {
  collegeIds?: string[];
  respondentTypes?: ('librarian' | 'user')[];
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'admin' | 'user';
  is_active: boolean;
}

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  sections: string[];
}

export interface ReportOptions {
  templateId: string;
  collegeIds: string[];
  sections: string[];
  includeCharts: boolean;
  language: 'en' | 'hi';
  branding?: {
    logo?: string;
    colors?: {
      primary: string;
      secondary: string;
    };
  };
}
