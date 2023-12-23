from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def upload_blob(data, filename):
    try:
        blob_service_client = BlobServiceClient.from_connection_string("<connection_string>")
        blob_client = blob_service_client.get_blob_client("https://storageformyapp.blob.core.windows.net/praetoriandetection")

        print("\nUploading to Azure Storage as blob:\n\t" + filename)

        # Upload the created file
        with open(filename, "rb") as data:
            blob_client.upload_blob(data)

    except Exception as ex:
        print('Exception:')
        print(ex)

