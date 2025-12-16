import axios from "axios";
import { GeneratedVideoResult } from "@/models/video_output";
import { Input } from "@/models/input";

const ENDPOINT = "http://127.0.0.1:8000/generate/video";

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
      ENDPOINT,
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

export default generateVideo;
