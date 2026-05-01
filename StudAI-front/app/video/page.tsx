'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileUpload } from '@/components/aceternity/FileUpload';
import { Confetti } from '@/components/aceternity/Confetti';
import {
  ArrowLeft,
  Sparkles,
  Send,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import generateVideo from '@/lib/api';
import type { Input } from '@/models/input';
import { LoaderFive } from '@/components/ui/loader';

export default function VideoPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [additionalInput, setAdditionalInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [stage, setStage] = useState<'idle' | 'polling'>('idle');
  const [showConfetti, setShowConfetti] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [loaderIndex, setLoaderIndex] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const loaderMessages = [
    'Subiendo archivo',
    'Leyendo tu PDF',
    'Generando el mejor guion posible',
    'Preparando la narracion',
    'Renderizando audio y video',
    'Aplicando detalles finales',
  ];

  useEffect(() => {
    if (typeof window !== 'undefined') {
      audioRef.current = new Audio('/success.mp3');
    }
  }, []);

  useEffect(() => {
    if (!isGenerating) {
      setElapsedSeconds(0);
      setLoaderIndex(0);
      return;
    }
    const tick = setInterval(() => setElapsedSeconds((s) => s + 1), 1000);
    const rotate = setInterval(
      () => setLoaderIndex((i) => (i + 1) % loaderMessages.length),
      1500
    );
    return () => {
      clearInterval(tick);
      clearInterval(rotate);
    };
  }, [isGenerating]);

  const handleFileChange = (files: File[]) => {
    setFile(files.length > 0 ? files[0] : null);
    setErrorMessage('');
  };

  const handleGenerate = async () => {
    if (!file) {
      setErrorMessage('Primero debes subir un archivo PDF.');
      return;
    }
    if (!additionalInput.trim()) {
      alert('Por favor, escribe un poco de contexto o de qué trata tu video en el cuadro de texto antes de generar.');
      setErrorMessage('Debes ingresar una descripción o contexto en el texto.');
      return;
    }
    setErrorMessage('');
    setIsGenerating(true);
    const payload: Input = {
      files: [file],
      user_additional_input: additionalInput,
    };

    try {
      const apiResult = await generateVideo(payload);
      
      // Debug: Verificar que el audio_url está presente
      console.log('📦 API Result recibido:', apiResult);
      console.log('🎵 Audio URL:', apiResult.audio_url);
      console.log('🎬 Video URL:', apiResult.video_url);
      console.log('🆔 Job ID:', apiResult.job_id);

      // Si hay un job_id, significa que el video se está generando en background
      if (apiResult.job_id && !apiResult.video_url) {
        // Hacer polling hasta que el video esté listo
        console.log('⏳ Video generándose en background, iniciando polling...');
        setStage('polling');
        
        try {
          const { pollVideoStatus } = await import('@/lib/api');
          const finalResult = await pollVideoStatus(apiResult.job_id);
          
          console.log('✅ Video generado:', finalResult);
          
          // Combinar resultados
          const completeResult = {
            ...apiResult,
            ...finalResult,
            video_url: finalResult.video_url
          };
          
          setShowConfetti(true);
          if (audioRef.current) {
            audioRef.current.play().catch((err) => console.log('Audio error:', err));
          }
          try {
            sessionStorage.setItem('studaiLastResult', JSON.stringify(completeResult));
          } catch (e) {
            console.warn('Failed to store result in sessionStorage', e);
          }
          const encoded = encodeURIComponent(JSON.stringify(completeResult));
          router.push(`/video/output?result=${encoded}`);
          setTimeout(() => setShowConfetti(false), 3000);
        } catch (pollError) {
          console.error('Error en polling:', pollError);
          // Aún así, redirigir con los resultados parciales
          setShowConfetti(true);
          try {
            sessionStorage.setItem('studaiLastResult', JSON.stringify(apiResult));
          } catch (e) {
            console.warn('Failed to store result in sessionStorage', e);
          }
          const encoded = encodeURIComponent(JSON.stringify(apiResult));
          router.push(`/video/output?result=${encoded}`);
          setTimeout(() => setShowConfetti(false), 3000);
        }
      } else {
        // Video ya está listo (compatibilidad con versión anterior)
        setShowConfetti(true);
        if (audioRef.current) {
          audioRef.current.play().catch((err) => console.log('Audio error:', err));
        }
        try {
          sessionStorage.setItem('studaiLastResult', JSON.stringify(apiResult));
        } catch (e) {
          console.warn('Failed to store result in sessionStorage', e);
        }
        const encoded = encodeURIComponent(JSON.stringify(apiResult));
        router.push(`/video/output?result=${encoded}`);
        setTimeout(() => setShowConfetti(false), 3000);
      }
    } catch (error) {
      console.error('Failed to generate video:', error);
      const message =
        error instanceof Error
          ? error.message
          : 'No se pudo generar el video. Revisa que el backend este corriendo.';
      setErrorMessage(message);
      setIsGenerating(false);
      setStage('idle');
    }
  };

  const resetForm = () => {
    setFile(null);
    setAdditionalInput('');
    setIsGenerating(false);
    setShowConfetti(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {showConfetti && <Confetti />}
      {isGenerating && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-5 w-full px-4">
            <div className="w-full max-w-md rounded-3xl border border-white/15 bg-slate-900/80 p-6 backdrop-blur-md shadow-2xl">
              <LoaderFive text={`${loaderMessages[loaderIndex]} — ${elapsedSeconds}s`} />
              <p className="text-white/80 text-sm text-center mt-3">
                {elapsedSeconds < 30 
                  ? `Procesando tu video... ${elapsedSeconds}s` 
                  : elapsedSeconds < 60
                  ? `Seguimos trabajando... ${Math.floor(elapsedSeconds / 60)}m ${elapsedSeconds % 60}s`
                  : `Esto puede tardar unos minutos... ${Math.floor(elapsedSeconds / 60)}m ${elapsedSeconds % 60}s`}
              </p>
              <div className="mt-4 h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <motion.div
                  className="h-full w-1/3 bg-gradient-to-r from-cyan-400 to-emerald-400"
                  animate={{ x: ['-120%', '320%'] }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
                />
              </div>
              {elapsedSeconds > 20 && (
                <p className="text-white/60 text-xs mt-3 text-center">
                  El procesamiento puede tomar entre 2 a 5 minutos. Espera un momento.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_20%_18%,rgba(59,130,246,0.15),transparent_40%)]" />
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_82%_72%,rgba(16,185,129,0.13),transparent_45%)]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12 w-full max-w-4xl"
        >
          <div className="mb-6 flex justify-start">
            <div className="flex items-center gap-3">
              <Link
                href="/home"
                className="inline-flex items-center gap-2 text-sm text-white/75 hover:text-white transition"
              >
                <ArrowLeft className="w-4 h-4" />
                Volver al inicio
              </Link>
              <Link
                href="/video/library"
                className="inline-flex items-center gap-2 text-sm text-white/75 hover:text-white transition"
              >
                Mis videos
              </Link>
            </div>
          </div>
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ duration: 2, repeat: Infinity, repeatType: 'reverse' }}
            className="inline-flex items-center gap-2 rounded-full px-4 py-2 mb-4 bg-white/5 border border-white/10"
          >
            <Sparkles className="w-4 h-4 text-cyan-300" />
            <span className="text-white/90 text-sm">Generador IA</span>
          </motion.div>
          <h1 className="text-4xl md:text-6xl font-black text-white mb-4 tracking-tight">
            Crea tu video con
            <span className="bg-gradient-to-r from-cyan-300 via-sky-400 to-emerald-400 text-transparent bg-clip-text">
              {' '}
              StudAI
            </span>{' '}
            en minutos
          </h1>
          <p className="text-white/70 text-base md:text-lg max-w-2xl mx-auto">
            Sube un PDF, personaliza el enfoque y genera guion, narracion y video con una calidad visual profesional.
          </p>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div
            key="upload-form"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            className="w-full max-w-2xl space-y-8"
          >
            <div className="rounded-3xl border border-white/10 bg-slate-900/65 p-5 backdrop-blur-sm">
              <FileUpload onChange={handleFileChange} />
            </div>

            <div className="space-y-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleGenerate();
                }}
              >
                <div className="flex items-end gap-2 bg-slate-900/70 border border-white/15 rounded-[2rem] p-4 focus-within:ring-2 ring-cyan-500/40 transition backdrop-blur-sm">
                  <textarea
                    value={additionalInput}
                    onChange={(e) => setAdditionalInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleGenerate();
                      }
                    }}
                    rows={1}
                    placeholder="Describe tono, estilo o palabras clave..."
                    className="w-full bg-transparent text-white placeholder-slate-400 focus:outline-none resize-none leading-6"
                  />
                  <button
                    type="submit"
                    disabled={!file || isGenerating}
                    className="shrink-0 inline-flex items-center justify-center h-11 w-11 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Enviar"
                    title="Enviar"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>

            <div className="flex justify-center">
              <button
                onClick={handleGenerate}
                disabled={!file || isGenerating}
                className="w-full max-w-md inline-flex items-center justify-center gap-2 rounded-2xl px-6 py-3 font-bold text-slate-950 bg-gradient-to-r from-cyan-500 to-emerald-500 shadow-lg shadow-cyan-900/40 hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="w-5 h-5" />
                {isGenerating ? 'Generando...' : 'Generar video'}
              </button>
            </div>
            {errorMessage && (
              <p className="text-sm text-amber-300 text-center -mt-2">{errorMessage}</p>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

