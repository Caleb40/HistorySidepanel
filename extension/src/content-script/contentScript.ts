/**
 * Content script for extracting page metrics
 * Runs in the context of the web page
 */

import {PageMetrics, UrlUtils} from '@/common';
import {ImageAnalyzer, LinkAnalyzer, TextAnalyzer} from "@/content-script";


class PageMetricsExtractor {
  public static extractMetrics(): PageMetrics {
    const wordCount =
      TextAnalyzer.countContentWords();
    const linkAnalysis = LinkAnalyzer.countContentLinks();
    const imageAnalysis = ImageAnalyzer.countContentImages();

    return {
      url: window.location.href,
      link_count: linkAnalysis.total,
      internal_links: linkAnalysis.internal,
      external_links: linkAnalysis.external,
      image_count: imageAnalysis.total,
      content_images: imageAnalysis.content,
      decorative_images: imageAnalysis.decorative,
      word_count: wordCount,
      datetime_visited: new Date().toISOString()
    };
  }
}

class NavigationHandler {
  private static lastUrl: string = window.location.href;

  private static navigationTimer: number | undefined;

  static handleNavigation(newUrl: string): void {
    clearTimeout(this.navigationTimer);
    this.navigationTimer = window.setTimeout(() => {
      if (UrlUtils.shouldRecordNewVisit(this.lastUrl, newUrl)) {
        this.lastUrl = newUrl;
        console.log('Recording new visit for:', UrlUtils.getDisplayUrl(newUrl));
        sendPageMetrics();
      }
    }, 300);
  }


  static setInitialUrl(url: string): void {
    this.lastUrl = url;
  }
}

// Send metrics when the page loads
function sendPageMetrics(): void {
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
      console.log('Page metrics sent successfully');
    });
  } catch (error) {
    console.error('Error extracting page metrics:', error);
  }
}


function addSidePanelButton(): void {
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

// Add message listener to content script
function setupContentScriptListeners(): void {
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('Content script received message:', message);

    if (message.type === 'TAB_UPDATED') {
      console.log('Content script: Tab updated to', message.url);
      NavigationHandler.handleNavigation(message.url);
      sendResponse({success: true});
    }

    return true;
  });
}

function initializeContentScript(): void {
  console.log('Initializing content script for:', UrlUtils.getDisplayUrl(window.location.href));

  // Set initial URL and record first visit
  NavigationHandler.setInitialUrl(window.location.href);
  sendPageMetrics();

  // Add the side panel button
  addSidePanelButton();

  // Setup listeners for updates
  setupContentScriptListeners();
}

// Handle navigation changes (SPA support)
function handleNavigationChange(): void {
  NavigationHandler.handleNavigation(window.location.href);
}

// Run when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeContentScript);
} else {
  initializeContentScript();
}

// Handle SPA navigation via DOM mutations
let lastUrl = window.location.href;
const observer = new MutationObserver(() => {
  if (window.location.href !== lastUrl) {
    lastUrl = window.location.href;
    console.log('URL changed via DOM mutation');
    handleNavigationChange();
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Handle SPA navigation via History API
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