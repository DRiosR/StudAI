'use client';

import { FormEvent, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft, LogIn } from 'lucide-react';
import { getSessionUser, saveSessionUser } from '@/lib/local-session';

export default function LoginPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const user = getSessionUser();
    if (user) {
      setName(user.name);
      setEmail(user.email);
    }
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setMessage('Ingresa un correo para continuar.');
      return;
    }
    saveSessionUser({
      name: name.trim() || 'Usuario StudAI',
      email: email.trim().toLowerCase(),
    });
    router.push('/video/library');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_20%_18%,rgba(59,130,246,0.15),transparent_40%)]" />
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_82%_72%,rgba(16,185,129,0.13),transparent_45%)]" />

      <div className="relative z-10 max-w-xl mx-auto px-4 py-16">
        <Link href="/video" className="inline-flex items-center gap-2 text-white/75 hover:text-white transition">
          <ArrowLeft className="w-4 h-4" />
          Volver
        </Link>

        <div className="mt-8 rounded-3xl border border-white/10 bg-slate-900/70 p-7 backdrop-blur-sm">
          <h1 className="text-3xl font-bold">Inicio de sesion opcional</h1>
          <p className="mt-2 text-white/70">
            Si inicias sesion podras guardar y ver hasta 5 videos. Sin sesion, igual puedes generar videos normalmente.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nombre (opcional)"
              className="w-full rounded-xl border border-white/15 bg-slate-950/70 px-4 py-3 text-white placeholder-slate-400 outline-none focus:ring-2 ring-cyan-500/40"
            />
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Correo"
              type="email"
              className="w-full rounded-xl border border-white/15 bg-slate-950/70 px-4 py-3 text-white placeholder-slate-400 outline-none focus:ring-2 ring-cyan-500/40"
            />
            <button
              type="submit"
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl px-4 py-3 font-semibold text-slate-950 bg-gradient-to-r from-cyan-500 to-emerald-500 hover:opacity-90 transition"
            >
              <LogIn className="w-4 h-4" />
              Entrar y ver mis videos
            </button>
          </form>
          {message && <p className="mt-3 text-sm text-amber-300">{message}</p>}
        </div>
      </div>
    </div>
  );
}
