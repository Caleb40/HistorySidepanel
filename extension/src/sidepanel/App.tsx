import './styles.css';
import React, {useEffect, useState} from 'react';
import {apiRequest, formatDateTime, GlobalStats, MessagePayload, VisitData} from "@/common";
import {URLNormalizer} from '@/content-script/urlNormalizer';

const App: React.FC = () => {
  const [currentMetrics, setCurrentMetrics] = useState<VisitData | null>(null);
  const [visitHistory, setVisitHistory] = useState<VisitData[]>([]);
  const [globalStats, setGlobalStats] = useState<GlobalStats | null>(null);
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    initializeSidepanel();
    setupMessageListeners();

    return () => {
      // Cleanup listeners
      if (chrome.runtime?.onMessage) {
        chrome.runtime.onMessage.removeListener(handleExternalMessage);
      }
    };
  }, []);

  // Event driven message handling
  const setupMessageListeners = () => {
    if (chrome.runtime?.onMessage) {
      chrome.runtime.onMessage.addListener(handleExternalMessage);
    }
  };

  const handleExternalMessage = (message: MessagePayload, sender: any, sendResponse: any) => {
    console.log('Side panel received message:', message);

    if (message.type === 'PAGE_LOADED' || message.type === 'TAB_SWITCHED' || message.type === 'PAGE_VISIT_RECORDED') {
      // Immediate refresh when page changes or new visit is recorded
      refreshAllData();
      sendResponse({success: true});
    }

    return true;
  };

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

  const refreshAllData = async (): Promise<void> => {
    try {
      const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
      if (tab?.url) {
        setCurrentUrl(tab.url);
        await fetchPageData(tab.url);
      }
    } catch (err) {
      console.error('Error refreshing data:', err);
    }
  };

  const fetchPageData = async (url: string): Promise<void> => {
    try {
      setLoading(true);
      setError('');

      const [metrics, history, stats] = await Promise.allSettled([
        apiRequest(`http://localhost:8000/api/v1/visits/latest?url=${encodeURIComponent(url)}`),
        apiRequest(`http://localhost:8000/api/v1/visits?url=${encodeURIComponent(url)}`).then(h => h || []),
        apiRequest('http://localhost:8000/api/v1/visits/stats')
      ]);

      // Handle metrics result
      if (metrics.status === 'fulfilled') {
        setCurrentMetrics(metrics.value);
      } else {
        console.warn('Failed to fetch metrics:', metrics.reason);
        setCurrentMetrics(null);
      }

      // Handle history result
      if (history.status === 'fulfilled') {
        setVisitHistory(history.value || []);
      } else {
        console.warn('Failed to fetch history:', history.reason);
        setVisitHistory([]);
      }

      // Handle stats result
      if (stats.status === 'fulfilled') {
        setGlobalStats(stats.value);
      } else {
        console.warn('Failed to fetch stats:', stats.reason);
        setGlobalStats(null);
      }

      // Only show error if all requests failed (likely backend down)
      if (metrics.status === 'rejected' && history.status === 'rejected' && stats.status === 'rejected') {
        const firstError = metrics.reason;
        if (firstError.message.includes('Failed to fetch') || firstError.message.includes('NetworkError')) {
          setError('Backend server not available. Make sure the backend is running on localhost:8000');
        } else {
          setError('Failed to connect to analytics service');
        }
      }

    } catch (err) {
      console.error('Unexpected error in fetchPageData:', err);
      setError('An unexpected error occurred');
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
            Current Site: <b>{URLNormalizer.getDisplayUrl(currentUrl)}</b>
          </div>

          {currentMetrics ? (
            <div className="metrics-grid">
              <div className="metric-row">
                <div className="metric-label">Links</div>
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
          ) : (
            <div className="no-data-message">
              <p>📊 No data collected for this page yet</p>
              <p className="subtext">Reload the page to start tracking analytics</p>
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
            {visitHistory.length > 0 ? (
              visitHistory.map((visit) => (
                <div key={visit.id} className="history-item">
                  <div className="history-date">{formatDateTime(visit.created_at)}</div>
                  <div className="history-stats">
                    <span>------ {visit.link_count} link(s), </span>
                    <span>{visit.image_count} images, </span>
                    <span>{visit.word_count} words ------</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-history-message">
                <p>No previous visits recorded for this site</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;