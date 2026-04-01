import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { Navbar } from '@/components/layout/Navbar';
import { Sidebar } from '@/components/layout/Sidebar';
import { Footer } from '@/components/layout/Footer';
import { Home } from '@/pages/Home';
import { DataEntry } from '@/pages/DataEntry';
import { Analysis } from '@/pages/Analysis';
import PredictionLabPage from '@/pages/PredictionLab';
import { Reports } from '@/pages/Reports';
import { Admin } from '@/pages/Admin';
import { Login } from '@/pages/Login';
import { Signup } from '@/pages/Signup';
import { AuthHome } from '@/pages/AuthHome';
import { useStore } from '@/store/store';
import { useEffect, useState } from 'react';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route Component
function ProtectedRoute({ children, requireAdmin = false }: { children: React.ReactNode; requireAdmin?: boolean }) {
  const { user, token } = useStore();
  
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  
  if (requireAdmin && user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
}

function AppContent() {
  const { darkMode, user, token, setUser, setToken } = useStore();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Initialize authentication state from localStorage
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');
        
        if (storedToken && storedUser) {
          const parsedUser = JSON.parse(storedUser);
          if (parsedUser && parsedUser.id && parsedUser.email) {
            setToken(storedToken);
            setUser(parsedUser);
          } else {
            // Clear invalid data
            localStorage.removeItem('token');
            localStorage.removeItem('user');
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        setAuthChecked(true);
      }
    };

    initAuth();
  }, [setUser, setToken]);

  // Show loading while checking auth
  if (!authChecked) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  const isAuthenticated = !!(token && user);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {isAuthenticated ? (
        <>
          <Navbar />
          <div className="flex">
            <Sidebar />
            <main className="flex-1 lg:ml-64 pt-16">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/data-entry" element={<DataEntry />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/prediction-lab" element={<PredictionLabPage />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/admin" element={
                  user.role === 'admin' ? <Admin /> : <Navigate to="/" replace />
                } />
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="/signup" element={<Navigate to="/" replace />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </div>
          <Footer />
        </>
      ) : (
        <Routes>
          <Route path="/" element={<AuthHome />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      )}
      <Toaster position="top-right" />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
