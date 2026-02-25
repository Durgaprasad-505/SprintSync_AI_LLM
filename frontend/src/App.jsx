import { useState, useEffect, useCallback } from 'react';
import { api } from './api';

/* ─── Design tokens ──────────────────────────────────────────────────────── */
const STATUS_META = {
  backlog:     { label: 'Backlog',     color: '#4a4a6a', bg: '#1a1a2e', next: ['in_progress'] },
  in_progress: { label: 'In Progress', color: '#f0a500', bg: '#2a1f00', next: ['review', 'backlog'] },
  review:      { label: 'Review',      color: '#00b4d8', bg: '#001a2e', next: ['done', 'in_progress'] },
  done:        { label: 'Done',        color: '#06d6a0', bg: '#002e22', next: [] },
};

/* ─── Global styles ──────────────────────────────────────────────────────── */
const GLOBAL_CSS = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0d0d14;
    --surface: #13131f;
    --surface2: #1a1a2e;
    --border: #2a2a40;
    --text: #e8e8f0;
    --muted: #6b6b8a;
    --accent: #7c3aed;
    --accent2: #f0a500;
    --danger: #ef4444;
    --radius: 8px;
    --font-body: 'Syne', sans-serif;
    --font-mono: 'IBM Plex Mono', monospace;
  }
  body { background: var(--bg); color: var(--text); font-family: var(--font-body); min-height: 100vh; }
  button { cursor: pointer; font-family: inherit; }
  input, textarea, select { font-family: inherit; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

/* ─── Tiny helpers ───────────────────────────────────────────────────────── */
function Badge({ status }) {
  const m = STATUS_META[status] || STATUS_META.backlog;
  return (
    <span style={{
      display: 'inline-block', padding: '2px 10px', borderRadius: 20,
      background: m.bg, color: m.color, fontSize: 11, fontFamily: 'var(--font-mono)',
      fontWeight: 600, letterSpacing: '0.08em', border: `1px solid ${m.color}44`,
      textTransform: 'uppercase',
    }}>{m.label}</span>
  );
}

function Btn({ children, variant = 'primary', size = 'md', loading, ...props }) {
  const styles = {
    primary: { background: 'var(--accent)', color: '#fff', border: 'none' },
    secondary: { background: 'transparent', color: 'var(--text)', border: '1px solid var(--border)' },
    danger: { background: 'transparent', color: 'var(--danger)', border: `1px solid var(--danger)44` },
    ghost: { background: 'transparent', color: 'var(--muted)', border: 'none' },
  };
  const sizes = {
    sm: { padding: '4px 12px', fontSize: 12 },
    md: { padding: '8px 18px', fontSize: 13 },
    lg: { padding: '12px 28px', fontSize: 15 },
  };
  return (
    <button
      {...props}
      disabled={loading || props.disabled}
      style={{
        borderRadius: 'var(--radius)', fontWeight: 600, transition: 'all .15s',
        opacity: (loading || props.disabled) ? 0.5 : 1,
        ...styles[variant], ...sizes[size], ...props.style,
      }}
    >
      {loading ? '…' : children}
    </button>
  );
}

function Input({ label, error, ...props }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && <span style={{ fontSize: 12, color: 'var(--muted)', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{label}</span>}
      {props.type === 'textarea'
        ? <textarea {...props} rows={3} style={{ background: 'var(--surface2)', border: `1px solid ${error ? 'var(--danger)' : 'var(--border)'}`, borderRadius: 'var(--radius)', color: 'var(--text)', padding: '10px 14px', fontSize: 14, resize: 'vertical', outline: 'none', ...props.style }} />
        : <input {...props} style={{ background: 'var(--surface2)', border: `1px solid ${error ? 'var(--danger)' : 'var(--border)'}`, borderRadius: 'var(--radius)', color: 'var(--text)', padding: '10px 14px', fontSize: 14, outline: 'none', ...props.style }} />
      }
      {error && <span style={{ fontSize: 12, color: 'var(--danger)' }}>{error}</span>}
    </label>
  );
}

/* ─── Login page ─────────────────────────────────────────────────────────── */
function LoginPage({ onLogin }) {
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ username: '', password: '', email: '' });
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(''); setLoading(true);
    try {
      if (tab === 'login') {
        const { access_token } = await api.login(form.username, form.password);
        localStorage.setItem('ss_token', access_token);
        onLogin();
      } else {
        await api.register({ email: form.email, username: form.username, password: form.password });
        setTab('login');
        setErr('Registered! Please log in.');
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 20, background: 'radial-gradient(ellipse at 50% 0%, #1e0a3c 0%, var(--bg) 60%)' }}>
      <div style={{ animation: 'fadeIn .5s ease', width: '100%', maxWidth: 380 }}>
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--accent)', letterSpacing: '0.2em', marginBottom: 8 }}>◈ CODESTRAT LABS</div>
          <h1 style={{ fontSize: 42, fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, #fff 40%, #7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>SprintSync</h1>
          <p style={{ color: 'var(--muted)', fontSize: 14, marginTop: 6 }}>Engineering work tracker + AI planning</p>
        </div>

        <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: '28px 32px' }}>
          <div style={{ display: 'flex', gap: 4, marginBottom: 24, background: 'var(--surface2)', borderRadius: 8, padding: 4 }}>
            {['login', 'register'].map(t => (
              <button key={t} onClick={() => { setTab(t); setErr(''); }} style={{ flex: 1, padding: '8px', borderRadius: 6, border: 'none', background: tab === t ? 'var(--accent)' : 'transparent', color: tab === t ? '#fff' : 'var(--muted)', fontSize: 13, fontWeight: 600, fontFamily: 'inherit', transition: 'all .15s', textTransform: 'capitalize' }}>{t}</button>
            ))}
          </div>

          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {tab === 'register' && <Input label="Email" type="email" placeholder="you@company.com" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />}
            <Input label="Username" type="text" placeholder="alice" value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} required />
            <Input label="Password" type="password" placeholder="••••••••" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required />
            {err && <div style={{ fontSize: 13, color: err.includes('Registered') ? '#06d6a0' : 'var(--danger)', padding: '8px 12px', background: err.includes('Registered') ? '#002e22' : '#2e0000', borderRadius: 6 }}>{err}</div>}
            <Btn type="submit" loading={loading} size="lg" style={{ marginTop: 4 }}>
              {tab === 'login' ? 'Sign In' : 'Create Account'}
            </Btn>
          </form>
        </div>

        <p style={{ textAlign: 'center', marginTop: 16, fontSize: 12, color: 'var(--muted)' }}>
          Demo: <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent2)' }}>alice / alice123</code> · <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent2)' }}>admin / admin123</code>
        </p>
      </div>
    </div>
  );
}

