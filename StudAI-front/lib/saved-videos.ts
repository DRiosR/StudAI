'use client';

import type { GeneratedVideoResult } from '@/models/video_output';

export type SavedVideoItem = {
  id: string;
  createdAt: string;
  title: string;
  data: GeneratedVideoResult;
};

export const SAVED_VIDEOS_KEY = 'studaiSavedVideos';
export const MAX_SAVED_VIDEOS = 5;

export const readSavedVideos = (): SavedVideoItem[] => {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(SAVED_VIDEOS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SavedVideoItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

export const writeSavedVideos = (items: SavedVideoItem[]) => {
  localStorage.setItem(SAVED_VIDEOS_KEY, JSON.stringify(items));
};
