'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FileText, Video, ArrowLeft, Sparkles } from 'lucide-react';
import type { GeneratedVideoResult } from '@/models/video_output';
import { useSearchParams } from 'next/navigation';

export default function VideoOutputPage() {
  const [result, setResult] = useState<GeneratedVideoResult | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const searchParams = useSearchParams();

  useEffect(() => {
    try {
      const urlParam = searchParams.get('result');
      if (urlParam) {
        const decoded = decodeURIComponent(urlParam);
        const parsed = JSON.parse(decoded) as GeneratedVideoResult;
        console.log('📥 Resultado parseado desde URL:', parsed);
        setResult(parsed);
        try {
          sessionStorage.setItem('studaiLastResult', JSON.stringify(parsed));
        } catch {}
        
        // Si hay job_id y no hay video_url, hacer polling
        if (parsed.job_id && !parsed.video_url) {
          setIsPolling(true);
          pollForVideo(parsed.job_id);
        }
        return;
      }
      const stored = sessionStorage.getItem('studaiLastResult');
      if (stored) {
        const parsed = JSON.parse(stored) as GeneratedVideoResult;
        setResult(parsed);
        
        // Si hay job_id y no hay video_url, hacer polling
        if (parsed.job_id && !parsed.video_url) {
          setIsPolling(true);
          pollForVideo(parsed.job_id);
        }
      }
    } catch (e) {
      console.warn('Failed to read result from sessionStorage', e);
    }
  }, [searchParams]);

  const pollForVideo = async (jobId: string) => {
    const ENDPOINT = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    const STATUS_ENDPOINT = `${ENDPOINT}/generate/video/status/${jobId}`;
    
    const poll = async () => {
      try {
        const response = await fetch(STATUS_ENDPOINT);
        const status = await response.json();
        
        console.log("Polling status:", status);
        
        if (status.status === "completed" && status.result) {
          // Actualizar resultado con video_url
          const updatedResult = {
            ...result!,
            ...status.result,
            video_url: status.result.video_url
          };
          setResult(updatedResult);
          setIsPolling(false);
          try {
            sessionStorage.setItem('studaiLastResult', JSON.stringify(updatedResult));
          } catch (e) {
            console.warn('Failed to update sessionStorage', e);
          }
        } else if (status.status === "error") {
          console.error("Error generando video:", status.error);
          setIsPolling(false);
        } else {
          // Seguir haciendo polling cada 2 segundos
          setTimeout(poll, 2000);
        }
      } catch (err) {
        console.error("Error en polling:", err);
        setIsPolling(false);
      }
    };
    
    poll();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-slate-900 to-black relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(120,119,198,0.08),rgba(255,255,255,0))]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(149,76,233,0.07),rgba(255,255,255,0))]" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-10 md:py-16">
        <div className="mb-8 flex items-center justify-between">
          <Link
            href="/video"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Generate
          </Link>
          <div className="inline-flex items-center gap-2 text-white/80">
            <Sparkles className="w-5 h-5 text-pink-400" />
            <span className="font-semibold">StudAI</span>
          </div>
        </div>

        {!result ? (
          <div className="text-center text-white/80">
            <p>No result found. Please generate a video first.</p>
            <div className="mt-6">
              <Link
                href="/video"
                className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-gradient-to-r from-purple-700 to-pink-700 text-white font-semibold hover:opacity-90 transition"
              >
                Go to Generator
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            <motion.h1
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-3xl md:text-4xl font-bold text-white"
            >
              StudAI — Your Generated Output
            </motion.h1>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="bg-black/40 backdrop-blur-md border border-white/10 rounded-3xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-semibold text-white">Generated Script</h2>
              </div>
              <p className="text-white/80 leading-relaxed">{result.script}</p>
              {result.pdf_blob_url && result.pdf_name && (
                <div className="mt-4">
                  <a
                    href={result.pdf_blob_url}
                    download={result.pdf_name}
                    className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
                  >
                    Download Source PDF
                  </a>
                </div>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.15 }}
              className="bg-black/40 backdrop-blur-md border border-white/10 rounded-3xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Video className="w-6 h-6 text-pink-400" />
                <h3 className="text-lg font-semibold text-white">Final Video</h3>
              </div>
              {result.video_url ? (
                <div className="flex justify-center">
                  <video
                    controls
                    src={result.video_url}
                    className="max-w-full max-h-[600px] rounded-2xl border border-white/10"
                    style={{ width: 'auto', height: 'auto' }}
                  />
                </div>
              ) : isPolling ? (
                <div className="w-full h-64 flex items-center justify-center rounded-2xl border border-white/10 bg-black/20">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
                    <p className="text-white/80">Generando video...</p>
                    <p className="text-white/50 text-sm mt-2">Esto puede tardar unos minutos</p>
                  </div>
                </div>
              ) : (
                <div className="w-full h-64 flex items-center justify-center rounded-2xl border border-white/10 bg-black/20">
                  <p className="text-white/60">Video no disponible</p>
                </div>
              )}
            </motion.div>

            <div className="pt-4">
              <Link
                href="/video"
                className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
              >
                Create Another
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

