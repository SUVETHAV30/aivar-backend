import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    api.sessions()
      .then(setSessions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <>
      <div className="page-header">
        <div className="eyebrow">Monitoring</div>
        <h1>Production Sessions</h1>
        <p>Live stream of agent interactions and behavioral metrics.</p>
      </div>

      <div className="table-wrapper">
        <div className="table-header">
          <h2>Recorded Sessions</h2>
          <span className="badge badge-blue">{sessions.length} total</span>
        </div>
        {sessions.length === 0 ? (
          <div className="empty-state">No production sessions recorded yet.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Agent</th>
                <th>Scenario</th>
                <th>Latency (ms)</th>
                <th>Tools Used</th>
                <th>Errors</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map(s => {
                const metric = s.metrics?.[0] || {};
                return (
                  <tr key={s.id}>
                    <td style={{ color: 'var(--text-muted)' }}>#{s.id}</td>
                    <td style={{ fontWeight: 600 }}>{s.agent?.name || `Agent ${s.agent_id}`}</td>
                    <td>{s.scenario?.title || `Scenario ${s.scenario_id}`}</td>
                    <td>{metric.latency_ms || '-'}</td>
                    <td>{metric.tool_count || 0}</td>
                    <td>
                      {metric.error_count > 0 ? (
                        <span className="badge badge-red">{metric.error_count}</span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>0</span>
                      )}
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                      {new Date(s.created_at).toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
