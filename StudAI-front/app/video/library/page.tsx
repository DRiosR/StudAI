'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Trash2 } from 'lucide-react';
import { readSavedVideos, writeSavedVideos, type SavedVideoItem, MAX_SAVED_VIDEOS } from '@/lib/saved-videos';

export default function VideoLibraryPage() {
  const [savedVideos, setSavedVideos] = useState<SavedVideoItem[]>([]);

  useEffect(() => {
    setSavedVideos(readSavedVideos());
  }, []);

  const removeVideo = (id: string) => {
    const updated = savedVideos.filter((item) => item.id !== id);
    setSavedVideos(updated);
    writeSavedVideos(updated);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_20%_18%,rgba(59,130,246,0.15),transparent_40%)]" />
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_82%_72%,rgba(16,185,129,0.13),transparent_45%)]" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <Link href="/video" className="inline-flex items-center gap-2 text-white/75 hover:text-white transition">
            <ArrowLeft className="w-4 h-4" />
            Volver al generador
          </Link>
          <div className="text-sm text-white/70">
            Guardados: {savedVideos.length}/{MAX_SAVED_VIDEOS}
          </div>
        </div>

        <div className="mt-8">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <h1 className="text-3xl font-bold">Mis videos guardados</h1>
          </div>

          {savedVideos.length === 0 ? (
            <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-5 text-white/70">
              No hay videos guardados todavia.
            </div>
          ) : (
            <div className="mt-6 grid gap-3">
              {savedVideos.map((item) => (
                <div
                  key={item.id}
                  className="rounded-2xl border border-white/10 bg-white/5 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
                >
                  <div>
                    <p className="font-semibold">{item.title}</p>
                    <p className="text-xs text-white/60">
                      Guardado: {new Date(item.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.data.video_url && (
                      <a
                        href={item.data.video_url}
                        download
                        className="rounded-xl border border-white/15 px-3 py-2 text-sm hover:bg-white/10 transition"
                      >
                        Descargar video
                      </a>
                    )}
                    <button
                      onClick={() => removeVideo(item.id)}
                      className="inline-flex items-center gap-1 rounded-xl border border-red-400/30 bg-red-500/15 text-red-200 px-3 py-2 text-sm hover:bg-red-500/25 transition"
                    >
                      <Trash2 className="w-4 h-4" />
                      Eliminar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
