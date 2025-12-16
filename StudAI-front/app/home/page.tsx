'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { BackgroundRippleEffect } from '@/components/ui/background-ripple-effect';
import { Sparkles } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-black">
      <BackgroundRippleEffect rows={8} cols={27} cellSize={52} />

      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_30%_20%,rgba(149,76,233,0.08),transparent_40%)]" />
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_80%_70%,rgba(236,72,153,0.07),transparent_40%)]" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-24 md:py-32">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 rounded-full px-4 py-2 bg-white/5 border border-white/10 text-white/80"
          >
            <Sparkles className="w-4 h-4 text-pink-400" />
            <span>StudAI</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="mt-6 text-5xl md:text-7xl font-extrabold tracking-tight text-white"
          >
            Turn PDFs into{' '}
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-transparent bg-clip-text">
              viral clips
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mt-5 text-white/70 text-lg md:text-xl max-w-2xl mx-auto"
          >
            Upload your PDF, generate a punchy script, TTS voice, and a ready-to-share video — in minutes.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-10 flex items-center justify-center gap-4"
          >
            <Link
              href="/video"
              className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-gradient-to-r from-purple-700 to-pink-700 text-white font-semibold shadow-sm hover:opacity-90 transition"
            >
              Start Creating
            </Link>
            <a
              href="#features"
              className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
            >
              Learn More
            </a>
          </motion.div>
        </div>

        <section
          id="features"
          className="mt-24 grid sm:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {[
            { title: 'Smart Script', desc: 'AI turns your docs into punchy shorts.' },
            { title: 'Natural TTS', desc: 'Lifelike voiceover in seconds.' },
            { title: 'Auto Video', desc: 'Output primed for socials.' },
          ].map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.5, delay: 0.1 * i }}
              className="rounded-3xl p-6 bg-white/5 border border-white/10"
            >
              <h3 className="text-white text-xl font-semibold">{f.title}</h3>
              <p className="text-white/70 mt-2">{f.desc}</p>
            </motion.div>
          ))}
        </section>
      </div>
    </div>
  );
}

