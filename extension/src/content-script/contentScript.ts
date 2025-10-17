/**
 * Content script for extracting page metrics
 * Runs in the context of the web page
 */

interface PageMetrics {
  url: string;
  link_count: number;
  image_count: number;
  word_count: number;
  datetime_visited: string;
}

class PageMetricsExtractor {
  private static cleanText(text: string): string {
    return text
      .replace(/[^\w\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  private static countWords(): number {
    const bodyText = document.body.innerText || '';
    const cleanedText = this.cleanText(bodyText);
    return cleanedText ? cleanedText.split(' ').length : 0;
  }

  private static countLinks(): number {
    return document.querySelectorAll('a').length;
  }

  private static countImages(): number {
    return document.querySelectorAll('img').length;
  }

  public static extractMetrics(): PageMetrics {
    return {
      url: window.location.href,
      link_count: this.countLinks(),
      image_count: this.countImages(),
      word_count: this.countWords(),
      datetime_visited: new Date().toISOString()
    };
  }
}

function addSidePanelButton() {
  // Remove existing button if it exists
  const existingButton = document.getElementById('history-sidepanel-button');
  if (existingButton) {
    existingButton.remove();
  }

  const button = document.createElement('button');
  button.id = 'history-sidepanel-button';
  button.innerHTML = '📊 View Page Metrics';
  button.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    padding: 12px 16px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    transition: all 0.2s ease;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  `;

  // Add hover effects
  button.addEventListener('mouseenter', () => {
    button.style.background = '#1d4ed8';
    button.style.transform = 'translateY(-2px)';
    button.style.boxShadow = '0 6px 16px rgba(37, 99, 235, 0.4)';
  });

  button.addEventListener('mouseleave', () => {
    button.style.background = '#2563eb';
    button.style.transform = 'translateY(0)';
    button.style.boxShadow = '0 4px 12px rgba(37, 99, 235, 0.3)';
  });

  // Add click handler to open side panel
  button.addEventListener('click', () => {
    console.log('Side panel button clicked');
    chrome.runtime.sendMessage({
      type: 'OPEN_SIDE_PANEL'
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('Error opening side panel:', chrome.runtime.lastError);
        return;
      }
      console.log('Side panel opened successfully');
    });
  });

  document.body.appendChild(button);
  console.log('Side panel button added to page');
}

// Send metrics when the page loads
const sendPageMetrics = (): void => {
  try {
    const metrics = PageMetricsExtractor.extractMetrics();

    chrome.runtime.sendMessage({
      type: 'PAGE_VISIT',
      data: metrics
    }, (response: any) => {
      if (chrome.runtime.lastError) {
        console.warn('Extension context invalidated:', chrome.runtime.lastError);
        return;
      }
      console.log('Page metrics sent successfully:', metrics);
    });
  } catch (error) {
    console.error('Error extracting page metrics:', error);
  }
};

function initializeContentScript() {
  // Add the side panel button
  addSidePanelButton();

  // Send page metrics
  sendPageMetrics();
}

// Run when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeContentScript);
} else {
  initializeContentScript();
}

// Handle SPA navigation
let lastUrl = window.location.href;
const observer = new MutationObserver(() => {
  if (window.location.href !== lastUrl) {
    lastUrl = window.location.href;
    setTimeout(() => {
      // Re-add button and send metrics for new page
      addSidePanelButton();
      sendPageMetrics();
    }, 1000);
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Also handle history API changes (for SPAs)
let originalPushState = history.pushState;
let originalReplaceState = history.replaceState;

history.pushState = function (...args) {
  originalPushState.apply(this, args);
  handleNavigationChange();
};

history.replaceState = function (...args) {
  originalReplaceState.apply(this, args);
  handleNavigationChange();
};

window.addEventListener('popstate', handleNavigationChange);

function handleNavigationChange() {
  setTimeout(() => {
    addSidePanelButton();
    sendPageMetrics();
  }, 500);
}