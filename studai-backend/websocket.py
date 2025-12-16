import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws/generate"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "pdf_name": "CAiEM.pdf",
            "user_additional_input": "En estilo de Rocky Haz el video en español y que funcione!. Y usa palabras coloquiales como no mames o puto, chingon, o wey, etc. Y no uses emojis"
        }))

        try:
            async for msg in ws:
                data = json.loads(msg)
                print(f"{data['stage']} -> {data['message']}")
                if data['stage'] == "completed":
                    print("\n🎬 Final URLs:")
                    print("Script:", data['script'])
                    print("Audio URL:", data['audio_url'])
                    print("Video URL:", data['video_url'])
        except:
            print("WebSocket closed")

asyncio.run(test_ws())
