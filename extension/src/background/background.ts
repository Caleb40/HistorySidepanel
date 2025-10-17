/**
 * Background service worker for Chrome extension
 * Handles API communication and side panel management
 */

interface VisitData {
    url: string;
    link_count: number;
    image_count: number;
    word_count: number;
    datetime_visited: string;
}

// TODO: investigate type bug here
// @ts-ignore
class BackgroundService {
    private static readonly API_BASE_URL = 'http://localhost:8000/api/v1';

    private static async makeApiRequest<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.API_BASE_URL}${endpoint}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    public static async recordVisit(visitData: VisitData): Promise<void> {
        try {
            await this.makeApiRequest('/visits', {
                method: 'POST',
                body: JSON.stringify(visitData),
            });
            console.log('Visit recorded successfully:', visitData.url);
        } catch (error) {
            console.error('Failed to record visit:', error);
            // NB: We don't throw here to avoid breaking the extension
            // TODO:
            // In production, we might want to implement retry logic
        }
    }

    public static initializeMessageHandlers(): void {
        chrome.runtime.onMessage.addListener((message: {
            type: string;
            data: VisitData;
        }, sender: any, sendResponse: (arg0: { success: boolean; }) => void) => {
            if (message.type === 'PAGE_VISIT') {
                // we won't wait for the API call to complete
                this.recordVisit(message.data).finally(() => {
                    sendResponse({success: true});
                });

                // Return true to indicate we'll send response asynchronously
                return true;
            }
        });
    }

    public static initializeSidePanel(): void {
        // open side panel when extension icon is clicked
        chrome.action.onClicked.addListener((tab) => {
            if (tab.id) {
                chrome.sidePanel.open({windowId: tab.windowId});
            }
        });

        // Optional: Automatically open side panel on specific sites
        chrome.tabs.onUpdated.addListener((tabId, info, tab) => {
            if (info.status === 'complete' && tab.url) {
                // TODO: We could add logic here to auto-open on specific domains
            }
        });
    }
}

// Initialize the background service when the service worker starts
BackgroundService.initializeMessageHandlers();
BackgroundService.initializeSidePanel();

// Handle extension installation
chrome.runtime.onInstalled.addListener((details: { reason: string; }) => {
    if (details.reason === 'install') {
        console.log('History Sidepanel extension installed');
    }
});

// Keep service worker alive
chrome.runtime.onStartup.addListener(() => {
    console.log('History Sidepanel extension starting up');
});