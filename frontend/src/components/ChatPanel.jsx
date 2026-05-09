import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Zap, Database, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { chatApi } from '../api';

function ToolTrace({ trace }) {
  const [open, setOpen] = useState(false);
  if (!trace || trace.length === 0) return null;
  return (
    <div className="tool-trace">
      <button
        className="tool-trace-header"
        onClick={() => setOpen(!open)}
        style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 0 }}
      >
        <Zap size={10} />
        {trace.length} tool{trace.length !== 1 ? 's' : ''} used
        {open ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
      </button>
      {open && trace.map((item, i) => (
        <div key={i} className="tool-trace-item">
          <Database size={10} style={{ color: 'var(--blue)', flexShrink: 0 }} />
          <span className="tool-name">{item.tool}</span>
          <span className="tool-result">{item.result_preview}</span>
        </div>
      ))}
    </div>
  );
}

function SourceChips({ sources }) {
  if (!sources || sources.length === 0) return null;
  const getClass = (s) => {
    if (s.includes('query') || s.includes('get_')) return 'sql';
    if (s.includes('document') || s.includes('search_doc')) return 'doc';
    return 'tool';
  };
  const getLabel = (s) => {
    if (s === 'query_structured_data') return '📊 SQL Database';
    if (s === 'search_documents') return '📄 Documents';
    if (s === 'get_top_titles') return '🏆 Top Titles';
    if (s === 'get_trending_analysis') return '🔥 Trending';
    if (s === 'compare_titles') return '⚖️ Comparison';
    if (s === 'get_regional_engagement') return '🗺️ Regional';
    if (s === 'get_genre_performance') return '🎬 Genre';
    return s;
  };
  return (
    <div className="sources-row">
      {sources.map((s, i) => (
        <span key={i} className={`source-chip ${getClass(s)}`}>{getLabel(s)}</span>
      ))}
    </div>
  );
}

function Message({ msg }) {
  if (msg.role === 'user') {
    return (
      <div className="message user">
        <div className="message-avatar"><User size={14} /></div>
        <div className="message-body">
          <div className="message-content">{msg.content}</div>
        </div>
      </div>
    );
  }
  return (
    <div className="message assistant">
      <div className="message-avatar"><Bot size={14} /></div>
      <div className="message-body">
        <div className="message-content">{msg.content}</div>
        {msg.tool_trace && <ToolTrace trace={msg.tool_trace} />}
        {msg.sources_used && <SourceChips sources={msg.sources_used} />}
      </div>
    </div>
  );
}

const WELCOME = `👋 Welcome to **StreamVault AI Insights**!

I'm your AI-powered analytics assistant with access to:
• 📊 **SQL Database** — movies, viewers, watch activity, reviews, marketing & regional data
• 📄 **Internal Documents** — quarterly reports, campaign summaries, audience behavior analysis

Ask me anything about StreamVault's content performance. Try one of the suggestions below, or type your own question.`;

export default function ChatPanel({ onNewMessage }) {
  const [messages, setMessages] = useState([
    { id: 0, role: 'assistant', content: WELCOME, tool_trace: [], sources_used: [] }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    chatApi.getSuggestedQuestions()
      .then(r => setSuggestions(r.data.questions.slice(0, 6)))
      .catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const buildHistory = () => messages
    .filter(m => m.id > 0)
    .map(m => ({ role: m.role, content: m.content }));

  const sendMessage = async (text) => {
    const userMsg = text || input.trim();
    if (!userMsg || loading) return;
    setInput('');

    const userEntry = { id: Date.now(), role: 'user', content: userMsg };
    setMessages(prev => [...prev, userEntry]);
    setLoading(true);

    try {
      const history = buildHistory();
      const res = await chatApi.sendMessage(userMsg, history);
      const { answer, tool_trace, sources_used } = res.data;
      const assistantEntry = {
        id: Date.now() + 1,
        role: 'assistant',
        content: answer,
        tool_trace,
        sources_used,
      };
      setMessages(prev => [...prev, assistantEntry]);
      if (onNewMessage) onNewMessage(assistantEntry);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: `⚠️ Error: ${err.message}. Please check the backend is running and your API key is configured.`,
        tool_trace: [],
        sources_used: [],
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map(msg => <Message key={msg.id} msg={msg} />)}

        {messages.length === 1 && suggestions.length > 0 && (
          <div style={{ padding: '0 4px' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Try asking...
            </div>
            <div className="suggestions-grid">
              {suggestions.map((q, i) => (
                <button key={i} className="suggestion-chip" onClick={() => sendMessage(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="message assistant">
            <div className="message-avatar"><Bot size={14} /></div>
            <div className="message-body">
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                Querying data sources...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-row">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="Ask about content performance, trends, audience insights..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
          >
            <Send size={16} />
          </button>
        </div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 6, textAlign: 'center' }}>
          Press Enter to send · Shift+Enter for new line · StreamVault Internal Analytics
        </div>
      </div>
    </div>
  );
}
