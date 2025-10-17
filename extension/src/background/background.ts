/**
 * Background service worker for Chrome extension
 * Handles API communication and side panel management
 */

import {API_BASE_URL, apiRequest, MessagePayload, PageMetrics} from '@/common';

class BackgroundService {
  public static async recordVisit(visitData: PageMetrics): Promise<void> {
    try {
      await apiRequest(`${API_BASE_URL}/visits`, {
        method: 'POST',
        body: JSON.stringify(visitData),
      });
      console.log('Visit recorded successfully:', visitData.url);

      // Notify side panels about the new visit
      this.notifySidePanels('PAGE_VISIT_RECORDED', visitData.url);
    } catch (error) {
      console.error('Failed to record visit:', error);
    }
  }

  private static notifySidePanels(type: string, url: string): void {
    // Notify all tabs that might have side panels open
    chrome.tabs.query({}, (tabs) => {
      tabs.forEach(tab => {
        if (tab.id && tab.url?.startsWith('http')) {
          chrome.tabs.sendMessage(tab.id, {
            type: type,
            url: url,
            timestamp: Date.now()
          }).catch(err => {
            // Tab might not have a content script, which is fine
          });
        }
      });
    });

    // Also notify the runtime (for side panels directly)
    chrome.runtime.sendMessage({
      type: type,
      url: url,
      timestamp: Date.now()
    }).catch(err => {
      // No side panel might be listening, which is fine
    });
  }

  public static initializeMessageHandlers(): void {
    chrome.runtime.onMessage.addListener((message: MessagePayload, sender, sendResponse) => {
      console.log('Background received message:', message);

      if (message.type === 'PAGE_VISIT') {
        // Record the visit and then notify side panels
        this.recordVisit(message.data).finally(() => {
          sendResponse({success: true});
        });
        return true; // Keep message channel open
      }

      if (message.type === 'OPEN_SIDE_PANEL') {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
          if (tabs[0]?.id) {
            chrome.sidePanel.open({windowId: tabs[0].windowId})
              .then(() => {
                console.log('Side panel opened via message');
                sendResponse({success: true});
              })
              .catch((error) => {
                console.error('Failed to open side panel:', error);
                sendResponse({success: false, error: error.message});
              });
          }
        });
        return true;
      }

      sendResponse({success: false, error: 'Unknown message type'});
    });
  }

  public static initializeTabMonitoring(): void {
    // Track when user switches between tabs
    chrome.tabs.onActivated.addListener((activeInfo) => {
      chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (tab.url?.startsWith('http')) {
          console.log('Tab switched to:', tab.url);
          this.notifySidePanels('TAB_SWITCHED', tab.url);
        }
      });
    });

    // Track when pages finish loading
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      if (changeInfo.status === 'complete' && tab.url?.startsWith('http')) {
        console.log('Page loaded:', tab.url);
        this.notifySidePanels('PAGE_LOADED', tab.url);

        // Also notify the content script in that tab
        chrome.tabs.sendMessage(tabId, {
          type: 'TAB_UPDATED',
          url: tab.url,
          timestamp: Date.now()
        }).catch(err => {
          // Content script might not be loaded yet
        });
      }
    });
  }

  public static initializeSidePanel(): void {
    console.log('Initializing side panel...');

    const isChrome = navigator.userAgent.includes('Chrome') &&
      !navigator.userAgent.includes('Edg') &&
      !navigator.userAgent.includes('Arc');

    if (!isChrome || !chrome.sidePanel) {
      console.warn('Side panel not supported in this browser');
      return;
    }

    // Set side panel options
    chrome.sidePanel.setOptions({
      enabled: true,
      path: 'sidepanel.html'
    }).then(() => {
      console.log('Side panel options set');
    }).catch((error) => {
      console.error('Failed to set side panel options:', error);
    });

    // Open side panel when extension icon is clicked
    chrome.action.onClicked.addListener((tab) => {
      if (tab.id) {
        chrome.sidePanel.open({windowId: tab.windowId})
          .then(() => console.log('Side panel opened via icon'))
          .catch((error) => console.error('Failed to open side panel:', error));
      }
    });

    console.log('Side panel initialization complete');
  }
}

// Initialize everything when the service worker starts
BackgroundService.initializeMessageHandlers();
BackgroundService.initializeSidePanel();
BackgroundService.initializeTabMonitoring();

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('History Sidepanel extension installed');
  }
});

// Keep service worker alive
chrome.runtime.onStartup.addListener(() => {
  console.log('History Sidepanel extension starting up');
});