import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

# --- 1. Setup ---
API_KEY = os.getenv("ASSEMBLYAI_API_KEY")  # Replace with your actual API key
audio_filename = "output/audio.mp3"  # Replace with your audio file path

base_url = "https://api.assemblyai.com/v2"
headers = {
    "authorization": API_KEY
}

# --- 2. Upload your local audio file ---
# AssemblyAI needs a URL. If your file is local,
# you first upload it to a temporary, secure URL.
def upload_file(filename):
    with open(filename, 'rb') as f:
        response = requests.post(f"{base_url}/upload",
                                 headers=headers,
                                 data=f)
    
    if response.status_code != 200:
        raise Exception(f"Failed to upload file: {response.json()}")
        
    return response.json()["upload_url"]

print("Uploading file...")
audio_url = upload_file(audio_filename)

# --- 3. Submit the transcription job ---
# This is where you request word-level timestamps
json_payload = {
    "audio_url": audio_url,
    "word_timestamps": True  # <-- This is the equivalent of 'word_timestamps=True'
}

response = requests.post(f"{base_url}/transcript",
                         json=json_payload,
                         headers=headers)

transcript_id = response.json()['id']
print(f"Transcription job started with ID: {transcript_id}")

# --- 4. Poll for the result ---
# Async transcription can take time, so we poll for the status
while True:
    poll_endpoint = f"{base_url}/transcript/{transcript_id}"
    poll_response = requests.get(poll_endpoint, headers=headers)
    result = poll_response.json()
    
    if result['status'] == 'completed':
        print("Transcription complete!")
        break
    elif result['status'] == 'failed':
        raise Exception(f"Transcription failed: {result['error']}")
    
    print("Transcription in progress...")
    time.sleep(5) # Wait 5 seconds before checking again

# --- 5. Process the results (similar to your script) ---
# The structure is slightly different: AssemblyAI returns a flat
# list of words, not nested segments.

wordlevel_info = []

# 'result['words']' contains the list you're looking for
for word in result['words']:
    # AssemblyAI provides timestamps in milliseconds
    start_s = word['start'] / 1000.0
    end_s = word['end'] / 1000.0
    
    # This prints in the same format as your example
    print("[%.2fs -> %.2fs] %s" % (start_s, end_s, word['text']))
    
    # This builds the same list of dictionaries
    wordlevel_info.append({
        'word': word['text'],
        'start': start_s,
        'end': end_s
    })

# print(wordlevel_info)