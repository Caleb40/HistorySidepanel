import React, {useEffect, useState} from 'react';
import './styles.css';
import {formatDateTime} from "@/common";

interface VisitData {
  id: number;
  datetime_visited: string;
  url: string;
  link_count: number;
  word_count: number;
  image_count: number;
}

const App: React.FC = () => {
  const [currentMetrics, setCurrentMetrics] = useState<VisitData | null>(null);
  const [visitHistory, setVisitHistory] = useState<VisitData[]>([]);
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    initializeSidepanel();
  }, []);

  const initializeSidepanel = async (): Promise<void> => {
    try {
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

      if (!tab?.url) {
        throw new Error('Could not get current tab URL');
      }

      setCurrentUrl(tab.url);
      await fetchPageData(tab.url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize sidepanel');
      setLoading(false);
    }
  };

  const fetchPageData = async (url: string): Promise<void> => {
    try {
      setLoading(true);
      setError('');

      const [metricsResponse, historyResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/visits/latest?url=${encodeURIComponent(url)}`),
        fetch(`http://localhost:8000/api/v1/visits?url=${encodeURIComponent(url)}`)
      ]);

      if (!metricsResponse.ok || !historyResponse.ok) {
        throw new Error('Failed to fetch page data from server');
      }

      const [metrics, history] = await Promise.all([
        metricsResponse.json(),
        historyResponse.json()
      ]);

      setCurrentMetrics(metrics);
      setVisitHistory(history);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch page data');
      console.error('Error fetching page data:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRefresh = (): void => {
    if (currentUrl) {
      fetchPageData(currentUrl);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading page analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-state">
        <h2>⚠️ Error</h2>
        <p>{error}</p>
        <button onClick={handleRefresh} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📊 Page Analytics</h1>
        <button onClick={handleRefresh} className="refresh-button" title="Refresh data">
          🔄
        </button>
      </header>

      <main className="app-content">
        <section className="current-page-section">
          <h2>Current Page</h2>
          <div className="url-display" title={currentUrl}>
            {currentUrl}
          </div>

          {currentMetrics ? (
            <div className="metrics-grid">
              <MetricCard
                label="Links"
                value={currentMetrics.link_count}
                icon="🔗"
              />
              <MetricCard
                label="Images"
                value={currentMetrics.image_count}
                icon="🖼️"
              />
              <MetricCard
                label="Words"
                value={currentMetrics.word_count}
                icon="📝"
              />
              <MetricCard
                label="Last Visit"
                value={formatDateTime(currentMetrics.datetime_visited)}
                icon="🕒"
                isDate
              />
            </div>
          ) : (
            <div className="no-data">No metrics available for this page</div>
          )}
        </section>

        <section className="history-section">
          <h2>Visit History</h2>
          {visitHistory.length > 0 ? (
            <div className="history-list">
              {visitHistory.map((visit) => (
                <HistoryItem key={visit.id} visit={visit}/>
              ))}
            </div>
          ) : (
            <div className="no-data">No visit history found</div>
          )}
        </section>
      </main>
    </div>
  );
};

// Sub-components for better organization
interface MetricCardProps {
  label: string;
  value: string | number;
  icon: string;
  isDate?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({label, value, icon, isDate = false}) => (
  <div className="metric-card">
    <div className="metric-icon">{icon}</div>
    <div className="metric-content">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${isDate ? 'metric-value-date' : ''}`}>
        {value}
      </div>
    </div>
  </div>
);

interface HistoryItemProps {
  visit: VisitData;
}

const HistoryItem: React.FC<HistoryItemProps> = ({visit}) => (
  <div className="history-item">
    <div className="history-date">{formatDateTime(visit.datetime_visited)}</div>
    <div className="history-metrics">
      <span>🔗 {visit.link_count}</span>
      <span>🖼️ {visit.image_count}</span>
      <span>📝 {visit.word_count}</span>
    </div>
  </div>
);

export default App;