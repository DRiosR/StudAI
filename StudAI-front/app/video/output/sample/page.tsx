'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { FileText, Video, ArrowLeft, Sparkles } from 'lucide-react';
import type { GeneratedVideoResult } from '@/models/video_output';

const sampleResult: GeneratedVideoResult = {
    pdf_name: '5b84e690-cb93-4ae1-84fc-bac91232bec5_Clase_08.pdf',
    pdf_blob_url: 'https://studai.blob.core.windows.net/files/53deb1bc-3fda-46df-b0be-97d358c3ffe1_Clase_01.pdf?se=2025-11-10T16%3A48%3A28Z&sp=r&sv=2025-11-05&sr=b&sig=Y0OCtVhWH7kU9n7TLdVQWSH/ItwgKdkuilSAhzB4hy0%3D',
    script: `[SP]
  No mames, casi regalo todo mi storage en vivo.
  Transmitiendo y sin darme cuenta pegué una API key en el chat.
  Obvio, se desató el caos.
  Gente entrando, archivos volando.
  Aprendí la lección en cinco minutos y millones de vistas.
  
  Escucha.
  Hay dos mundos en la nube.
  Las keys son como llaves físicas.
  Fáciles, directas, pero si se filtran, ¡pum! Todo comprometido.
  RBAC es otra onda.
  Le das roles, no llaves.
  Identidades, permisos, control fino.
  Rotación automática, auditoría chingona.
  En Azure existen las Managed Identities.
  El servicio se autentica solo.
  Sin manejar secretos.
  Como magia.
  
  Consejos rápidos entre stream y meme:
  No dejes keys en el chat.
  Usa roles y el principio de menor privilegio.
  Guarda lo inevitable en un Key Vault.
  Revisa accesos como revisas los donativos raros.
  
  Twist final: el viewer que “me hackeó” en realidad me ayudó a configurar RBAC.
  Y ahora soy más seguro y más viral.
  
  Si jugas con llaves, acabarás abriendo la puerta… a todos.`,
    audio_url: 'https://studai.blob.core.windows.net/audio/53deb1bc-3fda-46df-b0be-97d358c3ffe1_Clase_01.pdf_spanish.mp3?se=2025-11-10T16%3A48%3A46Z&sp=r&sv=2025-11-05&sr=b&sig=EPRRAnko6/QV/poj2dfUCtVTwYXMIoXj12Zpbbo%2BLFE%3D',
    video_url: 'https://studai.blob.core.windows.net/videos/53deb1bc-3fda-46df-b0be-97d358c3ffe1_Clase_01.pdf_final_video_spanish.mp4?sp=r&st=2025-11-23T23:12:54Z&se=2025-12-01T07:27:54Z&sv=2024-11-04&sr=b&sig=S5GX8bnndn%2F9Ss94Ng8NHQepC9kAmvc7RZ%2BQHgI37MQ%3D'
  };
  

export default function VideoOutputSamplePage() {
  const result = sampleResult;

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-slate-900 to-black relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(120,119,198,0.08),rgba(255,255,255,0))]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(149,76,233,0.07),rgba(255,255,255,0))]" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-10 md:py-16">
        <div className="mb-8 flex items-center justify-between">
          <Link
            href="/video"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Generate
          </Link>
          <div className="inline-flex items-center gap-2 text-white/80">
            <Sparkles className="w-5 h-5 text-pink-400" />
            <span className="font-semibold">StudAI</span>
          </div>
        </div>

        <div className="space-y-8">
          <motion.h1
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-3xl md:text-4xl font-bold text-white"
          >
            StudAI — Sample Output Preview
          </motion.h1>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="bg-black/40 backdrop-blur-md border border-white/10 rounded-3xl p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <FileText className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-semibold text-white">Generated Script</h2>
            </div>
            <p className="text-white/80 leading-relaxed">{result.script}</p>
            {result.pdf_blob_url && result.pdf_name && (
              <div className="mt-4">
                <a
                  href={result.pdf_blob_url}
                  download={result.pdf_name}
                  className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
                >
                  Download Source PDF
                </a>
              </div>
            )}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="bg-black/40 backdrop-blur-md border border-white/10 rounded-3xl p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <Video className="w-6 h-6 text-pink-400" />
              <h3 className="text-lg font-semibold text-white">Final Video</h3>
            </div>
            {result.video_url ? (
              <video
                controls
                src={result.video_url}
                className="w-full rounded-2xl border border-white/10"
              />
            ) : (
              <div className="w-full h-64 flex items-center justify-center rounded-2xl border border-white/10 bg-black/20">
                <p className="text-white/60">Video no disponible</p>
              </div>
            )}
          </motion.div>

          <div className="pt-4">
            <Link
              href="/video"
              className="inline-flex items-center justify-center px-6 py-3 rounded-2xl bg-white/5 text-white border border-white/10 hover:bg-white/10 transition"
            >
              Create Another
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}


