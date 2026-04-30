'use client';

export const SESSION_KEY = 'studaiSessionUser';

export type SessionUser = {
  name: string;
  email: string;
};

export const getSessionUser = (): SessionUser | null => {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as SessionUser;
    if (!parsed?.email) return null;
    return parsed;
  } catch {
    return null;
  }
};

export const saveSessionUser = (user: SessionUser) => {
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
};

export const clearSessionUser = () => {
  localStorage.removeItem(SESSION_KEY);
};
