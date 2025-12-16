import os
import asyncio
import aiohttp
from services.genScript_responses import generate_short_video_script, client, deployment
from services import genTTS, videoEditor
from utils.azure_blob import upload_to_blob, download_from_blob
import uuid


async def process_pipeline(
    pdf_path: str,
    ws=None,
    user_additional_input: str | None = None,
    callback_url: str | None = None
):
    """
    FULL StudAI pipeline:
    1. Upload PDF to Blob
    2. Download local temp file
    3. Generate script (PDF fed directly to Azure OpenAI Responses API)
    4. Generate TTS
    5. Generate video
    6. Upload video + audio to Blob
    7. Send WS/callback updates
    """

    # Send updates either via webhook or websocket
    async def safe_send(data: dict):
        if callback_url:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(callback_url, json=data, timeout=10)
                return
            except Exception as e:
                print(f"Callback error: {e}")

        if ws is not None:
            try:
                await ws.send_json(data)
            except Exception as e:
                print(f"WS send error: {e}")

    try:
        # ----------------------------------------------------------------------
        # STEP 0 — Upload original PDF to Blob Storage
        # ----------------------------------------------------------------------
        blob_name = f"files/{uuid.uuid4()}.pdf"
        pdf_url = await upload_to_blob(pdf_path, blob_name)

        await safe_send({
            "stage": "start",
            "message": "🚀 Pipeline started",
            "pdf_url": pdf_url
        })

        # ----------------------------------------------------------------------
        # STEP 1 — Download PDF locally (Azure Blob → backend)
        # ----------------------------------------------------------------------
        await safe_send({
            "stage": "download_pdf",
            "message": "📥 Downloading PDF from blob..."
        })

        local_pdf_temp = f"/tmp/{uuid.uuid4()}.pdf"
        await download_from_blob(pdf_url, local_pdf_temp)

        # ----------------------------------------------------------------------
        # STEP 2 — Generate Script (NO OCR, model reads PDF directly)
        # ----------------------------------------------------------------------
        await safe_send({
            "stage": "script_generation",
            "message": "✍️ Generating video script..."
        })

        script = await asyncio.to_thread(
            generate_short_video_script,
            local_pdf_temp,       # <-- send PDF path, NOT text
            client,
            deployment,
            user_additional_input=user_additional_input
        )

        if not script:
            raise ValueError("Generated script is empty.")

        # ----------------------------------------------------------------------
        # STEP 3 — Generate TTS
        # ----------------------------------------------------------------------
        await safe_send({
            "stage": "tts_generation",
            "message": "🎧 Generating voiceover..."
        })

        os.makedirs("output/audio", exist_ok=True)
        audio_path = f"output/audio/{uuid.uuid4()}.mp3"
        audio_path, language = await genTTS.generate_tts(
            script,
            gender="male",
            output_path=audio_path
        )

        # ----------------------------------------------------------------------
        # STEP 4 — Render Video
        # ----------------------------------------------------------------------
        await safe_send({
            "stage": "video_editing",
            "message": "🎬 Rendering video..."
        })

        os.makedirs("output/videos", exist_ok=True)
        os.makedirs("output/temp", exist_ok=True)

        base_video = "assets/content/MC/mc1.mp4"
        final_video_path = f"output/videos/{uuid.uuid4()}_{language}.mp4"

        # Heartbeat while rendering
        HEARTBEAT_INTERVAL = 10
        stop_heartbeat = asyncio.Event()

        async def heartbeat():
            try:
                while not stop_heartbeat.is_set():
                    await safe_send({
                        "stage": "video_rendering",
                        "message": "⏳ Rendering... still working"
                    })
                    await asyncio.sleep(HEARTBEAT_INTERVAL)
            except asyncio.CancelledError:
                return

        heartbeat_task = asyncio.create_task(heartbeat())

        # CPU-bound video composition
        def do_render():
            return videoEditor.videoEditor(
                base_video,
                audio_path,
                language,
                output_path=final_video_path
            )

        final_video_path = await asyncio.to_thread(do_render)

        # Stop heartbeat
        stop_heartbeat.set()
        try:
            await heartbeat_task
        except:
            pass

        # ----------------------------------------------------------------------
        # STEP 5 — Upload final video + audio
        # ----------------------------------------------------------------------
        async def upload_with_updates(local_path, blob_path):
            await safe_send({
                "stage": "uploading",
                "message": "⬆️ Uploading media..."
            })
            return await upload_to_blob(local_path, blob_path)

        video_url = await upload_with_updates(
            final_video_path, f"videos/{uuid.uuid4()}_{language}.mp4"
        )

        audio_url = await upload_to_blob(
            audio_path, f"audio/{uuid.uuid4()}_{language}.mp3"
        )

        # ----------------------------------------------------------------------
        # DONE
        # ----------------------------------------------------------------------
        await safe_send({
            "stage": "completed",
            "message": "✅ Video generation complete!",
            "script": script,
            "audio_url": audio_url,
            "video_url": video_url,
            "pdf_url": pdf_url
        })

    except Exception as e:
        await safe_send({
            "stage": "error",
            "message": f"❌ Error: {str(e)}"
        })
