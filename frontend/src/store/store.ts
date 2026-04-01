import { create } from 'zustand';
import type {
  SurveyResponse,
  College,
  User,
  FilterState,
  SatisfactionPrediction,
  EfficiencyPrediction,
  ScenarioSimulation,
} from '@/types';

interface Store {
  // Data
  responses: SurveyResponse[];
  currentCollege: College | null;
  user: User | null;
  token: string | null;
  
  // UI State
  isLoading: boolean;
  activeTab: string;
  filters: FilterState;
  darkMode: boolean;
  
  // ML State
  satisfactionPrediction: SatisfactionPrediction | null;
  efficiencyPrediction: EfficiencyPrediction | null;
  scenarioSimulation: ScenarioSimulation | null;
  
  // Actions
  setResponses: (responses: SurveyResponse[]) => void;
  addResponse: (response: SurveyResponse) => void;
  updateResponse: (id: string, data: Partial<SurveyResponse>) => void;
  deleteResponse: (id: string) => void;
  setCurrentCollege: (college: College | null) => void;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
  setActiveTab: (tab: string) => void;
  setFilters: (filters: FilterState) => void;
  toggleDarkMode: () => void;
  setSatisfactionPrediction: (prediction: SatisfactionPrediction | null) => void;
  setEfficiencyPrediction: (prediction: EfficiencyPrediction | null) => void;
  setScenarioSimulation: (simulation: ScenarioSimulation | null) => void;
}

export const useStore = create<Store>((set) => ({
  // Initial state
  responses: [],
  currentCollege: null,
  user: null,
  token: null,
  isLoading: false,
  activeTab: 'home',
  filters: {},
  darkMode: false,
  satisfactionPrediction: null,
  efficiencyPrediction: null,
  scenarioSimulation: null,
  
  // Actions
  setResponses: (responses) => set({ responses }),
  addResponse: (response) => set((state) => ({ responses: [...state.responses, response] })),
  updateResponse: (id, data) =>
    set((state) => ({
      responses: state.responses.map((r) => (r.id === id ? { ...r, ...data } : r)),
    })),
  deleteResponse: (id) =>
    set((state) => ({
      responses: state.responses.filter((r) => r.id !== id),
    })),
  setCurrentCollege: (college) => set({ currentCollege: college }),
  setUser: (user) => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
    set({ user });
  },
  setToken: (token) => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
    set({ token });
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ user: null, token: null });
  },
  setLoading: (isLoading) => set({ isLoading }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setFilters: (filters) => set({ filters }),
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  setSatisfactionPrediction: (prediction) => set({ satisfactionPrediction: prediction }),
  setEfficiencyPrediction: (prediction) => set({ efficiencyPrediction: prediction }),
  setScenarioSimulation: (simulation) => set({ scenarioSimulation: simulation }),
}));
