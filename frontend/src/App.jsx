import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import AuditHistory from './pages/AuditHistory';
import SubmitWebsite from './pages/SubmitWebsite';
import SubmitHistory from './pages/SubmitHistory';
import ProtectedRoute from './components/ProtectedRoute';
import AppShell from './components/AppShell';
import ThreeBackground from './components/ThreeBackground';

function ProtectedPage({ children }) {
  return (
    <ProtectedRoute>
      <AppShell>{children}</AppShell>
    </ProtectedRoute>
  );
}

function PublicPage({ children }) {
  return (
    <>
      <ThreeBackground variant="auth" />
      {children}
    </>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/seo-audit" replace />} />
          <Route
            path="/seo-audit"
            element={
              <ProtectedPage>
                <Dashboard />
              </ProtectedPage>
            }
          />
          <Route
            path="/seo-audit/history"
            element={
              <ProtectedPage>
                <AuditHistory />
              </ProtectedPage>
            }
          />
          <Route
            path="/submit-website"
            element={
              <ProtectedPage>
                <SubmitWebsite />
              </ProtectedPage>
            }
          />
          <Route
            path="/submit-website/history"
            element={
              <ProtectedPage>
                <SubmitHistory />
              </ProtectedPage>
            }
          />
          <Route
            path="/submit-website/:platformCode"
            element={
              <ProtectedPage>
                <SubmitWebsite />
              </ProtectedPage>
            }
          />
          <Route path="/login" element={<PublicPage><Login /></PublicPage>} />
          <Route path="/register" element={<PublicPage><Register /></PublicPage>} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
