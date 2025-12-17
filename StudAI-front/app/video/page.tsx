'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileUpload } from '@/components/aceternity/FileUpload';
import { GradientButton } from '@/components/aceternity/GradientButton';
import { Confetti } from '@/components/aceternity/Confetti';
import {
  Sparkles,
  Send,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import generateVideo from '@/lib/api';
import type { Input } from '@/models/input';
import { LoaderFive } from '@/components/ui/loader';

export default function VideoPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [additionalInput, setAdditionalInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [stage, setStage] = useState<'idle'>('idle');
  const [showConfetti, setShowConfetti] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [loaderIndex, setLoaderIndex] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const loaderMessages = [
    'Uploading file',
    'Reading your PDF',
    'Generating the best script possible',
    'Making it Funny AF',
    'Cooking the perfect TTS',
    'Stitching your video magic',
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
    if (files.length > 0) {
      setFile(files[0]);
    }
  };

  const handleGenerate = async () => {
    if (!file) return;
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
    } catch (error) {
      console.error('Failed to generate video:', error);
      setIsGenerating(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setAdditionalInput('');
    setIsGenerating(false);
    setShowConfetti(false);
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {showConfetti && <Confetti />}
      {isGenerating && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-5 w-full px-4">
            <div className="flex flex-col items-center gap-2">
              <LoaderFive text={`${loaderMessages[loaderIndex]} — ${elapsedSeconds}s`} />
              <p className="text-white/70 text-sm">
                {elapsedSeconds < 30 
                  ? `Processing your video... ${elapsedSeconds}s` 
                  : elapsedSeconds < 60
                  ? `Still working... ${Math.floor(elapsedSeconds / 60)}m ${elapsedSeconds % 60}s`
                  : `This may take a few minutes... ${Math.floor(elapsedSeconds / 60)}m ${elapsedSeconds % 60}s`}
              </p>
              {elapsedSeconds > 20 && (
                <p className="text-white/50 text-xs mt-1">
                  Video processing can take 1-3 minutes. Please wait...
                </p>
              )}
            </div>
          </div>
        </div>
      )}
      {/* solid black background as requested; gradients removed */}

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            transition={{ duration: 2, repeat: Infinity, repeatType: 'reverse' }}
            className="inline-flex items-center gap-2 mb-4"
          >
            <Sparkles className="w-8 h-8 text-pink-400" />
          </motion.div>
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4 tracking-tight">
            StudAI — Generate
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-transparent bg-clip-text">
              {' '}
              Short-Form
            </span>{' '}
            Video
          </h1>
          <p className="text-white/70 text-base md:text-lg max-w-2xl mx-auto">
            Upload a PDF and let AI craft a viral-ready script, TTS, and video.
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
            <FileUpload onChange={handleFileChange} />

            <div className="space-y-4">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleGenerate();
                }}
              >
                <div className="flex items-end gap-2 bg-white/5 border border-purple-900/40 rounded-[2rem] p-4 focus-within:ring-2 ring-purple-700/40 transition">
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
                    placeholder="Describe tone, style, or keywords…"
                    className="w-full bg-transparent text-white placeholder-white/40 focus:outline-none resize-none leading-6"
                  />
                  <button
                    type="submit"
                    disabled={!file || isGenerating}
                    className="shrink-0 inline-flex items-center justify-center h-11 w-11 rounded-2xl bg-gradient-to-r from-purple-700 to-pink-700 text-white hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Send"
                    title="Send"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>

            <div className="flex justify-center">
              <GradientButton
                onClick={handleGenerate}
                disabled={!file}
                className="w-full max-w-md"
              >
                <Sparkles className="w-5 h-5" />
                Generate Video
              </GradientButton>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

