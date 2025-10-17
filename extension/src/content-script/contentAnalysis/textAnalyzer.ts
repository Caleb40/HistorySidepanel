export class TextAnalyzer {
  /**
   * Counts words in main content area, excluding navigation/footers
   */
  static countContentWords(): number {
    try {
      const contentSelectors = [
        'main', 'article', '[role="main"]', '.content', '.main-content',
        '.post-content', '.entry-content', '#content', '#main'
      ];

      let contentElement = document.querySelector(contentSelectors.join(', '));

      // Fallback to body but exclude common non-content areas
      if (!contentElement) {
        contentElement = document.body;
      }

      // Clone to avoid modifying the DOM
      const clone = contentElement.cloneNode(true) as HTMLElement;

      // Remove elements that typically don't contain main content
      const excludeSelectors = [
        'nav', 'header', 'footer', 'aside', 'script', 'style',
        '.nav', '.header', '.footer', '.sidebar', '.menu',
        '.advertisement', '.ad', '.banner'
      ];

      excludeSelectors.forEach(selector => {
        clone.querySelectorAll(selector).forEach(el => el.remove());
      });

      const text = clone.innerText || '';
      const cleanedText = this.cleanText(text);

      if (!cleanedText) return 0;

      // Better word splitting that handles multiple languages
      const words = cleanedText.match(/\p{L}+/gu); // Unicode letter matching
      return words ? words.length : 0;

    } catch (error) {
      console.error('Error counting words:', error);
      return this.fallbackWordCount();
    }
  }

  private static cleanText(text: string): string {
    return text
      .replace(/[^\p{L}\s]/gu, ' ') // Keep letters and spaces
      .replace(/\s+/g, ' ')         // Collapse multiple spaces
      .trim();
  }

  private static fallbackWordCount(): number {
    // Simple fallback
    const text = document.body.innerText || '';
    const cleaned = this.cleanText(text);
    return cleaned ? cleaned.split(/\s+/).length : 0;
  }
}