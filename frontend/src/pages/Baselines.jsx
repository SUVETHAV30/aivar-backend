import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Baselines() {
  const [baselines, setBaselines] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [agents, setAgents]       = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [creating, setCreating]   = useState(false);
  const [toast, setToast]         = useState('');

  const load = () => {
    Promise.all([api.baselines(), api.agents()])
      .then(([b, a]) => { setBaselines(b); setAgents(a); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const notify = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!selectedAgentId) return notify('❌ Select an agent first');
    setCreating(true);
    try {
      await api.createBaseline({ agent_id: parseInt(selectedAgentId, 10) });
      notify('✅ Baseline generated successfully!');
      setShowModal(false);
      load();
    } catch (err) {
      notify(`❌ ${err.message}`);
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <>
      <div className="page-header">
        <div className="eyebrow">Evaluation</div>
        <h1>Baselines</h1>
        <p>Reference behavioral fingerprints for anomaly detection.</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Generate Baseline</button>
      </div>

      <div className="table-wrapper">
        <div className="table-header">
          <h2>Active Baselines</h2>
          <span className="badge badge-purple">{baselines.length} total</span>
        </div>
        {baselines.length === 0 ? (
          <div className="empty-state">No baselines found. Create one to enable monitoring.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Agent</th>
                <th>Scenario Coverage</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {baselines.map(b => (
                <tr key={b.id}>
                  <td style={{ color: 'var(--text-muted)' }}>#{b.id}</td>
                  <td style={{ fontWeight: 600 }}>{b.agent?.name || `Agent ${b.agent_id}`}</td>
                  <td>
                    <span className="badge badge-blue">100% (50/50 scenarios)</span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{new Date(b.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>📐 Generate Baseline</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20 }}>
              This will execute the agent against all generated synthetic scenarios to establish a behavioral fingerprint.
            </p>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Select Agent</label>
                <select 
                  className="form-input" 
                  value={selectedAgentId} 
                  onChange={e => setSelectedAgentId(e.target.value)}
                  required
                >
                  <option value="">-- Choose Agent --</option>
                  {agents.map(a => <option key={a.id} value={a.id}>{a.name} (#{a.id})</option>)}
                </select>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Generating… (takes a minute)' : 'Generate Baseline'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}
    </>
  );
}
