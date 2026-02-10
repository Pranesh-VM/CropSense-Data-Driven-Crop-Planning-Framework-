import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';

// Auth Pages
import { Welcome } from './pages/auth/Welcome';
import { Login } from './pages/auth/Login';
import { Signup } from './pages/auth/Signup';

// App Pages
import { Dashboard } from './pages/dashboard/Dashboard';
import { QuickRecommendation } from './pages/recommendation/QuickRecommendation';
import { NewCycle } from './pages/cycle/NewCycle';
import { ActiveCycle } from './pages/cycle/ActiveCycle';
import { CycleHistory } from './pages/cycle/CycleHistory';
import { Profile } from './pages/profile/Profile';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Auth Routes */}
            <Route path="/welcome" element={<Welcome />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Protected Routes */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <div className="flex flex-col md:flex-row min-h-screen">
                    <Sidebar />
                    <div className="flex-1 flex flex-col">
                      <Header />
                      <main className="flex-1 bg-gray-50">
                        <Routes>
                          <Route path="/dashboard" element={<Dashboard />} />
                          <Route path="/quick-recommendation" element={<QuickRecommendation />} />
                          <Route path="/cycle/new" element={<NewCycle />} />
                          <Route path="/cycle/active" element={<ActiveCycle />} />
                          <Route path="/cycle/history" element={<CycleHistory />} />
                          <Route path="/profile" element={<Profile />} />
                          <Route path="*" element={<Navigate to="/dashboard" replace />} />
                        </Routes>
                      </main>
                    </div>
                  </div>
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/welcome" replace />} />
          </Routes>

          {/* Toast Notifications */}
          <ToastContainer
            position="top-right"
            autoClose={4000}
            hideProgressBar={false}
            newestOnTop={true}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
