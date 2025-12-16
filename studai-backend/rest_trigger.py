"""Simple REST client to trigger the video generation pipeline.

Usage:
  python rest_trigger.py \
    # This script uses constants below; edit ENDPOINT/PDF_PATH/USER_INPUT as needed.

The script sends a multipart/form-data POST to the FastAPI endpoint:
  - field 'file': the PDF file (UploadFile)
  - field 'user_additional_input': optional text

It prints the HTTP response status and body.
"""
import json
import sys
import os

try:
    import requests
except ImportError:
    print("The 'requests' package is required. Install with: pip install requests")
    sys.exit(1)


# Minimal script: configure endpoint and inputs below, then run the file.
ENDPOINT = "http://127.0.0.1:8000/generate/video"  # matches FastAPI route in main.py
PDF_PATH = "photos/Clase_08.pdf"  # local path to the PDF you want to upload
USER_INPUT = "En estilo de un wey haciendo un stream de twitch Haz el video en español  y que funcione!. Y usa palabras coloquiales como no mames o puto, chingon, o wey, etc. Y no uses emojis"

print(f"POSTing to {ENDPOINT} with file: {PDF_PATH}")
try:
    if not os.path.exists(PDF_PATH):
        print(f"File not found: {PDF_PATH}")
        sys.exit(1)

    with open(PDF_PATH, "rb") as f:
        files = {
            "file": (os.path.basename(PDF_PATH), f, "application/pdf")
        }
        data = {
            "user_additional_input": USER_INPUT
        }
        # Allow long-running processing: 10s connect timeout, 600s read timeout
        resp = requests.post(ENDPOINT, files=files, data=data, timeout=(10, 600))

    print(f"Response: {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
except Exception as e:
    print(f"Request failed: {e}")
