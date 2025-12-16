// lib/fetchPreview.ts
/**
 * Helper for fetching link preview data from your backend.
 *
 * Backend base URL controlled via NEXT_PUBLIC_BACKEND_BASE_URL
 * Toggle vulnerable mode via NEXT_PUBLIC_ALLOW_VULNERABLE (set to "true" for dev only)
 *
 * This helper expects the backend to return either:
 *  - { status_code: number, content: string }   (the FastAPI app's shape)
 *  - OR a LinkPreview object directly: { title?, description?, image?, url? }
 */

export type LinkPreview = {
    title?: string;
    description?: string;
    image?: string;
    url?: string;
  };
  
  const DEFAULT_BACKEND = 'http://127.0.0.1:8000';
  const BASE = (process.env.NEXT_PUBLIC_BACKEND_BASE_URL || DEFAULT_BACKEND).replace(/\/$/, '');
  const ALLOW_VULN = process.env.NEXT_PUBLIC_ALLOW_VULNERABLE === 'true';
  
  async function safeReadText(res: Response, maxChars = 100000): Promise<string | null> {
    try {
      const text = await res.text();
      return text ? text.slice(0, maxChars) : null;
    } catch {
      return null;
    }
  }
  
  /** extract metadata from returned HTML/text using DOMParser (browser) */
  function extractFromHtml(html: string, baseUrl?: string): LinkPreview {
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
  
      const title = (doc.querySelector('title')?.textContent || '').trim() || undefined;
  
      const desc =
        (doc.querySelector('meta[name="description"]')?.getAttribute('content') ||
          doc.querySelector('meta[property="og:description"]')?.getAttribute('content') ||
          doc.querySelector('meta[name="og:description"]')?.getAttribute('content') ||
          '')?.trim() || undefined;
  
      const image =
        (doc.querySelector('meta[property="og:image"]')?.getAttribute('content') ||
          doc.querySelector('meta[name="twitter:image"]')?.getAttribute('content') ||
          '')?.trim() || undefined;
  
      const canonical =
        (doc.querySelector('link[rel="canonical"]')?.getAttribute('href') ||
          doc.querySelector('meta[property="og:url"]')?.getAttribute('content') ||
          baseUrl) || undefined;
  
      return {
        title,
        description: desc,
        image,
        url: canonical,
      };
    } catch {
      return {};
    }
  }
  
  /**
   * fetchPreview
   * - mode: 'secure' | 'vulnerable'
   * - throws on error (including when vulnerable mode is disabled)
   */
  export async function fetchPreview(
    targetUrl: string,
    mode: 'secure' | 'vulnerable' = 'secure'
  ): Promise<LinkPreview> {
    if (!targetUrl || typeof targetUrl !== 'string') {
      throw new Error('Please provide a URL string.');
    }
  
    if (mode === 'vulnerable' && !ALLOW_VULN) {
      throw new Error('Vulnerable mode is disabled in this environment.');
    }
  
    // Map to the FastAPI endpoints you provided
    const endpoint = mode === 'vulnerable' ? '/vulnerable-fetch' : '/secure-fetch';
    const url = `${BASE}${endpoint}`;

    console.log("Fetching preview from:", url);
  
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: targetUrl }),
    });

    console.log("Response:", res);
  
    if (!res.ok) {
      const txt = await safeReadText(res, 1000);
      throw new Error(txt ? `Backend error: ${res.status} ${txt}` : `Request failed with status ${res.status}`);
    }
  
    // Try to parse JSON safely
    let json: unknown;
    try {
      json = await res.json();
    } catch {
      // If backend returned non-json (unlikely), attempt to read text and extract
      const text = (await safeReadText(res)) || '';
      return extractFromHtml(text, targetUrl);
    }
  
    // Backend shapes we expect:
    // 1) { status_code: number, content: string }
    // 2) LinkPreview directly { title?, description?, image?, url? }
    // 3) { data: LinkPreview } wrapped
    if (json && typeof json === 'object') {
      const obj = json as any;
      if ('content' in obj && typeof obj.content === 'string') {
        // Extract metadata from HTML content returned by the backend
        const content = obj.content as string;
        // small safety: limit size before parsing
        const snippet = content.slice(0, 200_000);
        const preview = extractFromHtml(snippet, targetUrl);
  
        // If DOM extraction produced nothing, but backend included a plain text fallback,
        // return that as description
        if (!preview.title && !preview.description && typeof snippet === 'string') {
          return { title: undefined, description: snippet.slice(0, 2000), url: targetUrl };
        }
        return preview;
      }
  
      // If it's already a LinkPreview object
      const maybePreviewKeys = ['title', 'description', 'image', 'url'];
      const hasAny = maybePreviewKeys.some((k) => k in obj);
      if (hasAny) {
        return {
          title: obj.title,
          description: obj.description,
          image: obj.image,
          url: obj.url,
        } as LinkPreview;
      }
  
      // Possibly wrapped
      if ('data' in obj && typeof obj.data === 'object') {
        const d = obj.data as any;
        return {
          title: d.title,
          description: d.description,
          image: d.image,
          url: d.url,
        } as LinkPreview;
      }
    }
  
    // Fallback: try to coerce to string and parse
    const raw = typeof json === 'string' ? (json as string) : '';
    return extractFromHtml(raw, targetUrl);
  }
  