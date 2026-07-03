import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.alerts()
      .then(setAlerts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const severityMap = { Alert: 'red', Warning: 'amber', Normal: 'green' };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <>
      <div className="page-header">
        <div className="eyebrow">Monitoring</div>
        <h1>Security & Behavioral Alerts</h1>
        <p>Anomalies detected by the Isolation Forest model.</p>
      </div>

      <div className="table-wrapper">
        <div className="table-header">
          <h2>Alert History</h2>
          <span className="badge badge-amber">{alerts.length} total</span>
        </div>
        {alerts.length === 0 ? (
          <div className="empty-state">No alerts triggered. System operating normally.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Severity</th>
                <th>Message</th>
                <th>Anomaly Score</th>
                <th>Session ID</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map(a => (
                <tr key={a.id}>
                  <td style={{ color: 'var(--text-muted)' }}>#{a.id}</td>
                  <td>
                    <span className={`badge badge-${severityMap[a.severity] || 'blue'}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td style={{ fontWeight: 500 }}>{a.message}</td>
                  <td>
                    <div className="score-bar-wrap">
                      <div className="score-bar-bg">
                        <div className="score-bar-fill" style={{
                          width: `${Math.min(a.score, 100)}%`,
                          background: a.score > 35 ? 'var(--red)' : a.score > 15 ? 'var(--amber)' : 'var(--green)'
                        }} />
                      </div>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)', minWidth: 36 }}>
                        {a.score?.toFixed(1)}
                      </span>
                    </div>
                  </td>
                  <td style={{ color: 'var(--cyan)' }}>#{a.session_id}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                    {new Date(a.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
