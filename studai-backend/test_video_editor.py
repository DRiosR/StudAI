import os
import time
from services.videoEditor import videoEditor

# Absolute project root
PROJECT_ROOT = "/Users/martinortiz/Desktop/Cloud_School/studai-backend"

# Inputs
BASE_VIDEO = os.path.join(PROJECT_ROOT, "assets/content/MC/mc1.mp4")
TEST_AUDIO = os.path.join(
    PROJECT_ROOT,
    "output/audio/5b84e690-cb93-4ae1-84fc-bac91232bec5_Clase_08.pdf.mp3"
)
LANGUAGE = "spanish"

# Output
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output/videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)
FINAL_OUTPUT = os.path.join(OUTPUT_DIR, "test_final_video_spanish.mp4")


def main():
    if not os.getenv("ASSEMBLYAI_API_KEY"):
        print("Missing ASSEMBLYAI_API_KEY environment variable. Set it and rerun.")
        return
    if not os.path.exists(BASE_VIDEO):
        print(f"Base video not found at {BASE_VIDEO}")
        return
    if not os.path.exists(TEST_AUDIO):
        print(f"Test audio not found at {TEST_AUDIO}")
        return

    start = time.perf_counter()
    final_path = videoEditor(BASE_VIDEO, TEST_AUDIO, LANGUAGE, FINAL_OUTPUT)
    elapsed = time.perf_counter() - start
    print(f"Final video: {final_path}")
    print(f"Elapsed: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()

