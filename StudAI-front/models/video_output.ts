export type GeneratedVideoResult = {
    job_id?: string;
    status?: string;
    message?: string;
    pdf_name?: string;
    pdf_blob_url?: string;
    script: string;
    audio_url: string;
    video_url: string | null;
    topic?: string;
  };
  