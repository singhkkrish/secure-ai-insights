import { useState } from 'react';
import { MessageSquare, BarChart2, FileText, Shield } from 'lucide-react';
import './App.css';
import ChatPanel from './components/ChatPanel';
import ChartsPanel from './components/ChartsPanel';
import DocumentsPanel from './components/DocumentsPanel';
import StatsBar from './components/StatsBar';

const TABS = [
  { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
  { id: 'charts', label: 'Analytics', icon: BarChart2 },
  { id: 'documents', label: 'Documents', icon: FileText },
];

const DATA_SOURCES = [
  { label: 'SQL Database', desc: '6 tables, ~3K rows', color: 'var(--green)' },
  { label: 'PDF Documents', desc: '5 internal reports', color: 'var(--purple)' },
  { label: 'CSV Data Files', desc: 'Movies, viewers, activity', color: 'var(--blue)' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-mark">SV</div>
        <div><div className="header-title">StreamVault AI Insights</div><div className="header-subtitle">Internal Analytics Assistant</div></div>
        <div className="header-spacer" />
        <div className="status-badge"><div className="status-dot" />System Online</div>
      </header>
      <nav className="app-sidebar">
        <div className="sidebar-label">Navigation</div>
        {TABS.map(tab => (
          <button key={tab.id} className={`nav-item ${activeTab === tab.id ? 'active' : ''}`} onClick={() => setActiveTab(tab.id)}>
            <tab.icon size={15} />{tab.label}
          </button>
        ))}
        <div className="nav-divider" />
        <div className="sidebar-label">Data Sources</div>
        {DATA_SOURCES.map((ds, i) => (
          <div key={i} style={{ padding: '7px 14px', display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: ds.color, flexShrink: 0 }} />
            <div><div style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)' }}>{ds.label}</div><div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{ds.desc}</div></div>
          </div>
        ))}
        <div className="nav-divider" />
        <div className="sidebar-label">Security</div>
        <div style={{ padding: '7px 14px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Shield size={13} style={{ color: 'var(--green)' }} />
          <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>Tool-based access<br />SQL injection guard<br />Read-only queries</div>
        </div>
        <div style={{ flex: 1 }} />
        <div style={{ padding: '8px 14px', fontSize: 10, color: 'var(--text-muted)', borderTop: '1px solid var(--border)' }}>
          <div>StreamVault Entertainment</div>
          <div style={{ marginTop: 2, color: 'var(--accent)', fontSize: 9 }}>CONFIDENTIAL — Internal Use Only</div>
        </div>
      </nav>
      <main className="app-main">
        <StatsBar />
        {activeTab === 'chat' && <ChatPanel />}
        {activeTab === 'charts' && <ChartsPanel />}
        {activeTab === 'documents' && <DocumentsPanel />}
      </main>
    </div>
  );
}
