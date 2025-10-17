export class LinkAnalyzer {
  /**
   * Counts meaningful links in the main content
   */
  static countContentLinks(): { total: number; internal: number; external: number } {
    try {
      const allLinks = Array.from(document.querySelectorAll('a[href]'));
      const currentDomain = window.location.hostname;

      const meaningfulLinks = allLinks.filter(link => {
        // Exclude links that are likely not content
        if (this.isNonContentLink(link)) return false;

        const href = link.getAttribute('href') || '';
        return this.isMeaningfulLink(href);
      });

      const internalLinks = meaningfulLinks.filter(link => {
        const href = link.getAttribute('href') || '';
        return this.isInternalLink(href, currentDomain);
      });

      const externalLinks = meaningfulLinks.filter(link => {
        const href = link.getAttribute('href') || '';
        return this.isExternalLink(href, currentDomain);
      });

      return {
        total: meaningfulLinks.length,
        internal: internalLinks.length,
        external: externalLinks.length
      };

    } catch (error) {
      console.error('Error counting links:', error);
      return { total: 0, internal: 0, external: 0 };
    }
  }

  private static isNonContentLink(link: Element): boolean {
    // Check if link is in navigation/footer areas
    const inNav = link.closest('nav, header, footer, .nav, .header, .footer, .menu');
    if (inNav) return true;

    // Check if link is empty or just an icon
    const text = link.textContent?.trim() || '';
    const hasMeaningfulText = text.length > 1 && !/^[#•·→]$/.test(text);
    const hasImage = link.querySelector('img');

    return !hasMeaningfulText && !hasImage;
  }

  private static isMeaningfulLink(href: string): boolean {
    // Exclude anchors, javascript, tel, mailto, etc.
    return !href.match(/^(#|javascript:|tel:|mailto:|data:|about:blank)/i) &&
           href.trim().length > 0;
  }

  private static isInternalLink(href: string, currentDomain: string): boolean {
    try {
      if (href.startsWith('/') || href.startsWith('./') || href.startsWith('../')) {
        return true;
      }

      if (href.startsWith('http')) {
        const url = new URL(href);
        return url.hostname === currentDomain ||
               url.hostname.endsWith('.' + currentDomain);
      }

      return true; // Relative URLs are internal
    } catch {
      return false;
    }
  }

  private static isExternalLink(href: string, currentDomain: string): boolean {
    try {
      if (!href.startsWith('http')) return false;

      const url = new URL(href);
      return url.hostname !== currentDomain &&
             !url.hostname.endsWith('.' + currentDomain);
    } catch {
      return false;
    }
  }
}