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

// @ts-ignore
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

// send metrics when the page loads
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

// Send metrics after DOM is fully loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', sendPageMetrics);
} else {
  sendPageMetrics();
}

// Optionalally handle SPA navigation
let lastUrl = window.location.href;
const observer = new MutationObserver(() => {
  if (window.location.href !== lastUrl) {
    lastUrl = window.location.href;
    setTimeout(sendPageMetrics, 1000);
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});