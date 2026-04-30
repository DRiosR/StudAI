'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FileText, Video, ArrowLeft, Sparkles, Trash2, Save } from 'lucide-react';
import type { GeneratedVideoResult } from '@/models/video_output';
import { useSearchParams } from 'next/navigation';
import { MAX_SAVED_VIDEOS, readSavedVideos, type SavedVideoItem, writeSavedVideos } from '@/lib/saved-videos';

export default function VideoOutputPage() {
  const [result, setResult] = useState<GeneratedVideoResult | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [savedVideos, setSavedVideos] = useState<SavedVideoItem[]>([]);
  const [saveMessage, setSaveMessage] = useState('');
  const searchParams = useSearchParams();

  const normalizeAzureSasUrl = (maybeUrl: string | null | undefined) => {
    if (!maybeUrl || typeof maybeUrl !== 'string') return maybeUrl;
    // Azure SAS signatures often contain '+' which MUST be URL-encoded as %2B.
    // If we pass a raw '+' to the browser, Azure may interpret it as space and reject (403).
    try {
      const u = new URL(maybeUrl);
      const query = u.search.replace(/\+/g, '%2B');
      return `${u.origin}${u.pathname}${query}${u.hash}`;
    } catch {
      return maybeUrl.replace(/\+/g, '%2B');
    }
  };

  useEffect(() => {
    setSavedVideos(readSavedVideos());
  }, []);

  useEffect(() => {
    try {
      const urlParam = searchParams.get('result');
      if (urlParam) {
        const decoded = decodeURIComponent(urlParam);
        const parsed = JSON.parse(decoded) as GeneratedVideoResult;
        // Normalizar URLs SAS para evitar 403 por '+' sin escape.
        parsed.audio_url = normalizeAzureSasUrl(parsed.audio_url) as string;
        parsed.video_url = normalizeAzureSasUrl(parsed.video_url) as string | null;
        console.log('📥 Resultado parseado desde URL:', parsed);
        console.log('🎬 Video URL:', parsed.video_url);
        console.log('🆔 Job ID:', parsed.job_id);
        setResult(parsed);
        try {
          sessionStorage.setItem('studaiLastResult', JSON.stringify(parsed));
        } catch {}
        
        // Verificar si el video_url es válido
        const hasValidVideoUrl = parsed.video_url && 
                                 parsed.video_url !== 'null' && 
                                 parsed.video_url !== null &&
                                 parsed.video_url.trim() !== '';
        
        // Si hay job_id y no hay video_url válido, hacer polling
        if (parsed.job_id && !hasValidVideoUrl) {
          console.log('⏳ Iniciando polling para job_id:', parsed.job_id);
          setIsPolling(true);
          pollForVideo(parsed.job_id);
        } else if (hasValidVideoUrl) {
          console.log('✅ Video URL ya disponible:', parsed.video_url);
          setIsPolling(false);
        }
        return;
      }
      const stored = sessionStorage.getItem('studaiLastResult');
      if (stored) {
        const parsed = JSON.parse(stored) as GeneratedVideoResult;
        // Normalizar URLs SAS para evitar 403 por '+' sin escape.
        parsed.audio_url = normalizeAzureSasUrl(parsed.audio_url) as string;
        parsed.video_url = normalizeAzureSasUrl(parsed.video_url) as string | null;
        console.log('📥 Resultado desde sessionStorage:', parsed);
        console.log('🎬 Video URL:', parsed.video_url);
        setResult(parsed);
        
        // Verificar si el video_url es válido
        const hasValidVideoUrl = parsed.video_url && 
                                 parsed.video_url !== 'null' && 
                                 parsed.video_url !== null &&
                                 parsed.video_url.trim() !== '';
        
        // Si hay job_id y no hay video_url válido, hacer polling
        if (parsed.job_id && !hasValidVideoUrl) {
          console.log('⏳ Iniciando polling para job_id:', parsed.job_id);
          setIsPolling(true);
          pollForVideo(parsed.job_id);
        } else if (hasValidVideoUrl) {
          console.log('✅ Video URL ya disponible:', parsed.video_url);
          setIsPolling(false);
        }
      }
    } catch (e) {
      console.warn('Failed to read result from sessionStorage', e);
    }
  }, [searchParams]);

  // Efecto para forzar re-render cuando video_url cambie
  useEffect(() => {
    if (result?.video_url) {
      console.log('🎬 video_url detectado, forzando re-render:', result.video_url);
    }
  }, [result?.video_url]);

  const pollForVideo = async (jobId: string) => {
    const ENDPOINT = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    const STATUS_ENDPOINT = `${ENDPOINT}/generate/video/status/${jobId}`;
    
    let pollCount = 0;
    const MAX_POLLS = 300; // Máximo 10 minutos
    
    const poll = async () => {
      pollCount++;
      try {
        const response = await fetch(STATUS_ENDPOINT);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const status = await response.json();
        
        console.log("📊 Polling status:", status);
        console.log("   Status:", status.status);
        console.log("   Result:", status.result);
        console.log("   Video URL en result:", status.result?.video_url);
        
        if (status.status === "completed" && status.result) {
          const videoUrl = normalizeAzureSasUrl(status.result.video_url);
          console.log("✅ Job completado! Video URL:", videoUrl);
          
          // Verificar que el video_url sea válido
          if (!videoUrl || videoUrl === 'null' || videoUrl === null) {
            console.warn("⚠️  Job completado pero video_url es inválido, continuando polling...");
            setTimeout(poll, 2000);
            return;
          }
          
          // Actualizar resultado con video_url usando el estado actual
          setResult((prevResult) => {
            if (!prevResult) {
              console.warn("⚠️  No hay resultado previo, creando nuevo resultado desde status.result");
              const newResult = {
                ...status.result,
                audio_url: normalizeAzureSasUrl(status.result.audio_url),
                video_url: normalizeAzureSasUrl(status.result.video_url),
              };
              try {
                sessionStorage.setItem('studaiLastResult', JSON.stringify(newResult));
              } catch (e) {
                console.warn('Failed to update sessionStorage', e);
              }
              return newResult;
            }
            const updatedResult = {
              ...prevResult,
              ...status.result,
              audio_url: normalizeAzureSasUrl(status.result.audio_url) || prevResult.audio_url,
              video_url: videoUrl
            };
            console.log("🔄 Actualizando resultado con video_url:", updatedResult.video_url);
            try {
              sessionStorage.setItem('studaiLastResult', JSON.stringify(updatedResult));
              console.log("💾 Resultado guardado en sessionStorage");
            } catch (e) {
              console.warn('Failed to update sessionStorage', e);
            }
            return updatedResult;
          });
          setIsPolling(false);
          console.log("✅ Polling detenido, video debería mostrarse ahora");
        } else if (status.status === "error") {
          console.error("❌ Error generando video:", status.error);
          setIsPolling(false);
        } else {
          // Seguir haciendo polling cada 2 segundos
          if (pollCount >= MAX_POLLS) {
            console.error("❌ Timeout: Máximo número de intentos alcanzado");
            setIsPolling(false);
          } else {
            console.log(`⏳ Job aún procesando (${status.status}), continuando polling... (${pollCount}/${MAX_POLLS})`);
            setTimeout(poll, 2000);
          }
        }
      } catch (err) {
        console.error(`❌ Error en polling #${pollCount}:`, err);
        if (pollCount >= MAX_POLLS) {
          setIsPolling(false);
        } else {
          // Reintentar en caso de error de red
          console.warn(`⚠️  Reintentando polling... (${pollCount}/${MAX_POLLS})`);
          setTimeout(poll, 2000);
        }
      }
    };
    
    poll();
  };

  const persistSavedVideos = (items: SavedVideoItem[]) => {
    setSavedVideos(items);
    writeSavedVideos(items);
  };

  const handleSaveCurrentVideo = () => {
    if (!result) return;
    if (!result.video_url || result.video_url === 'null' || result.video_url.trim() === '') {
      setSaveMessage('No puedes guardar hasta que el video este disponible.');
      return;
    }

    const alreadySaved = savedVideos.some(
      (item) =>
        item.data.video_url === result.video_url ||
        (result.job_id && item.data.job_id === result.job_id)
    );
    if (alreadySaved) {
      setSaveMessage('Este video ya esta guardado.');
      return;
    }

    if (savedVideos.length >= MAX_SAVED_VIDEOS) {
      setSaveMessage('Llegaste al maximo de 5 videos. Elimina uno para guardar otro.');
      return;
    }

    const titleSource = result.topic || result.pdf_name || 'Video sin titulo';
    const newItem: SavedVideoItem = {
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      title: titleSource,
      data: result,
    };

    const updated = [newItem, ...savedVideos];
    persistSavedVideos(updated);
    setSaveMessage('Video guardado correctamente.');
  };

  const handleDeleteSavedVideo = (id: string) => {
    const updated = savedVideos.filter((item) => item.id !== id);
    persistSavedVideos(updated);
    setSaveMessage('Video eliminado del historial.');
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_20%_18%,rgba(59,130,246,0.15),transparent_40%)]" />
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_82%_72%,rgba(16,185,129,0.13),transparent_45%)]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-10 md:py-16">
        <div className="mb-8 flex items-center justify-between">
          <Link
            href="/video"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Volver al generador
          </Link>
          <div className="inline-flex items-center gap-2 text-white/80">
            <Sparkles className="w-5 h-5 text-cyan-300" />
            <span className="font-semibold">StudAI</span>
          </div>
        </div>

        {!result ? (
          <div className="text-center text-white/80">
            <p>No se encontro resultado. Genera un video primero.</p>
            <div className="mt-6">
              <Link
                href="/video"
                className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-semibold hover:opacity-90 transition"
              >
                Ir al generador
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            <motion.h1
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-3xl md:text-4xl font-black tracking-tight text-white"
            >
              Resultado generado con StudAI
            </motion.h1>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="bg-slate-900/65 backdrop-blur-md border border-white/10 rounded-3xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <FileText className="w-6 h-6 text-cyan-300" />
                <h2 className="text-xl font-semibold text-white">Guion generado</h2>
              </div>
              <p className="text-white/80 leading-relaxed">{result.script}</p>
              {result.pdf_blob_url && result.pdf_name && (
                <div className="mt-4">
                  <a
                    href={result.pdf_blob_url}
                    download={result.pdf_name}
                    className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
                  >
                    Descargar PDF fuente
                  </a>
                </div>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.15 }}
              className="bg-slate-900/65 backdrop-blur-md border border-white/10 rounded-3xl p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <Video className="w-6 h-6 text-emerald-300" />
                <h3 className="text-lg font-semibold text-white">Video final</h3>
              </div>
              {(() => {
                const videoUrl = result.video_url;
                const hasValidVideoUrl = videoUrl && 
                                         videoUrl !== 'null' && 
                                         videoUrl !== null &&
                                         typeof videoUrl === 'string' &&
                                         videoUrl.trim() !== '';
                console.log('🎬 Verificando video_url:', videoUrl, 'Tipo:', typeof videoUrl, 'Válido:', hasValidVideoUrl);
                return hasValidVideoUrl;
              })() ? (
                <div className="flex justify-center">
                  <video
                    key={result.video_url} // Forzar re-render cuando cambie la URL
                    controls
                    src={result.video_url || undefined}
                    className="max-w-full max-h-[600px] rounded-2xl border border-white/10"
                    style={{ width: 'auto', height: 'auto' }}
                    onError={(e) => {
                      console.error('❌ Error al cargar video:', e);
                      console.error('URL del video:', result.video_url);
                      const target = e.target as HTMLVideoElement;
                      if (target.error) {
                        console.error('Código de error:', target.error.code);
                        console.error('Mensaje:', target.error.message);
                      }
                    }}
                    onLoadStart={() => {
                      console.log('⏳ Cargando video desde:', result.video_url);
                    }}
                    onLoadedMetadata={() => {
                      console.log('✅ Metadatos del video cargados');
                    }}
                    onCanPlay={() => {
                      console.log('✅ Video listo para reproducir');
                    }}
                  />
                </div>
              ) : isPolling ? (
                <div className="w-full h-64 flex items-center justify-center rounded-2xl border border-white/10 bg-slate-950/40">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-300 mx-auto mb-4"></div>
                    <p className="text-white/80">Generando video...</p>
                    <p className="text-white/50 text-sm mt-2">Esto puede tardar unos minutos</p>
                  </div>
                </div>
              ) : (
                <div className="w-full h-64 flex items-center justify-center rounded-2xl border border-white/10 bg-slate-950/40">
                  <p className="text-white/60">Video no disponible</p>
                </div>
              )}
            </motion.div>

            <div className="pt-4">
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleSaveCurrentVideo}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-semibold hover:opacity-90 transition"
                >
                  <Save className="w-4 h-4" />
                  Guardar video
                </button>
                <Link
                  href="/video"
                  className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
                >
                  Crear otro
                </Link>
                <Link
                  href="/video/library"
                  className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
                >
                  Ver guardados
                </Link>
              </div>
              {saveMessage && <p className="mt-3 text-sm text-white/75">{saveMessage}</p>}
            </div>

            <section className="bg-slate-900/65 backdrop-blur-md border border-white/10 rounded-3xl p-6">
              <div className="flex items-center justify-between gap-4">
                <h3 className="text-lg font-semibold text-white">Videos guardados</h3>
                <span className="text-sm text-white/60">
                  {savedVideos.length}/{MAX_SAVED_VIDEOS}
                </span>
              </div>

              {savedVideos.length === 0 ? (
                <p className="text-white/60 mt-4">
                  Aun no tienes videos guardados. Guarda tu primer resultado.
                </p>
              ) : (
                <div className="mt-4 grid gap-3">
                  {savedVideos.map((item) => (
                    <div
                      key={item.id}
                      className="rounded-2xl border border-white/10 bg-white/5 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
                    >
                      <div>
                        <p className="text-white font-medium">{item.title}</p>
                        <p className="text-xs text-white/60">
                          Guardado: {new Date(item.createdAt).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {item.data.video_url && (
                          <a
                            href={item.data.video_url}
                            target="_blank"
                            rel="noreferrer"
                            className="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm text-white hover:bg-white/10 transition"
                          >
                            Ver
                          </a>
                        )}
                        <button
                          onClick={() => handleDeleteSavedVideo(item.id)}
                          className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-red-500/15 border border-red-400/20 text-red-200 text-sm hover:bg-red-500/25 transition"
                        >
                          <Trash2 className="w-4 h-4" />
                          Eliminar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