/* ─── Task card ──────────────────────────────────────────────────────────── */
function TaskCard({ task, onRefresh }) {
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ title: task.title, description: task.description, total_minutes: task.total_minutes });
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [transitioning, setTransitioning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const next = STATUS_META[task.status]?.next || [];

  const handleTransition = async (status) => {
    setTransitioning(true);
    try { await api.tasks.transition(task.id, status); onRefresh(); }
    catch (e) { alert(e.message); }
    finally { setTransitioning(false); }
  };

  const handleSave = async () => {
    setSaving(true);
    try { await api.tasks.update(task.id, form); onRefresh(); setEditing(false); }
    catch (e) { alert(e.message); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!confirm('Delete this task?')) return;
    setDeleting(true);
    try { await api.tasks.delete(task.id); onRefresh(); }
    catch (e) { alert(e.message); setDeleting(false); }
  };

  const handleAISuggest = async () => {
    setAiLoading(true); setAiResult(null);
    try {
      const r = await api.ai.suggest('description', task.title);
      setAiResult(r);
    } catch (e) { alert(e.message); }
    finally { setAiLoading(false); }
  };

  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden', animation: 'fadeIn .3s ease', transition: 'border-color .2s' }}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)44'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
    >
      <div style={{ padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }} onClick={() => setExpanded(x => !x)}>
        <Badge status={task.status} />
        <span style={{ flex: 1, fontWeight: 600, fontSize: 15 }}>{task.title}</span>
        <span style={{ fontSize: 12, color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>{task.total_minutes}m</span>
        <span style={{ color: 'var(--muted)', fontSize: 18, lineHeight: 1 }}>{expanded ? '−' : '+'}</span>
      </div>

      {expanded && (
        <div style={{ padding: '0 18px 18px', borderTop: '1px solid var(--border)' }}>
          {editing ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, paddingTop: 16 }}>
              <Input label="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
              <Input label="Description" type="textarea" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
              <Input label="Minutes logged" type="number" min="0" value={form.total_minutes} onChange={e => setForm(f => ({ ...f, total_minutes: Number(e.target.value) }))} />
              <div style={{ display: 'flex', gap: 8 }}>
                <Btn onClick={handleSave} loading={saving} size="sm">Save</Btn>
                <Btn variant="ghost" size="sm" onClick={() => setEditing(false)}>Cancel</Btn>
              </div>
            </div>
          ) : (
            <div style={{ paddingTop: 14, display: 'flex', flexDirection: 'column', gap: 12 }}>
              {task.description && <p style={{ fontSize: 14, color: 'var(--muted)', lineHeight: 1.6 }}>{task.description}</p>}

              {/* AI suggestion */}
              <div style={{ background: 'var(--surface2)', borderRadius: 8, padding: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: aiResult ? 8 : 0 }}>
                  <span style={{ fontSize: 12, color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>◈ AI ASSIST</span>
                  <Btn variant="ghost" size="sm" onClick={handleAISuggest} loading={aiLoading} style={{ color: 'var(--accent)', fontSize: 12 }}>
                    {aiLoading ? 'Thinking…' : 'Suggest description'}
                  </Btn>
                </div>
                {aiResult && (
                  <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6, borderTop: '1px solid var(--border)', paddingTop: 8 }}>
                    <div style={{ color: 'var(--muted)', fontSize: 11, fontFamily: 'var(--font-mono)', marginBottom: 4 }}>source: {aiResult.source}</div>
                    {aiResult.description}
                    <Btn size="sm" variant="secondary" style={{ marginTop: 8 }} onClick={() => { setForm(f => ({ ...f, description: aiResult.description })); setEditing(true); }}>Use this</Btn>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
                {next.map(s => (
                  <Btn key={s} variant="secondary" size="sm" onClick={() => handleTransition(s)} loading={transitioning}
                    style={{ borderColor: STATUS_META[s]?.color + '66', color: STATUS_META[s]?.color }}>
                    → {STATUS_META[s]?.label}
                  </Btn>
                ))}
                <Btn variant="ghost" size="sm" onClick={() => setEditing(true)} style={{ marginLeft: 'auto' }}>Edit</Btn>
                <Btn variant="danger" size="sm" onClick={handleDelete} loading={deleting}>Delete</Btn>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Create task modal ──────────────────────────────────────────────────── */
function CreateTaskModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ title: '', description: '', total_minutes: 0 });
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return setErr('Title required');
    setLoading(true);
    try { await api.tasks.create(form); onCreated(); onClose(); }
    catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#000a', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 20 }}>
      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 28, width: '100%', maxWidth: 480, animation: 'fadeIn .2s ease' }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>New Task</h2>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Input label="Title" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="e.g. Implement auth middleware" />
          <Input label="Description" type="textarea" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Optional initial description" />
          <Input label="Minutes logged" type="number" min="0" value={form.total_minutes} onChange={e => setForm(f => ({ ...f, total_minutes: Number(e.target.value) }))} />
          {err && <div style={{ color: 'var(--danger)', fontSize: 13 }}>{err}</div>}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 4 }}>
            <Btn variant="ghost" onClick={onClose}>Cancel</Btn>
            <Btn type="submit" loading={loading}>Create Task</Btn>
          </div>
        </form>
      </div>
    </div>
  );
}

