'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Check, X, Loader2 } from 'lucide-react';

type ButtonState = 'idle' | 'loading' | 'success' | 'error';
type Variant = 'secure' | 'vulnerable' | 'neutral';

export function StatefulButton({
  state = 'idle',
  onClick,
  disabled,
  className,
  labelIdle,
  labelLoading = 'Loading…',
  labelSuccess = 'Done',
  labelError = 'Retry',
  variant = 'neutral',
}: {
  state?: ButtonState;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  labelIdle: string;
  labelLoading?: string;
  labelSuccess?: string;
  labelError?: string;
  variant?: Variant;
}) {
  const isDisabled = disabled || state === 'loading';

  const palette =
    variant === 'secure'
      ? {
          ring: 'focus:ring-emerald-400/60',
          bg: 'from-emerald-500 to-teal-500',
          hover: 'hover:from-emerald-400 hover:to-teal-400',
        }
      : variant === 'vulnerable'
      ? {
          ring: 'focus:ring-fuchsia-400/60',
          bg: 'from-fuchsia-500 to-violet-500',
          hover: 'hover:from-fuchsia-400 hover:to-violet-400',
        }
      : {
          ring: 'focus:ring-white/50',
          bg: 'from-slate-600 to-slate-500',
          hover: 'hover:from-slate-500 hover:to-slate-400',
        };

  const content = {
    idle: (
      <span className="inline-flex items-center gap-2">
        {labelIdle}
      </span>
    ),
    loading: (
      <span className="inline-flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        {labelLoading}
      </span>
    ),
    success: (
      <span className="inline-flex items-center gap-2">
        <Check className="h-4 w-4" />
        {labelSuccess}
      </span>
    ),
    error: (
      <span className="inline-flex items-center gap-2">
        <X className="h-4 w-4" />
        {labelError}
      </span>
    ),
  }[state];

  return (
    <motion.button
      whileHover={{ scale: isDisabled ? 1 : 1.02 }}
      whileTap={{ scale: isDisabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={isDisabled}
      className={cn(
        'relative inline-flex h-11 items-center justify-center rounded-xl px-5 text-sm font-medium text-white transition-all focus:outline-none',
        'shadow-[0_0_0_1px_rgba(255,255,255,0.08)]',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        palette.ring,
        className
      )}
      style={{
        backgroundImage:
          'linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02)),' +
          `linear-gradient(90deg, var(--from), var(--to))`,
        // CSS variables to allow hover transitions without repaint jumps
        // Tailwind classes applied below set initial values
      }}
    >
      <span
        className={cn(
          'absolute inset-0 rounded-xl opacity-[0.18] blur-xl',
          variant === 'secure' && 'bg-gradient-to-r from-emerald-500 to-teal-500',
          variant === 'vulnerable' && 'bg-gradient-to-r from-fuchsia-500 to-violet-500',
          variant === 'neutral' && 'bg-gradient-to-r from-slate-600 to-slate-500'
        )}
        aria-hidden="true"
      />
      <span
        className={cn(
          'absolute inset-0 rounded-xl bg-gradient-to-r',
          palette.bg,
          palette.hover,
          'transition-colors'
        )}
        aria-hidden="true"
      />
      <span className="relative z-10 px-1">
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={state}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
            className="inline-flex items-center"
          >
            {content}
          </motion.span>
        </AnimatePresence>
      </span>
    </motion.button>
  );
}

