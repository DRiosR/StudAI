import axios from "axios";
import { GeneratedVideoResult } from "@/models/video_output";
import { Input } from "@/models/input";

// Usar variable de entorno para el endpoint del backend
// En desarrollo: http://127.0.0.1:8000
// En produccion: URL de tu servicio en Render (ej: https://studai.onrender.com)
const ENDPOINT = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const API_ENDPOINT = `${ENDPOINT}/generate/video`;

async function generateVideo(input: Input): Promise<GeneratedVideoResult> {
  if (!input.files || input.files.length === 0) {
    throw new Error("No files provided in input.");
  }

  // Use the browser's native FormData
  const formData = new FormData();
  // Append the first PDF File
  formData.append("file", input.files[0], input.files[0].name);
  formData.append("user_additional_input", input.user_additional_input);

  try {
    const response = await axios.post<GeneratedVideoResult>(
      API_ENDPOINT,
      formData,
      {
        // Let axios/browser set proper multipart boundary headers automatically
        timeout: 600_000, // 10 min read timeout
      }
    );

    console.log("Response data:", response.data);

    return response.data;
  } catch (err: any) {
    if (err?.response) {
      throw new Error(
        `API Error: ${err?.response?.status || 'Unknown status'} - ${JSON.stringify(err?.response?.data || 'Unknown data')}`
      );
    }
    throw err;
  }
}

export async function pollVideoStatus(jobId: string): Promise<GeneratedVideoResult> {
  const STATUS_ENDPOINT = `${ENDPOINT}/generate/video/status/${jobId}`;
  
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const response = await axios.get(STATUS_ENDPOINT);
        const status = response.data;
        
        console.log("Polling status:", status);
        
        if (status.status === "completed") {
          // Obtener resultados completos
          const resultResponse = await axios.get(`${ENDPOINT}/generate/video/result/${jobId}`);
          resolve(resultResponse.data);
        } else if (status.status === "error") {
          reject(new Error(status.error || "Error generando video"));
        } else {
          // Seguir haciendo polling cada 2 segundos
          setTimeout(poll, 2000);
        }
      } catch (err: any) {
        reject(err);
      }
    };
    
    poll();
  });
}

export default generateVideo;
