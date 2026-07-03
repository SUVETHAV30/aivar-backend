import { useEffect, useState } from 'react';
import { api } from '../api';

export default function Agents() {
  const [agents, setAgents]       = useState([]);
  const [loading, setLoading]     = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm]           = useState({ name: '', prompt: '', tool_list: '' });
  const [saving, setSaving]       = useState(false);
  const [toast, setToast]         = useState('');
  const [genLoading, setGenLoading] = useState(null); // agent id being generated for

  const load = () => api.agents().then(setAgents).catch(console.error).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const notify = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const tools = form.tool_list.split(',').map(t => t.trim()).filter(Boolean);
      const agent = await api.createAgent({ name: form.name, prompt: form.prompt, tool_list: tools });
      notify(`✅ Agent "${agent.name}" created!`);
      setShowModal(false);
      setForm({ name: '', prompt: '', tool_list: '' });
      load();
    } catch (err) {
      notify(`❌ ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleGenScenarios = async (agent) => {
    setGenLoading(agent.id);
    try {
      const res = await api.genScenarios({ agent_id: agent.id, agent_prompt: agent.prompt, tool_list: agent.tool_list });
      notify(`✅ Generated ${res.count} scenarios for "${agent.name}"`);
    } catch (err) {
      notify(`❌ ${err.message}`);
    } finally {
      setGenLoading(null);
    }
  };

  if (loading) return <div className="loading"><div className="spinner" /></div>;

  return (
    <>
      <div className="page-header">
        <div className="eyebrow">Management</div>
        <h1>Agents</h1>
        <p>Register AI agents and generate synthetic test scenarios.</p>
      </div>

      <div style={{ marginBottom: 20 }}>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ New Agent</button>
      </div>

      <div className="table-wrapper">
        <div className="table-header">
          <h2>Registered Agents</h2>
          <span className="badge badge-cyan">{agents.length} total</span>
        </div>
        {agents.length === 0 ? (
          <div className="empty-state">No agents yet. Create your first agent above.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Tools</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {agents.map(a => (
                <tr key={a.id}>
                  <td style={{ color: 'var(--text-muted)' }}>#{a.id}</td>
                  <td style={{ fontWeight: 600 }}>{a.name}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {(a.tool_list || []).map(t => (
                        <span key={t} className="badge badge-purple">{t}</span>
                      ))}
                    </div>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{new Date(a.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-ghost"
                      style={{ padding: '6px 12px', fontSize: 12 }}
                      onClick={() => handleGenScenarios(a)}
                      disabled={genLoading === a.id}
                    >
                      {genLoading === a.id ? '⏳ Generating…' : '⚡ Gen Scenarios'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>🤖 Create New Agent</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Agent Name</label>
                <input className="form-input" placeholder="e.g. Customer Support Bot" required
                  value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">System Prompt</label>
                <textarea className="form-textarea" placeholder="Describe what this agent does…" required
                  value={form.prompt} onChange={e => setForm(f => ({ ...f, prompt: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Tools (comma-separated)</label>
                <input className="form-input" placeholder="search, write, calendar"
                  value={form.tool_list} onChange={e => setForm(f => ({ ...f, tool_list: e.target.value }))} />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Creating…' : 'Create Agent'}
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
