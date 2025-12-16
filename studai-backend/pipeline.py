import os, asyncio
import aiohttp
from services.genScript_correct import extract_text_from_pdf, generate_short_video_script, client, deployment
from services import genTTS, videoEditor
from utils.azure_blob import upload_to_blob
import uuid

async def process_pipeline(pdf_path: str, ws=None, user_additional_input: str | None = None, callback_url: str | None = None):
    async def safe_send(data: dict):
        # If a callback_url is provided, POST updates to it. Otherwise, fall back to websocket (if present).
        if callback_url:
            try:
                async with aiohttp.ClientSession() as session:
                    # short timeout to avoid blocking the pipeline for too long
                    await session.post(callback_url, json=data, timeout=10)
                return
            except Exception as e:
                print(f"Failed to POST update to callback_url {callback_url}: {e}")

        # Fallback to websocket if available
        try:
            if ws is not None:
                # Some ws implementations expose client_state; if not, just attempt to send
                state_name = getattr(getattr(ws, 'client_state', None), 'name', None)
                if state_name == "CONNECTED":
                    await ws.send_json(data)
                else:
                    # Try to send regardless; send_json will raise if disconnected
                    await ws.send_json(data)
        except Exception as e:
            print(f"Notification send failed (websocket or callback): {e}")

    try:

        #name of the file uploaded to blob will be uuid

        pdf_url = await upload_to_blob(pdf_path, f"files/{pdf_path.split('/')[-1]}")

        await safe_send({"stage": "start", "message": "🚀 Starting video generation pipeline...", "pdf_url": pdf_url})




        # === STEP 1: Extract text ===
        await safe_send({"stage": "pdf_extraction", "message": "📄 Extracting text from PDF..."})
        pdf_text = await asyncio.to_thread(extract_text_from_pdf, pdf_path)

        # === STEP 2: Generate script ===
        await safe_send({"stage": "script_generation", "message": "✍️ Generating short-form video script..."})
        script = await asyncio.to_thread(
            generate_short_video_script,
            pdf_text,
            client,
            deployment,
            user_additional_input=user_additional_input
        )
        if not script:
            raise ValueError("Generated script is empty.")

        # === STEP 3: Generate TTS ===
        await safe_send({"stage": "tts_generation", "message": "🎧 Generating voiceover..."})
        os.makedirs("output/audio", exist_ok=True)
        audio_path = "output/audio/audio.mp3"
        audio_path, language = await genTTS.generate_tts(script, gender="male", output_path=audio_path)

        # === STEP 4: Video Editing ===
        await safe_send({"stage": "video_editing", "message": "🎬 Merging video and audio..."})
        os.makedirs("output/videos", exist_ok=True)
        os.makedirs("output/temp", exist_ok=True)

        base_video = "assets/content/MC/mc1.mp4"
        final_video_path = f"output/videos/{pdf_path.split('/')[-1].split('.')[0]}_final_video_{language}.mp4"

        # Heartbeat configuration
        HEARTBEAT_INTERVAL = 10
        stop_heartbeat = asyncio.Event()

        async def heartbeat():
            try:
                while not stop_heartbeat.is_set():
                    await safe_send({"stage": "video_rendering", "message": "⏳ Rendering/uploading — still working..."})
                    await asyncio.sleep(HEARTBEAT_INTERVAL)
            except asyncio.CancelledError:
                return

        heartbeat_task = asyncio.create_task(heartbeat())

        # CPU-bound video render
        def render_video():
            return videoEditor.videoEditor(base_video, audio_path, language, output_path=final_video_path)

        # Run video render in background thread
        final_video_path = await asyncio.to_thread(render_video)

        # === STEP 5: Upload Video with Heartbeat ===
        async def upload_with_heartbeat(file_path, blob_path):
            # Wrap Azure upload to send progress messages
            # (if you want, can implement chunked upload for detailed %)
            await safe_send({"stage": "uploading", "message": "⬆️ Uploading video..."})
            return await upload_to_blob(file_path, blob_path)

        video_url = await upload_with_heartbeat(final_video_path, f"videos/final_video_{language}.mp4")
        audio_url = await upload_to_blob(audio_path, f"audio/{language}.mp3")  # small, fast

        # Stop heartbeat after upload
        stop_heartbeat.set()
        try:
            await heartbeat_task
        except Exception:
            pass

        # Final success message
        json_data = {
            "stage": "completed",
            "message": "✅ Video generation completed!",
            "script": script,
            "audio_url": audio_url,
            "video_url": video_url,
            "pdf_url": pdf_url
        }
        await safe_send(json_data)

    except Exception as e:
        await safe_send({"stage": "error", "message": f"❌ Error: {str(e)}"})
