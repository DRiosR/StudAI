'use client';

import { useEffect, useRef, useState } from 'react';

type GameState = 'ready' | 'running' | 'gameover';

interface Pipe {
  x: number;
  gapY: number;
}

export function FlappyBird() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const animationRef = useRef<number | null>(null);
  const [score, setScore] = useState(0);
  const [best, setBest] = useState<number>(() => {
    if (typeof window === 'undefined') return 0;
    const v = localStorage.getItem('flappy_best_score');
    return v ? parseInt(v, 10) || 0 : 0;
  });
  const [state, setState] = useState<GameState>('ready');

  // Game refs (mutable to avoid re-renders)
  const scoreRef = useRef<number>(0);
  const bestRef = useRef<number>(0);
  const pipesRef = useRef<Pipe[]>([]);
  const lastSpawnRef = useRef<number>(0);
  const birdYRef = useRef<number>(0);
  const birdVYRef = useRef<number>(0);
  const timeRef = useRef<number>(0);

  // Settings
  const gapHeight = 150;
  const gravity = 0.4;
  const flapImpulse = -7.5;
  const pipeSpeed = 2.4;
  const pipeIntervalMs = 1400;
  const birdX = 80;

  // Resize canvas to device pixel ratio for crisp rendering
  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(320, Math.min(container.clientWidth, 560));
    const height = Math.round(width * 0.6); // 16:9-ish but a bit taller for play area
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
  };

  const resetGame = () => {
    setScore(0);
    scoreRef.current = 0;
    pipesRef.current = [];
    lastSpawnRef.current = 0;
    timeRef.current = 0;
    birdYRef.current = 140;
    birdVYRef.current = 0;
  };

  const spawnPipe = (canvasWidth: number, canvasHeight: number) => {
    const margin = 40;
    const minGapY = margin;
    const maxGapY = canvasHeight - margin - gapHeight;
    const gapY = Math.floor(minGapY + Math.random() * (maxGapY - minGapY));
    pipesRef.current.push({ x: canvasWidth + 40, gapY });
  };

  const flap = () => {
    if (state === 'ready') {
      resetGame();
      setState('running');
    }
    if (state === 'running') {
      birdVYRef.current = flapImpulse;
    }
    if (state === 'gameover') {
      setState('ready');
      resetGame();
    }
  };

  // Keep refs synced with state for rendering without restarting loop
  useEffect(() => {
    scoreRef.current = score;
  }, [score]);
  useEffect(() => {
    bestRef.current = best;
  }, [best]);

  // Input handlers: space/up/click/touch
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault();
        flap();
      }
    };
    const onClick = () => flap();
    window.addEventListener('keydown', onKey);
    window.addEventListener('mousedown', onClick);
    window.addEventListener('touchstart', onClick, { passive: true });
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('mousedown', onClick);
      window.removeEventListener('touchstart', onClick);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  // Resize observer
  useEffect(() => {
    resizeCanvas();
    const onResize = () => resizeCanvas();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  // Initialize values on mount
  useEffect(() => {
    resetGame();
  }, []);

  // Main game loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let lastT = performance.now();

    const step = (now: number) => {
      const dt = Math.min(32, now - lastT); // cap dt to avoid big jumps
      lastT = now;
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      timeRef.current += dt;

      // Clear
      ctx.clearRect(0, 0, width, height);

      // Background
      ctx.fillStyle = '#0b0b0b';
      ctx.fillRect(0, 0, width, height);

      // Subtle stars
      ctx.fillStyle = 'rgba(255,255,255,0.06)';
      for (let i = 0; i < 30; i++) {
        const x = ((i * 123.456) % width);
        const y = ((i * 78.9 + (timeRef.current * 0.02)) % height);
        ctx.fillRect(x, y, 2, 2);
      }

      if (state === 'ready') {
        // Idle bird bob
        birdYRef.current = 140 + Math.sin(now * 0.004) * 8;
      }

      if (state === 'running') {
        // Physics
        birdVYRef.current += gravity;
        birdYRef.current += birdVYRef.current;

        // Spawn pipes
        if (now - lastSpawnRef.current > pipeIntervalMs) {
          spawnPipe(width, height);
          lastSpawnRef.current = now;
        }
        // Move pipes and check scoring/collisions
        for (let i = pipesRef.current.length - 1; i >= 0; i--) {
          const p = pipesRef.current[i];
          p.x -= pipeSpeed;
          if (p.x + 60 < 0) {
            pipesRef.current.splice(i, 1);
          }
        }
        // Collision + score
        const birdSize = 22;
        const birdTop = birdYRef.current - birdSize / 2;
        const birdBottom = birdYRef.current + birdSize / 2;
        const birdLeft = birdX - birdSize / 2;
        const birdRight = birdX + birdSize / 2;

        let passedPipeIndex: number | null = null;
        let collided = false;
        pipesRef.current.forEach((p, idx) => {
          const pipeWidth = 60;
          const topRect = { x: p.x, y: 0, w: pipeWidth, h: p.gapY };
          const bottomRect = { x: p.x, y: p.gapY + gapHeight, w: pipeWidth, h: height - (p.gapY + gapHeight) };

          // Collision
          const overlapsX = birdRight > topRect.x && birdLeft < topRect.x + topRect.w;
          const hitTop = overlapsX && birdTop < topRect.h;
          const hitBottom = overlapsX && birdBottom > bottomRect.y;
          if (hitTop || hitBottom) {
            collided = true;
          }

          // Scoring: when pipe center passes the bird's x
          const pipeCenter = p.x + pipeWidth / 2;
          if (pipeCenter < birdX && pipeCenter > birdX - pipeSpeed - 0.5) {
            passedPipeIndex = idx;
          }
        });
        if (passedPipeIndex !== null) {
          setScore((s) => {
            const next = s + 1;
            scoreRef.current = next;
            return next;
          });
        }

        // World bounds
        if (birdTop < -20 || birdBottom > height - 10) {
          collided = true;
        }
        if (collided) {
          setState('gameover');
          const newBest = Math.max(bestRef.current, scoreRef.current);
          setBest(newBest);
          try {
            localStorage.setItem('flappy_best_score', String(newBest));
          } catch {}
        }
      }

      // Draw pipes
      ctx.fillStyle = '#7c3aed'; // purple
      pipesRef.current.forEach((p) => {
        const pipeWidth = 60;
        // top
        ctx.fillRect(p.x, 0, pipeWidth, p.gapY);
        // bottom
        ctx.fillRect(p.x, p.gapY + gapHeight, pipeWidth, height - (p.gapY + gapHeight));
      });

      // Draw bird
      const birdSize = 22;
      ctx.save();
      ctx.translate(birdX, birdYRef.current);
      ctx.rotate(Math.max(-0.5, Math.min(0.8, birdVYRef.current * 0.06)));
      ctx.fillStyle = '#f97316'; // orange
      ctx.beginPath();
      ctx.arc(0, 0, birdSize / 2, 0, Math.PI * 2);
      ctx.fill();
      // eye
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(4, -4, 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#000';
      ctx.beginPath();
      ctx.arc(5, -4, 1.5, 0, Math.PI * 2);
      ctx.fill();
      // beak
      ctx.fillStyle = '#fde047';
      ctx.beginPath();
      ctx.moveTo(10, 0);
      ctx.lineTo(16, 3);
      ctx.lineTo(16, -3);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Ground line
      ctx.strokeStyle = 'rgba(255,255,255,0.08)';
      ctx.beginPath();
      ctx.moveTo(0, height - 8);
      ctx.lineTo(width, height - 8);
      ctx.stroke();

      // UI text
      ctx.fillStyle = 'rgba(255,255,255,0.85)';
      ctx.font = '16px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';
      ctx.fillText(`Score: ${scoreRef.current}`, 12, 24);
      ctx.fillStyle = 'rgba(255,255,255,0.55)';
      ctx.fillText(`Best: ${bestRef.current}`, 12, 44);

      if (state === 'ready') {
        ctx.fillStyle = 'rgba(255,255,255,0.9)';
        ctx.font = 'bold 20px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';
        ctx.fillText('Tap / Click / Space to start', Math.max(12, (width / 2) - 130), height / 2 - 6);
      } else if (state === 'gameover') {
        ctx.fillStyle = 'rgba(255,255,255,0.95)';
        ctx.font = 'bold 22px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';
        const text = 'Game Over — Tap to retry';
        const w = ctx.measureText(text).width;
        ctx.fillText(text, Math.max(12, (width - w) / 2), height / 2);
      }

      animationRef.current = requestAnimationFrame(step);
    };

    animationRef.current = requestAnimationFrame(step);
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  return (
    <div ref={containerRef} className="w-full">
      <canvas
        ref={canvasRef}
        className="w-full rounded-xl border border-white/10 bg-black/60"
        aria-label="Flappy Bird mini game"
      />
      <div className="mt-2 text-center text-xs text-white/60">
        Tap/Click/Space to flap — time will fly while we work
      </div>
    </div>
  );
}


