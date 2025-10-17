/**
 * Handles URL normalization and determines when to record new visits
 */

export class URLNormalizer {
  /**
   * Normalizes URL by removing query params, hash fragments, and www subdomain
   * Example:
   * https://www.example.com/page?param=value#section → https://example.com/page
   */
  static normalizeUrl(url: string): string {
    try {
      const urlObj = new URL(url);

      // Remove www subdomain, query params, and hash fragments
      const hostname = urlObj.hostname.replace(/^www\./i, '');

      return `${urlObj.protocol}//${hostname}${urlObj.pathname}`.toLowerCase();
    } catch {
      return url;
    }
  }

  /**
   * Determines if a URL change warrants recording a new visit
   * Returns true for different pages, false for same page with different params/fragments
   */
  static shouldRecordNewVisit(oldUrl: string, newUrl: string): boolean {
    const normalizedOld = this.normalizeUrl(oldUrl);
    const normalizedNew = this.normalizeUrl(newUrl);

    // Only record if the normalized URLs are different
    return normalizedOld !== normalizedNew;
  }

  /**
   * Gets the display-friendly version of a URL (for UI)
   */
  static getDisplayUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace(/^www\./i, '') + urlObj.pathname;
    } catch {
      return url.replace(/^https?:\/\//, '');
    }
  }
}