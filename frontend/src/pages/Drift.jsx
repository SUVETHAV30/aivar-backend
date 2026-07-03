import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Drift() {
  const [baselines, setBaselines] = useState([]);
  const [selectedBaseline, setSelectedBaseline] = useState('');
  const [driftData, setDriftData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [toast, setToast] = useState('');

  useEffect(() => {
    api.baselines()
      .then(setBaselines)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const notify = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const handleCheckDrift = async () => {
    if (!selectedBaseline) return notify('❌ Please select a baseline');
    setChecking(true);
    try {
      const data = await api.drift(selectedBaseline);
      setDriftData(data);
    } catch (err) {
      notify(`❌ ${err.message}`);
    } finally {
      setChecking(false);
    }
  };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <>
      <div className="page-header">
        <div className="eyebrow">Evaluation</div>
        <h1>Behavioral Drift</h1>
        <p>Monitor deviation of agent behavior over time using TVD (Total Variation Distance).</p>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 16 }}>Select Baseline to Analyze</h3>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <select 
            className="form-input" 
            style={{ width: 300 }}
            value={selectedBaseline} 
            onChange={e => { setSelectedBaseline(e.target.value); setDriftData(null); }}
          >
            <option value="">-- Choose Baseline --</option>
            {baselines.map(b => (
              <option key={b.id} value={b.id}>
                Baseline #{b.id} (Agent: {b.agent?.name || b.agent_id})
              </option>
            ))}
          </select>
          <button 
            className="btn btn-primary" 
            onClick={handleCheckDrift} 
            disabled={checking || !selectedBaseline}
          >
            {checking ? 'Analyzing…' : 'Check Drift Score'}
          </button>
        </div>
      </div>

      {driftData && (
        <div className="stats-grid">
          <div className="card">
            <div className="card-title">Drift Score (TVD)</div>
            <div className={`card-value ${driftData.drift_score > 0.5 ? 'red' : driftData.drift_score > 0.3 ? 'amber' : 'green'}`}>
              {(driftData.drift_score * 100).toFixed(1)}%
            </div>
            <div className="stat-delta">Total Variation Distance</div>
          </div>
          <div className="card">
            <div className="card-title">Recommendation</div>
            <div className="card-value cyan" style={{ fontSize: 24, marginTop: 8 }}>
              {driftData.recommendation}
            </div>
          </div>
        </div>
      )}

      {driftData?.history && driftData.history.length > 0 && (
        <div className="table-wrapper">
          <div className="table-header">
            <h2>Drift History</h2>
          </div>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Score</th>
                <th>Recommendation</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {driftData.history.map(h => (
                <tr key={h.id}>
                  <td style={{ color: 'var(--text-muted)' }}>#{h.id}</td>
                  <td>
                    <span className={`badge badge-${h.drift_score > 0.5 ? 'red' : h.drift_score > 0.3 ? 'amber' : 'green'}`}>
                      {(h.drift_score * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ fontWeight: 500 }}>{h.recommendation}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                    {new Date(h.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}
    </>
  );
}
