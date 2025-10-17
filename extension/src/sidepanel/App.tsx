import './styles.css';
import React, {useEffect, useState} from 'react';
import {formatDateTime} from "@/common";

interface VisitData {
  id: number;
  created_at: string;
  url: string;
  link_count: number;
  word_count: number;
  image_count: number;
}

interface GlobalStats {
  total_visits: number;
  unique_urls: number;
  average_links: number;
  average_words: number;
  average_images: number;
}

const App: React.FC = () => {
  const [currentMetrics, setCurrentMetrics] = useState<VisitData | null>(null);
  const [visitHistory, setVisitHistory] = useState<VisitData[]>([]);
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    initializeSidepanel();
  }, []);

  const initializeSidepanel = async (): Promise<void> => {
    try {
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      if (!tab?.url) throw new Error('Could not get current tab URL');

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

      const [metricsResponse, historyResponse, statsResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/visits/latest?url=${encodeURIComponent(url)}`),
        fetch(`http://localhost:8000/api/v1/visits?url=${encodeURIComponent(url)}`),
        fetch('http://localhost:8000/api/v1/visits/stats')
      ]);

      if (!metricsResponse.ok || !historyResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to fetch page data');
      }

      const [metrics, history, stats] = await Promise.all([
        metricsResponse.json(),
        historyResponse.json(),
        statsResponse.json()
      ]);

      setCurrentMetrics(metrics);
      setVisitHistory(history);
      setGlobalStats(stats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch page data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = (): void => {
    if (currentUrl) fetchPageData(currentUrl);
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-state">
        <p>Error: {error}</p>
        <button onClick={handleRefresh} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>Page Analytics</h1>
          <button onClick={handleRefresh} className="refresh-button" title="Refresh">
            🔄
          </button>
        </div>
      </header>

      <main className="app-content">
        <section className="current-page-section">
          <div className="url-display">
            Current Site's Link: <b>{currentUrl.replace(/^https?:\/\//, '')}</b>
          </div>

          {currentMetrics && (
            <div className="metrics-grid">
              <div className="metric-row">
                <div className="metric-label">Number of Links:</div>
                <div className="metric-value">{currentMetrics.link_count}</div>
              </div>
              <div className="metric-row">
                <div className="metric-label">Images</div>
                <div className="metric-value">{currentMetrics.image_count}</div>
              </div>
              <div className="metric-row">
                <div className="metric-label">Words</div>
                <div className="metric-value">{currentMetrics.word_count}</div>
              </div>
              <div className="metric-row">
                <div className="metric-label">Last visit</div>
                <div className="metric-value date">{formatDateTime(currentMetrics.created_at)}</div>
              </div>
            </div>
          )}
        </section>

        {globalStats && (
          <section className="stats-section">
            <h3>Global Stats</h3>
            <div className="stats-grid">
              <div className="stat-row">
                <div className="stat-label">Total Visits</div>
                <div className="stat-value">{globalStats.total_visits}</div>
              </div>
              <div className="stat-row">
                <div className="stat-label">Unique Sites</div>
                <div className="stat-value">{globalStats.unique_urls}</div>
              </div>
              <div className="stat-row">
                <div className="stat-label">Avg. Links</div>
                <div className="stat-value">{globalStats.average_links}</div>
              </div>
              <div className="stat-row">
                <div className="stat-label">Avg. Words</div>
                <div className="stat-value">{globalStats.average_words}</div>
              </div>
            </div>
          </section>
        )}

        <section className="history-section">
          <h3>Visit History</h3>
          <div className="history-list">
            {visitHistory.map((visit) => (
              <div key={visit.id} className="history-item">
                <div className="history-date">{formatDateTime(visit.created_at)}</div>
                <div className="history-stats">
                  <span>------ {visit.link_count} link(s), </span>
                  <span>{visit.image_count} images, </span>
                  <span>{visit.word_count} words ------</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;