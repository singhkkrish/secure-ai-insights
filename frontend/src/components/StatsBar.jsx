import { useState, useEffect } from 'react';
import { analyticsApi } from '../api';

export default function StatsBar() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    analyticsApi.getOverviewStats().then(r => setStats(r.data)).catch(() => {});
  }, []);

  const items = stats ? [
    { label: 'Total Titles', value: stats.total_titles, sub: 'in catalog' },
    { label: 'Active Viewers', value: stats.active_viewers?.toLocaleString(), sub: 'subscribers' },
    { label: 'Total Views', value: stats.total_views?.toLocaleString(), sub: 'in database' },
    { label: 'Avg Rating', value: stats.avg_content_rating, sub: 'content score' },
    { label: 'Top Genre', value: stats.top_genre, sub: 'most viewed' },
  ] : Array(5).fill({ label: '...', value: '—', sub: '' });

  return (
    <div className="stats-grid">
      {items.map((item, i) => (
        <div key={i} className="stat-card">
          <div className="stat-label">{item.label}</div>
          <div className="stat-value">{item.value ?? '—'}</div>
          <div className="stat-sub">{item.sub}</div>
        </div>
      ))}
    </div>
  );
}
