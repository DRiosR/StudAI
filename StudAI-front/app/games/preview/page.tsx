'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, Gamepad2 } from 'lucide-react';
import { FlappyBird } from '@/components/games/FlappyBird';
import UnscrambleGame  from '@/components/games/UnscrambleGame';
import WordleGame from '@/components/games/Worlde';

type GameKey = 'flappy' | 'unscramble' | 'wordle';

export default function GamesPreviewPage() {
  const games = useMemo(
    () =>
      [
        {
          key: 'flappy' as const,
          name: 'Flappy Bird',
          description: 'Tap/Click/Space to flap. Pass pipes to score.',
          component: <FlappyBird />,
        },
        {
          key: 'unscramble' as const,
          name: 'Unscramble',
          description: 'Rearrange the letters to find the hidden word.',
          component: <UnscrambleGame />,
        },
        {
          key: 'wordle' as const,
          name: 'Wordle',
          description: 'Guess the hidden 5-letter word in 6 tries.',
          component: <WordleGame />,
        },
      ] as const,
    []
  );

  const [selected, setSelected] = useState<GameKey>('flappy');
  const active = games.find((g) => g.key === selected) ?? games[0];

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      <div className="relative z-10 max-w-6xl mx-auto px-4 py-10 md:py-16">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <Link
            href="/video"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Generate
          </Link>
          <div className="inline-flex items-center gap-2 text-white/80">
            <Gamepad2 className="w-5 h-5 text-pink-400" />
            <span className="font-semibold">Games Preview</span>
          </div>
        </div>

        <motion.h1
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-3xl md:text-4xl font-bold text-white mb-6"
        >
          Mini-Games
        </motion.h1>

        {/* Layout */}
        <div className="grid lg:grid-cols-[280px,1fr] gap-6">
          {/* Sidebar */}
          <motion.aside
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.05 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-3 h-max"
          >
            <div className="px-2 py-2">
              <p className="text-white/70 text-sm mb-2">Games</p>
            </div>
            <div className="space-y-1">
              {games.map((g) => {
                const isActive = g.key === active.key;
                return (
                  <button
                    key={g.key}
                    onClick={() => setSelected(g.key)}
                    className={`w-full text-left px-3 py-2 rounded-xl transition ${
                      isActive
                        ? 'bg-white/10 text-white'
                        : 'text-white/80 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <div className="font-medium">{g.name}</div>
                    <div className="text-xs text-white/60">{g.description}</div>
                  </button>
                );
              })}
            </div>
          </motion.aside>

          {/* Main Game */}
          <motion.main
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="space-y-4"
          >
            <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h2 className="text-white font-semibold">{active.name}</h2>
                  <p className="text-white/60 text-sm">{active.description}</p>
                </div>
              </div>
              <div className="w-full max-w-[880px]">
                {active.component}
              </div>
            </div>
          </motion.main>
        </div>
      </div>
    </div>
  );
}
