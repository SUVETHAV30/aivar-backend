import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Baselines from './pages/Baselines';
import Sessions from './pages/Sessions';
import Alerts from './pages/Alerts';
import Drift from './pages/Drift';
import Login from './pages/Login';

function RequireAuth({ children }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('token');
    const role  = localStorage.getItem('role');
    return token ? { token, role } : null;
  });

  const handleLogin = (data) => {
    setUser(data);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setUser(null);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />} />
        <Route
          path="/*"
          element={
            <RequireAuth>
              <Layout role={user?.role} onLogout={handleLogout}>
                <Routes>
                  <Route path="/"          element={<Dashboard />} />
                  <Route path="/agents"    element={<Agents />} />
                  <Route path="/baselines" element={<Baselines />} />
                  <Route path="/sessions"  element={<Sessions />} />
                  <Route path="/alerts"    element={<Alerts />} />
                  <Route path="/drift"     element={<Drift />} />
                </Routes>
              </Layout>
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
