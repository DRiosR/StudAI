'use client';

import React from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import type { LinkPreview } from '@/lib/fetchPreview';
import { fetchPreview } from '@/lib/fetchPreview';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { StatefulButton } from '@/components/ui/stateful-button';

type FetchMode = 'secure' | 'vulnerable';

export default function PreviewDemo({ mode = 'both' as 'secure' | 'vulnerable' | 'both' }) {
  const [url, setUrl] = React.useState('');
  const [loading, setLoading] = React.useState<FetchMode | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<string | null>(null);
  const [preview, setPreview] = React.useState<LinkPreview | null>(null);
  const [selectedTestUrl, setSelectedTestUrl] = React.useState<string>('');
  const [selectedOkUrl, setSelectedOkUrl] = React.useState<string>('');
  const [lastMode, setLastMode] = React.useState<FetchMode | null>(null);

  const allowVulnerable = process.env.NEXT_PUBLIC_ALLOW_VULNERABLE === 'true';
  const showSecureButton = mode !== 'vulnerable';
  const showVulnerableButton = mode !== 'secure' && allowVulnerable;

  const handleFetch = async (mode: FetchMode, providedUrl?: string) => {
    const effectiveUrl = providedUrl ?? url;
    if (!effectiveUrl) {
      setError('Please enter a URL first.');
      return;
    }
    setLastMode(mode);
    setLoading(mode);
    setError(null);
    setSuccess(null);
    setPreview(null);
    try {
      const minDelayMs = process.env.NODE_ENV !== 'production' ? 2000 : 0;
      const [data] = await Promise.all([
        fetchPreview(effectiveUrl, mode),
        new Promise((resolve) => setTimeout(resolve, minDelayMs)),
      ]);
      setPreview(data);
      setSuccess(mode === 'secure' ? 'Secure preview fetched.' : 'Vulnerable preview fetched (dev).');
    } catch (e: any) {
      setError(e?.message || 'Failed to fetch preview.');
    } finally {
      setLoading(null);
    }
  };

  const hasPreview = Boolean(preview && (preview.title || preview.description || preview.image));
  const buttonStateFor = (btnMode: FetchMode): 'idle' | 'loading' | 'success' | 'error' => {
    if (loading === btnMode) return 'loading';
    if (lastMode === btnMode && error) return 'error';
    if (lastMode === btnMode && success) return 'success';
    return 'idle';
  };

  const vulnerableTests: Array<{ label: string; url: string; note?: string }> = [
    { label: 'Direct secret', url: 'http://127.0.0.1:8080/secret', note: 'Secure should block; Vulnerable returns JSON.' },
    { label: 'Redirector to secret', url: 'http://127.0.0.1:8085/go', note: 'Secure blocks; Vulnerable follows redirect.' },
    { label: 'Config', url: 'http://127.0.0.1:9001/config' },
    { label: 'Meta', url: 'http://127.0.0.1:8082/meta' },
    { label: 'Action', url: 'http://127.0.0.1:8083/action' },
  ];
  const okTests: Array<{ label: string; url: string; note?: string }> = [
    { label: 'Grassy Codes', url: 'https://grassy.codes' },
    { label: 'Grassy Codes - /...', url: 'https://www.grassy.codes/projects/vervi' },
    { label: 'Vervi', url: 'https://vervi.app' },
    { label: 'Facebook', url: 'https://www.facebook.com/' },
    { label: 'FIAD', url: 'http://fiad.ens.uabc.mx/' },
  ];

  return (
    <main className="relative min-h-screen w-full flex items-start sm:items-center justify-center px-4 py-8 bg-black text-white overflow-hidden">
      {/* Background layers */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute inset-0 bg-gradient-to-b from-[#0b0b14] via-[#0b0b14]/95 to-black" />
        <div className="absolute left-1/2 top-1/2 h-[140vmax] w-[140vmax] -translate-x-1/2 -translate-y-1/2 rounded-full blur-3xl opacity-60 bg-[conic-gradient(from_0deg,rgba(99,102,241,0.08),rgba(236,72,153,0.08),rgba(56,189,248,0.08),rgba(99,102,241,0.08))] animate-[spin_60s_linear_infinite]" />
      </div>

      <div className="relative z-10 w-full max-w-2xl space-y-6">
        <header className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight text-white">Link Preview Demo</h1>
          <p className="text-sm text-white/70">
            Enter a URL to fetch a compact preview card. Uses secure server-side fetching. A vulnerable fetch is available for development only.
          </p>
        </header>

        <section aria-labelledby="url-input" className="space-y-3">
          <div className="space-y-2">
            <label htmlFor="preview-url" id="url-input" className="text-sm font-medium text-white">
              URL
            </label>
            <Input
              id="preview-url"
              type="url"
              inputMode="url"
              placeholder="https://example.com/article"
              autoComplete="off"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'url-error' : undefined}
              className="bg-white/5 border-white/10 text-white placeholder:text-white/40"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            {showSecureButton && (
              <StatefulButton
                variant="secure"
                state={buttonStateFor('secure')}
                onClick={() => handleFetch('secure')}
                disabled={!url || loading !== null}
                className="h-11"
                labelIdle="Secure Fetch"
                labelLoading="Fetching…"
                labelSuccess="Fetched"
                labelError="Retry Secure"
              />
            )}

            {showVulnerableButton && (
              <StatefulButton
                variant="vulnerable"
                state={buttonStateFor('vulnerable')}
                onClick={() => handleFetch('vulnerable')}
                disabled={!url || loading !== null}
                className="h-11"
                labelIdle="Vulnerable Fetch (dev only)"
                labelLoading="Fetching…"
                labelSuccess="Fetched"
                labelError="Retry Vulnerable"
              />
            )}
          </div>
        </section>

        {allowVulnerable && (
          <section className="space-y-3">
            <h2 className="text-sm font-medium">Quick tests (vulnerable)</h2>
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                <label htmlFor="vuln-tests" className="sr-only">
                  Choose a vulnerable test URL
                </label>
                <Select
                  value={selectedTestUrl}
                  onValueChange={(val) => {
                    setSelectedTestUrl(val);
                  }}
                >
                  <SelectTrigger id="vuln-tests" className="bg-white/5 border-white/10 text-white">
                    <SelectValue placeholder="Select a test URL" />
                  </SelectTrigger>
                  <SelectContent className="bg-black text-white border-white/10">
                    {vulnerableTests.map((tc) => (
                      <SelectItem key={tc.url} value={tc.url}>
                        {tc.label} — {tc.url}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedTestUrl && (
                  <p className="mt-2 text-xs text-white/50">
                    {vulnerableTests.find((t) => t.url === selectedTestUrl)?.note ||
                      'This should demonstrate the secure vs vulnerable behavior.'}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  className="h-11 bg-white/10 hover:bg-white/15 text-white border-white/10 rounded-xl"
                  disabled={!selectedTestUrl}
                  onClick={() => {
                    if (selectedTestUrl) {
                      setUrl(selectedTestUrl);
                    }
                  }}
                >
                  Fill
                </Button>
                <StatefulButton
                  variant="vulnerable"
                  state={buttonStateFor('vulnerable')}
                  className="h-11"
                  disabled={!selectedTestUrl || loading !== null}
                  onClick={() => {
                    if (selectedTestUrl) {
                      setUrl(selectedTestUrl);
                      void handleFetch(mode === 'vulnerable' ? 'vulnerable' : 'secure', selectedTestUrl);
                    }
                  }}
                  labelIdle="Fill + Run"
                  labelLoading="Running…"
                  labelSuccess="Done"
                  labelError="Retry Run"
                />
              </div>
            </div>
          </section>
        )}

        <section className="space-y-3">
          <h2 className="text-sm font-medium">Quick tests (ok)</h2>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <label htmlFor="ok-tests" className="sr-only">
                Choose an OK test URL
              </label>
              <Select
                value={selectedOkUrl}
                onValueChange={(val) => {
                  setSelectedOkUrl(val);
                }}
              >
                <SelectTrigger id="ok-tests" className="bg-white/5 border-white/10 text-white">
                  <SelectValue placeholder="Select an OK URL" />
                </SelectTrigger>
                <SelectContent className="bg-black text-white border-white/10">
                  {okTests.map((tc) => (
                    <SelectItem key={tc.url} value={tc.url}>
                      {tc.label} — {tc.url}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                className="h-11 bg-white/10 hover:bg-white/15 text-white border-white/10 rounded-xl"
                disabled={!selectedOkUrl}
                onClick={() => {
                  if (selectedOkUrl) {
                    setUrl(selectedOkUrl);
                  }
                }}
              >
                Fill
              </Button>
              <StatefulButton
                variant="secure"
                state={buttonStateFor('secure')}
                className="h-11"
                disabled={!selectedOkUrl || loading !== null}
                onClick={() => {
                  if (selectedOkUrl) {
                    setUrl(selectedOkUrl);
                    void handleFetch('secure', selectedOkUrl);
                  }
                }}
                labelIdle="Fill + Run"
                labelLoading="Running…"
                labelSuccess="Done"
                labelError="Retry Run"
              />
            </div>
          </div>
        </section>

        <section aria-live="polite" className="space-y-3">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                <Alert variant="destructive">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription id="url-error">{error}</AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>
          <AnimatePresence mode="wait">
            {success && !error && (
              <motion.div
                key="success"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                <Alert>
                  <AlertTitle>Success</AlertTitle>
                  <AlertDescription>{success}</AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        <section className="space-y-3">
          <Card className="rounded-xl shadow-sm border-white/10 bg-white/5 text-white">
            <CardHeader>
              <CardTitle className="text-lg">Preview</CardTitle>
              <CardDescription className="text-sm text-white/60">
                A compact card showing title, description and image if available.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-4">
              <AnimatePresence mode="wait" initial={false}>
                {loading && (
                  <motion.div
                    key="skeleton"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex gap-4 items-start"
                    aria-label="Loading preview"
                  >
                    <div className="w-24 h-24 rounded-lg bg-white/10 animate-pulse" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-2/3 rounded bg-white/10 animate-pulse" />
                      <div className="h-3 w-full rounded bg-white/10 animate-pulse" />
                      <div className="h-3 w-5/6 rounded bg-white/10 animate-pulse" />
                      <div className="h-3 w-1/2 rounded bg-white/10 animate-pulse" />
                    </div>
                  </motion.div>
                )}
                {!loading && !hasPreview && (
                  <motion.p
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-sm text-white/60"
                  >
                    No preview yet. Enter a URL and choose an action.
                  </motion.p>
                )}
                {!loading && hasPreview && preview && (
                  <motion.article
                    key={preview.url || preview.title || 'preview'}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.2 }}
                    className="flex gap-4 items-start"
                    aria-label="Link preview card"
                  >
                    {preview.image && (
                      <motion.img
                        src={preview.image}
                        alt={preview.title ? `Preview image for ${preview.title}` : 'Preview image'}
                        className="w-24 h-24 rounded-lg object-cover border"
                        loading="lazy"
                        decoding="async"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.2 }}
                      />
                    )}
                    <div className="min-w-0">
                      {preview.title && (
                        <h2 className="text-base font-medium leading-snug line-clamp-2">
                          {preview.title}
                        </h2>
                      )}
                      {preview.description && (
                        <p className="mt-1 text-sm text-white/70 line-clamp-3">
                          {preview.description}
                        </p>
                      )}
                      {preview.url && (
                        <p className="mt-2 text-xs text-white/60 break-all">
                          {preview.url}
                        </p>
                      )}
                    </div>
                  </motion.article>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}


