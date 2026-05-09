import { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis
} from 'recharts';
import { analyticsApi } from '../api';

const COLORS = ['#e94560', '#58a6ff', '#3fb950', '#bc8cff', '#f0883e', '#d29922', '#79c0ff', '#56d364'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 6 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: <strong>{typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</strong></p>
      ))}
    </div>
  );
};

function ChartCard({ title, subtitle, children, fullWidth }) {
  return (
    <div className="chart-card" style={fullWidth ? { gridColumn: '1 / -1' } : {}}>
      <div className="chart-title">{title}</div>
      <div className="chart-subtitle">{subtitle}</div>
      {children}
    </div>
  );
}

function LoadingChart() {
  return (
    <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 12 }}>
      Loading data...
    </div>
  );
}

// Genre views over time
function GenreTrendsChart({ data }) {
  if (!data?.length) return <LoadingChart />;
  const genres = [...new Set(data.map(d => d.genre))];
  const months = [...new Set(data.map(d => d.month))].sort();
  const pivoted = months.map(month => {
    const row = { month: month.slice(5) };
    genres.forEach(g => {
      const found = data.find(d => d.month === month && d.genre === g);
      row[g] = found ? Math.round(found.total_views / 1000) : 0;
    });
    return row;
  });
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={pivoted} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="month" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
        <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} unit="k" />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {genres.slice(0, 6).map((g, i) => (
          <Line key={g} type="monotone" dataKey={g} stroke={COLORS[i]} strokeWidth={2} dot={false} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

// Top titles bar chart
function TopTitlesChart({ data }) {
  if (!data?.length) return <LoadingChart />;
  const top8 = data.slice(0, 8).map(d => ({ ...d, title: d.title.length > 15 ? d.title.slice(0, 14) + '…' : d.title }));
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={top8} margin={{ top: 5, right: 10, bottom: 30, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="title" tick={{ fill: 'var(--text-secondary)', fontSize: 9 }} angle={-30} textAnchor="end" />
        <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="total_views" name="Total Views" fill="var(--accent)" radius={[4, 4, 0, 0]}>
          {top8.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// Audience segments pie chart
function AudiencePieChart({ data }) {
  if (!data?.length) return <LoadingChart />;
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} dataKey="viewer_count" nameKey="segment" cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={3}>
          {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}

// Regional bar chart
function RegionalChart({ data }) {
  if (!data?.length) return <LoadingChart />;
  const top8 = data.slice(0, 8);
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={top8} layout="vertical" margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis type="number" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
        <YAxis dataKey="city" type="category" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="total_views" name="Views" fill="var(--blue)" radius={[0, 4, 4, 0]}>
          {top8.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// Completion rate by segment radar
function CompletionRadar({ data }) {
  if (!data?.length) return <LoadingChart />;
  return (
    <ResponsiveContainer width="100%" height={200}>
      <RadarChart data={data}>
        <PolarGrid stroke="var(--border)" />
        <PolarAngleAxis dataKey="segment" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
        <Radar name="Completion %" dataKey="avg_completion_pct" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.25} />
        <Tooltip content={<CustomTooltip />} />
      </RadarChart>
    </ResponsiveContainer>
  );
}

// Genre avg rating bar
function GenreRatingChart({ data }) {
  if (!data?.length) return <LoadingChart />;
  const genres = [...new Set(data.map(d => d.genre))];
  const genreAvg = genres.map(g => {
    const rows = data.filter(d => d.genre === g);
    return { genre: g, avg_rating: +(rows.reduce((s, r) => s + r.avg_rating, 0) / rows.length).toFixed(1), avg_completion: +(rows.reduce((s, r) => s + r.avg_completion_pct, 0) / rows.length).toFixed(1) };
  });
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={genreAvg} margin={{ top: 5, right: 10, bottom: 20, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey="genre" tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} angle={-20} textAnchor="end" />
        <YAxis domain={[0, 10]} tick={{ fill: 'var(--text-secondary)', fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Bar dataKey="avg_rating" name="Avg Rating" fill="var(--purple)" radius={[4, 4, 0, 0]} />
        <Bar dataKey="avg_completion" name="Completion %" fill="var(--green)" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function ChartsPanel() {
  const [topTitles, setTopTitles] = useState([]);
  const [genreTrends, setGenreTrends] = useState([]);
  const [segments, setSegments] = useState([]);
  const [regional, setRegional] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsApi.getTopTitles({ limit: 10 }).then(r => setTopTitles(r.data.data)),
      analyticsApi.getGenreTrends().then(r => setGenreTrends(r.data.data)),
      analyticsApi.getAudienceSegments().then(r => setSegments(r.data.data)),
      analyticsApi.getRegionalHeatmap().then(r => setRegional(r.data.data)),
    ]).finally(() => setLoading(false));
  }, []);

  return (
    <div className="charts-page">
      <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
        <span style={{ fontSize: 14, fontWeight: 600 }}>Visual Analytics</span>
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Auto-generated from live data</span>
        {loading && <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>Loading...</span>}
      </div>
      <div className="charts-grid">
        <ChartCard title="🏆 Top Titles by Views" subtitle="All-time views per title">
          <TopTitlesChart data={topTitles} />
        </ChartCard>

        <ChartCard title="👥 Audience Segments" subtitle="Viewer count by engagement segment">
          <AudiencePieChart data={segments} />
        </ChartCard>

        <ChartCard title="📈 Genre Views Over Time" subtitle="Monthly view trends by genre (thousands)" fullWidth>
          <GenreTrendsChart data={genreTrends} />
        </ChartCard>

        <ChartCard title="🗺️ Regional Engagement" subtitle="Total views by city">
          <RegionalChart data={regional} />
        </ChartCard>

        <ChartCard title="⭐ Genre Quality Scores" subtitle="Average rating & completion % by genre">
          <GenreRatingChart data={genreTrends} />
        </ChartCard>

        <ChartCard title="🎯 Completion by Segment" subtitle="Viewer engagement depth per segment">
          <CompletionRadar data={segments} />
        </ChartCard>
      </div>
    </div>
  );
}
