import asyncio
import io
import aiohttp
import aiohttp.helpers
import glob
from io import BytesIO
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import os
from async_timeout import timeout

load_dotenv()
azure_blob_account = os.getenv("AZURE_BLOB_ACCOUNT")
output_folder_name = os.getenv("OUTPUT_FOLDER_NAME")
container_name_video = os.getenv("CONTAINER_NAME_VIDEO")

class Uploader:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.azure_blob_account = azure_blob_account

    async def read_in_chunks(self, stream, chunk_size=4 * 1024 * 1024):
        while True:
            chunk = await stream.read(chunk_size)
            if not chunk:
                break
            yield chunk


    async def upload_video_blob(self, video_stream, filename):
        try:
            print("Envoi de la vidéo vers Azure Blob Storage...")
            blob_service_client = BlobServiceClient.from_connection_string(self.azure_blob_account)
            blob_container_client = blob_service_client.get_container_client("onpremvideo")
            blob_client = blob_container_client.get_blob_client(filename)

            async with aiohttp.ClientSession() as session:
                video_data = io.BytesIO(video_stream.read()).getvalue()

                async with session.post(url=blob_client.url, data=video_data, headers={'Content-Type': 'video/x-msvideo'}) as resp:
                    assert resp.status == 201

            print("Vidéo envoyée avec succès.")
        except Exception as ex:
                print('Exception:')
                print(ex)
                print("Vidéo non envoyée.")


    async def __call__(self):
        video_files = glob.glob(f"{self.output_folder}/*.avi")
        print(f"Found {len(video_files)} video files.")
        if len(video_files) == 0:
            print("No video files found.")
            return

        video_file = sorted(video_files)[-1]  # Select the newest video file

        with open(video_file, 'rb') as video_data:
            video_stream = BytesIO(video_data.read())
            # Generate unique filename
            filename = f"{self.output_folder}/{os.path.basename(video_file)}"
            print(f"Uploading {filename}...")
            # Upload video to Azure Blob Storage
            await self.upload_video_blob(video_stream, filename)

        print("Video upload complete.")


if __name__ == "__main__":
    uploader = Uploader(output_folder="video_record")
    asyncio.run(uploader())