/* ─── Daily plan panel ───────────────────────────────────────────────────── */
function DailyPlanPanel({ onClose }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  useEffect(() => {
    api.ai.suggest('daily_plan')
      .then(setPlan)
      .catch(e => setErr(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#000a', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 20 }}>
      <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: 28, width: '100%', maxWidth: 520, animation: 'fadeIn .2s ease', maxHeight: '85vh', overflow: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--accent)', letterSpacing: '0.1em', marginBottom: 4 }}>◈ AI ASSIST</div>
            <h2 style={{ fontSize: 20, fontWeight: 700 }}>Your Daily Plan</h2>
          </div>
          <Btn variant="ghost" onClick={onClose} style={{ fontSize: 20, lineHeight: 1 }}>×</Btn>
        </div>

        {loading && <div style={{ textAlign: 'center', color: 'var(--muted)', padding: 40, fontFamily: 'var(--font-mono)', animation: 'pulse 1.5s infinite' }}>Generating plan…</div>}
        {err && <div style={{ color: 'var(--danger)' }}>{err}</div>}
        {plan && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--muted)', marginBottom: 8 }}>source: {plan.source}</div>
            {plan.plan?.map((item, i) => (
              <div key={i} style={{ display: 'flex', gap: 16, padding: '10px 14px', background: 'var(--surface2)', borderRadius: 8 }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--accent2)', minWidth: 50 }}>{item.time}</span>
                <span style={{ fontSize: 14, color: 'var(--text)' }}>{item.activity}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Kanban column ──────────────────────────────────────────────────────── */
function KanbanView({ tasks, onRefresh }) {
  const statuses = ['backlog', 'in_progress', 'review', 'done'];
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, minWidth: 0 }}>
      {statuses.map(status => {
        const col = tasks.filter(t => t.status === status);
        const meta = STATUS_META[status];
        return (
          <div key={status} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 4px' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: meta.color }} />
              <span style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: meta.color }}>{meta.label}</span>
              <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--muted)', fontFamily: 'var(--font-mono)' }}>{col.length}</span>
            </div>
            {col.map(task => <TaskCard key={task.id} task={task} onRefresh={onRefresh} />)}
          </div>
        );
      })}
    </div>
  );
}

/* ─── Main App ───────────────────────────────────────────────────────────── */
export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem('ss_token'));
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('list');   // list | kanban
  const [showCreate, setShowCreate] = useState(false);
  const [showPlan, setShowPlan] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQ, setSearchQ] = useState('');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [me, taskList] = await Promise.all([api.me(), api.tasks.list()]);
      setUser(me);
      setTasks(taskList);
    } catch (e) {
      if (e.message === 'Unauthorized') setAuthed(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { if (authed) loadData(); }, [authed, loadData]);

  if (!authed) return <LoginPage onLogin={() => setAuthed(true)} />;

  const logout = () => { localStorage.removeItem('ss_token'); setAuthed(false); };

  const filtered = tasks.filter(t => {
    const matchStatus = filterStatus === 'all' || t.status === filterStatus;
    const matchQ = !searchQ || t.title.toLowerCase().includes(searchQ.toLowerCase());
    return matchStatus && matchQ;
  });

  const stats = {
    total: tasks.length,
    done: tasks.filter(t => t.status === 'done').length,
    minutes: tasks.reduce((s, t) => s + t.total_minutes, 0),
  };

  return (
    <>
      <style>{GLOBAL_CSS}</style>

      {/* Header */}
      <header style={{ background: 'var(--surface)', borderBottom: '1px solid var(--border)', padding: '0 24px', height: 56, display: 'flex', alignItems: 'center', gap: 20, position: 'sticky', top: 0, zIndex: 50 }}>
        <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: '-0.02em' }}>
          <span style={{ color: 'var(--accent)' }}>Sprint</span>Sync
        </div>

        {/* Nav */}
        <div style={{ display: 'flex', gap: 4, marginLeft: 16 }}>
          {[['list', 'List'], ['kanban', 'Kanban']].map(([v, l]) => (
            <button key={v} onClick={() => setView(v)} style={{ padding: '4px 12px', borderRadius: 6, border: 'none', background: view === v ? 'var(--accent)22' : 'transparent', color: view === v ? 'var(--accent)' : 'var(--muted)', fontSize: 13, fontWeight: 600, fontFamily: 'inherit', cursor: 'pointer' }}>{l}</button>
          ))}
        </div>

        {/* Quick stats */}
        <div style={{ display: 'flex', gap: 20, marginLeft: 'auto', fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--muted)' }}>
          <span><b style={{ color: 'var(--text)' }}>{stats.done}</b>/{stats.total} done</span>
          <span><b style={{ color: 'var(--text)' }}>{stats.minutes}m</b> logged</span>
        </div>

        <Btn size="sm" variant="secondary" onClick={() => setShowPlan(true)}>◈ Daily Plan</Btn>
        <Btn size="sm" onClick={() => setShowCreate(true)}>+ Task</Btn>

        <div style={{ width: 1, height: 24, background: 'var(--border)' }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700 }}>
            {user?.username?.[0]?.toUpperCase()}
          </div>
          <span style={{ fontSize: 13, color: 'var(--muted)' }}>{user?.username}</span>
          {user?.is_admin && <span style={{ fontSize: 10, background: 'var(--accent)22', color: 'var(--accent)', padding: '2px 6px', borderRadius: 4, fontFamily: 'var(--font-mono)', fontWeight: 700 }}>ADMIN</span>}
          <Btn variant="ghost" size="sm" onClick={logout}>Out</Btn>
        </div>
      </header>

      {/* Main */}
      <main style={{ padding: '24px', maxWidth: view === 'kanban' ? '100%' : 800, margin: '0 auto' }}>
        {/* Filters */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            placeholder="Search tasks…"
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
            style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', padding: '8px 14px', fontSize: 14, outline: 'none', width: 200 }}
          />
          <div style={{ display: 'flex', gap: 4 }}>
            {['all', 'backlog', 'in_progress', 'review', 'done'].map(s => (
              <button key={s} onClick={() => setFilterStatus(s)}
                style={{ padding: '6px 12px', borderRadius: 6, border: 'none', background: filterStatus === s ? 'var(--accent)' : 'var(--surface)', color: filterStatus === s ? '#fff' : 'var(--muted)', fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', textTransform: 'capitalize' }}>
                {s === 'all' ? 'All' : STATUS_META[s]?.label}
              </button>
            ))}
          </div>
          {loading && <span style={{ color: 'var(--muted)', fontSize: 13, fontFamily: 'var(--font-mono)', animation: 'pulse 1s infinite' }}>refreshing…</span>}
        </div>

        {/* Content */}
        {view === 'kanban' ? (
          <KanbanView tasks={filtered} onRefresh={loadData} />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--muted)', fontSize: 14 }}>
                {tasks.length === 0 ? 'No tasks yet. Create one to get started!' : 'No tasks match your filters.'}
              </div>
            )}
            {filtered.map(task => <TaskCard key={task.id} task={task} onRefresh={loadData} />)}
          </div>
        )}
      </main>

      {showCreate && <CreateTaskModal onClose={() => setShowCreate(false)} onCreated={loadData} />}
      {showPlan && <DailyPlanPanel onClose={() => setShowPlan(false)} />}
    </>
  );
}
