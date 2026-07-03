import { useEffect, useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, Title, Tooltip, Legend,
} from 'chart.js';
import { api } from '../api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#8b9cb8', font: { size: 12 } } } },
  scales: {
    x: { ticks: { color: '#4b5563' }, grid: { color: 'rgba(255,255,255,0.04)' } },
    y: { ticks: { color: '#4b5563' }, grid: { color: 'rgba(255,255,255,0.04)' } },
  },
};

const STAT_CARDS = [
  { key: 'agent_count',    label: 'Agents',     icon: '🤖', color: 'cyan'   },
  { key: 'baseline_count', label: 'Baselines',  icon: '📐', color: 'purple' },
  { key: 'session_count',  label: 'Sessions',   icon: '📡', color: 'blue'   },
  { key: 'alert_count',    label: 'Alerts',     icon: '🔔', color: 'amber'  },
  { key: 'drift_count',    label: 'Drift Events', icon: '📈', color: 'green' },
];

export default function Dashboard() {
  const [stats, setStats]   = useState({});
  const [alerts, setAlerts] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.stats(), api.alerts(), api.health()])
      .then(([s, a, h]) => { setStats(s); setAlerts(a.slice(0, 5)); setHealth(h); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const alertsByDay = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map((_, i) =>
    alerts.filter(a => new Date(a.created_at).getDay() === i).length
  );

  const trendData = {
    labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
    datasets: [{
      label: 'Alerts per day',
      data: alertsByDay,
      backgroundColor: 'rgba(167,139,250,0.35)',
      borderColor: '#a78bfa',
      borderRadius: 6,
    }],
  };

  const severityMap = { Alert: 'red', Warning: 'amber', Normal: 'green' };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <>
      <div className="page-header">
        <div className="eyebrow">Production AI Monitoring</div>
        <h1>Dashboard</h1>
        <p>Real-time behavioral baseline monitoring for enterprise AI agents.</p>
      </div>

      {/* Health Banner */}
      <div className="card" style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
        <span className={`status-dot dot-${health?.status === 'healthy' ? 'green' : 'red'}`} />
        <span style={{ fontWeight: 600 }}>API Status:</span>
        <span style={{ color: health?.status === 'healthy' ? 'var(--green)' : 'var(--red)' }}>
          {health?.status ?? 'unknown'}
        </span>
      </div>

      {/* Stat Cards */}
      <div className="stats-grid">
        {STAT_CARDS.map(({ key, label, icon, color }) => (
          <div key={key} className="card">
            <div className="card-title">{icon} {label}</div>
            <div className={`card-value ${color}`}>{stats[key] ?? 0}</div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div className="chart-wrapper">
        <h2>Alert Activity (this week)</h2>
        <div className="chart-inner">
          <Bar data={trendData} options={chartOpts} />
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="table-wrapper">
        <div className="table-header">
          <h2>Recent Alerts</h2>
          <span className="badge badge-red">{alerts.length} shown</span>
        </div>
        {alerts.length === 0 ? (
          <div className="empty-state">No alerts yet — system looks healthy 🎉</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Severity</th>
                <th>Message</th>
                <th>Score</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(a => (
                <tr key={a.id}>
                  <td><span className={`badge badge-${severityMap[a.severity] || 'blue'}`}>{a.severity}</span></td>
                  <td>{a.message}</td>
                  <td>
                    <div className="score-bar-wrap">
                      <div className="score-bar-bg">
                        <div className="score-bar-fill" style={{
                          width: `${Math.min(a.score, 100)}%`,
                          background: a.score > 35 ? 'var(--red)' : a.score > 15 ? 'var(--amber)' : 'var(--green)'
                        }} />
                      </div>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)', minWidth: 36 }}>{a.score?.toFixed(1)}</span>
                    </div>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{new Date(a.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
