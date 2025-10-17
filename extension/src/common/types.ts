export interface PageMetrics {
  url: string;
  link_count: number;
  internal_links?: number;      // NEW
  external_links?: number;      // NEW
  image_count: number;
  content_images?: number;      // NEW
  decorative_images?: number;   // NEW
  word_count: number;
  datetime_visited: string;
}

export interface VisitData {
  id: number;
  created_at: string;
  url: string;
  link_count: number;
  internal_links?: number;
  external_links?: number;
  word_count: number;
  image_count: number;
  content_images?: number;
  decorative_images?: number;
}

export interface GlobalStats {
  total_visits: number;
  unique_urls: number;
  average_links: number;
  average_words: number;
  average_images: number;
  average_internal_links?: number;
  average_external_links?: number;
  average_content_images?: number;
}

export interface MessagePayload {
  type: 'PAGE_VISIT' | 'OPEN_SIDE_PANEL' | 'PAGE_LOADED' | 'TAB_SWITCHED' | 'PAGE_VISIT_RECORDED' | 'TAB_UPDATED';
  data?: any;
  url?: string;
  tabId?: number;
  timestamp?: number;
}