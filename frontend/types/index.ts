// Global type definitions for the X Scraper Dashboard

export interface Tweet {
  tweet_id?: string;
  username: string;
  text: string;
  created_at: string;
  url?: string;
  retweet_count?: number;
  favorite_count?: number;
  reply_count?: number;
}

export interface Toast {
  message: string;
  type: 'success' | 'error';
}

export interface SearchParams {
  auth_id: string;
  password: string;
  screen_name?: string;
  query?: string;
  count: number;
  mode: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  success: boolean;
}

export type SortDirection = 'asc' | 'desc';
export type SortField = keyof Tweet;

export interface FilterOptions {
  usernameFilter: string;
  keywordFilter: string;
}

export interface ExportData {
  post_date: string;
  username: string;
  text: string;
  url: string;
  retweet_count: number;
  favorite_count: number;
  reply_count: number;
}
