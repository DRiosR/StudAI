'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { BackgroundRippleEffect } from '@/components/ui/background-ripple-effect';
import { ArrowRight, BrainCircuit, FileText, Sparkles, Video } from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      title: 'Guion inteligente',
      desc: 'Analiza tu PDF y construye un guion claro, breve y con enfoque educativo.',
      icon: FileText,
    },
    {
      title: 'Narracion natural',
      desc: 'Convierte el guion en audio con una voz fluida para mayor retencion.',
      icon: BrainCircuit,
    },
    {
      title: 'Video listo para compartir',
      desc: 'Genera una pieza final optimizada para presentar, estudiar o publicar.',
      icon: Video,
    },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
      <BackgroundRippleEffect rows={8} cols={27} cellSize={52} />

      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_20%_18%,rgba(59,130,246,0.18),transparent_38%)]" />
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_82%_72%,rgba(16,185,129,0.16),transparent_40%)]" />
      <div className="absolute inset-x-0 top-0 h-80 bg-gradient-to-b from-white/5 to-transparent pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-14 md:py-20">
        <header className="flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full px-4 py-2 bg-white/5 border border-white/10 text-white/85 backdrop-blur-sm"
          >
            <Sparkles className="w-4 h-4 text-cyan-300" />
            <span className="font-medium">StudAI</span>
          </motion.div>
          <Link
            href="/video"
            className="hidden sm:inline-flex items-center gap-2 text-sm text-white/80 hover:text-white transition"
          >
            Probar ahora <ArrowRight className="w-4 h-4" />
          </Link>
        </header>

        <div className="text-center mt-16 md:mt-24">

          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.08 }}
            className="mt-6 text-4xl md:text-6xl lg:text-7xl font-black tracking-tight text-white leading-tight"
          >
            Convierte conocimiento en{' '}
            <span className="bg-gradient-to-r from-cyan-300 via-sky-400 to-emerald-400 text-transparent bg-clip-text">
              videos con IA
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mt-6 text-white/70 text-lg md:text-xl max-w-3xl mx-auto"
          >
            Sube un PDF y StudAI se encarga del resto: extrae ideas clave, crea un guion,
            genera narracion y produce un video claro, moderno y listo para presentar o compartir.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href="/video"
              className="inline-flex items-center justify-center gap-2 px-7 py-3 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-bold shadow-lg shadow-cyan-900/40 hover:opacity-90 transition"
            >
              Crear mi primer video
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#proceso"
              className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition backdrop-blur-sm"
            >
              Ver como funciona
            </a>
          </motion.div>
        </div>

        <section
          className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-4xl mx-auto"
        >
          {[
            { metric: '3 pasos', label: 'de PDF a video' },
            { metric: '< 5 min', label: 'flujo orientativo' },
            { metric: '100%', label: 'enfocado a estudio' },
          ].map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-white/20 bg-slate-900/70 p-5 text-center backdrop-blur-sm"
            >
              <p className="text-xl font-bold text-white drop-shadow-sm">{item.metric}</p>
              <p className="text-sm text-slate-200 mt-1">{item.label}</p>
            </div>
          ))}
        </section>

        <section
          id="features"
          className="mt-14 grid sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.5, delay: 0.1 * i }}
              className="rounded-3xl p-6 bg-white/5 border border-white/10 backdrop-blur-sm"
            >
              <f.icon className="w-6 h-6 text-cyan-300 mb-4" />
              <h3 className="text-white text-xl font-semibold">{f.title}</h3>
              <p className="text-white/70 mt-2">{f.desc}</p>
            </motion.div>
          ))}
        </section>

        <section
          id="proceso"
          className="mt-14 rounded-3xl border border-white/10 bg-gradient-to-r from-slate-900/60 to-slate-800/50 p-7 md:p-10 backdrop-blur-sm"
        >
          <h2 className="text-2xl md:text-3xl font-bold text-white">Proceso simple, resultado profesional</h2>
          <div className="grid md:grid-cols-3 gap-5 mt-7">
            {[
              'Sube tu documento PDF y define el enfoque que necesitas.',
              'La IA resume, organiza y convierte el contenido en un guion narrable.',
              'Recibe audio y video final con formato limpio y listo para usar.',
            ].map((step, idx) => (
              <div key={step} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-xs text-cyan-300 font-semibold">PASO {idx + 1}</p>
                <p className="text-white/80 mt-2">{step}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

