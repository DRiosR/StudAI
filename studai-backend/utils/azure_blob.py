import os
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
load_dotenv()

AZURE_BLOB_ACCOUNT_NAME = os.getenv("AZURE_BLOB_ACCOUNT_NAME")
AZURE_BLOB_KEY = os.getenv("AZURE_BLOB_KEY")

blob_service_client = BlobServiceClient(
    f"https://{AZURE_BLOB_ACCOUNT_NAME}.blob.core.windows.net",
    credential=AZURE_BLOB_KEY
)

async def upload_to_blob(file_path: str, blob_name: str) -> str:
    """
    Uploads a file to Azure Blob Storage and returns a SAS URL available for 1 day.
    """
    print(f"Uploading file to blob: {file_path} -> {blob_name}")

    # Detect container
    parts = blob_name.split("/", 1)
    if len(parts) < 2:
        raise ValueError("blob_name must include container prefix (e.g. 'audio/audio.mp3')")
    container_name, blob_path = parts

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_path
    )

    # Upload the file
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    # Generate SAS token valid for 30 days
    sas_token = generate_blob_sas(
        account_name=AZURE_BLOB_ACCOUNT_NAME,
        container_name=container_name,
        blob_name=blob_path,
        account_key=AZURE_BLOB_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(days=30),
    )

    sas_url = f"{blob_client.url}?{sas_token}"
    print(f"SAS URL: {sas_url}")

    return sas_url



async def main():
    file_path = "output/videos/5b84e690-cb93-4ae1-84fc-bac91232bec5_Clase_08.pdf_final_video_spanish.mp4"
    blob_name = "videos/test.mp4"
    sas_url = await upload_to_blob(file_path, blob_name)
    print(sas_url)

if __name__ == "__main__":
    asyncio.run(main())
