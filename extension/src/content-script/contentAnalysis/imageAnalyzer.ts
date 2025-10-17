export class ImageAnalyzer {
  /**
   * Counts meaningful content images
   */
  static countContentImages(): { total: number; content: number; decorative: number } {
    try {
      const allImages = Array.from(document.querySelectorAll('img[src]'));

      const contentImages = allImages.filter(img => this.isContentImage(img));
      const decorativeImages = allImages.filter(img => !this.isContentImage(img));

      return {
        total: allImages.length,
        content: contentImages.length,
        decorative: decorativeImages.length
      };

    } catch (error) {
      console.error('Error counting images:', error);
      return { total: 0, content: 0, decorative: 0 };
    }
  }

  private static isContentImage(img: HTMLImageElement): boolean {
    // Exclude very small images (likely icons)
    if (img.naturalWidth < 50 || img.naturalHeight < 50) {
      return false;
    }

    // Exclude images in navigation/headers
    const inNonContentArea = img.closest('nav, header, .nav, .header, .menu, .icon');
    if (inNonContentArea) return false;

    // Check if image is visible and has reasonable dimensions
    const rect = img.getBoundingClientRect();
    const isVisible = rect.width > 0 && rect.height > 0 &&
                     img.style.display !== 'none' &&
                     img.style.visibility !== 'hidden';

    // Check if image is likely a content image (not decorative)
    const hasAltText = img.alt && img.alt.length > 10; // Meaningful alt text
    const src = img.src.toLowerCase();
    const isLikelyContent = hasAltText ||
                           src.includes('/media/') ||
                           src.includes('/images/') ||
                           src.includes('upload') ||
                           rect.width > 200; // Large images are more likely content

    return isVisible && isLikelyContent;
  }
}