import { useState, useEffect } from 'react';
import { Search, FileText, BookOpen } from 'lucide-react';
import { documentsApi } from '../api';

export default function DocumentsPanel() {
  const [docs, setDocs] = useState([]);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    documentsApi.listDocuments().then(r => setDocs(r.data.documents)).catch(() => {});
  }, []);

  const doSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setSearched(true);
    try {
      const r = await documentsApi.searchDocuments(query, 6);
      setResults(r.data.results);
    } catch (e) {
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>Internal Documents</div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{docs.length} PDF documents indexed</div>
      </div>

      <div style={{ padding: 16, borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '9px 12px', color: 'var(--text-primary)', fontSize: 13, outline: 'none' }}
            placeholder="Search document content..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && doSearch()}
          />
          <button
            onClick={doSearch}
            disabled={searching || !query.trim()}
            style={{ background: 'var(--accent)', border: 'none', borderRadius: 8, padding: '0 16px', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, opacity: searching ? 0.6 : 1 }}
          >
            <Search size={14} />
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
        {!searched ? (
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 10 }}>Available Documents</div>
            {docs.map((doc, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '12px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, marginBottom: 8 }}>
                <FileText size={20} style={{ color: 'var(--accent)', flexShrink: 0, marginTop: 1 }} />
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{doc.name}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>{doc.filename} · {doc.chunks} chunks indexed</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 10 }}>
              {results.length} result{results.length !== 1 ? 's' : ''} for "{query}"
            </div>
            {results.length === 0 && !searching && (
              <div style={{ color: 'var(--text-secondary)', fontSize: 13, textAlign: 'center', marginTop: 40 }}>No results found</div>
            )}
            {results.map((r, i) => (
              <div key={i} style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: 14, marginBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <BookOpen size={14} style={{ color: 'var(--purple)' }} />
                  <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--purple)' }}>{r.source}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-muted)' }}>score: {r.relevance_score}</span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{r.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
