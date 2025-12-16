import asyncio
import os
from pydantic import BaseModel
from genScript import generate_short_video_script, extract_text_from_pdf, client, deployment
import genTTS
import videoEditor




def test():
    print("Starting test pipeline...")

    # === STEP 1: Extract or generate script ===

    pdf_path = "photos/Clase_08.pdf"  # or your file path
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print("Extracting text from PDF...")
    pdf_text = extract_text_from_pdf(pdf_path)
    print("Generating short-form video script...")
    script = generate_short_video_script(pdf_text, client, deployment)

    print("Script generated ✅")

    # Optionally save the script
    print(f'Script: {script}')

    # === STEP 2: Generate TTS ===
    print("Generating TTS audio...")
    os.makedirs("output", exist_ok=True)
    audio_output = "output/audio2.mp3"
    asyncio.run(genTTS.generate_tts(script, "male", output_path=audio_output))
    print("Audio generated ✅")

    if not os.path.exists(audio_output):
        raise FileNotFoundError(f"TTS failed to produce {audio_output}")

    # === STEP 3: Combine video + audio + subtitles ===
    print("Editing video...")
    video_input = "assets/content/MC/mc1.mp4"
    final_clip = videoEditor.videoEditor(video_input, audio_output)
    print("Video edited ✅")

    # === STEP 4: Export ===
    final_video_path = "output/final_video.mp4"
    final_clip.write_videofile(
        final_video_path,
        codec="libx264",
        audio_codec="aac",
        fps=30,
        threads=4,
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )

    print(f"✅ Final video saved to: {final_video_path}")


if __name__ == "__main__":
    test()
