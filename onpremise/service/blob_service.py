from azure.storage.blob import BlobServiceClient

def upload_blob(data, filename):
    try:
        # Connect to the Azure storage account
        connect_str = "DefaultEndpointsProtocol=https;AccountName=praetorianblob;AccountKey=PEv0rg+hl5Y2j4I52M6eddkBVK/1JghLJj95PfBtqC8F/T3bjKgfTwxxi6kGGPIvonrSLvvkI9Vc+AStNfJI6w==;EndpointSuffix=core.windows.net"
        blob_client = BlobServiceClient.from_connection_string(connect_str)
        print("\nUploading to Azure Storage as blob:\n\t" + filename)
        # Upload the created file
        blob_client = blob_client.get_blob_client(container="onpremvideo", blob=filename)
        blob_client.upload_blob(data)
            
    except Exception as ex:
        print('Exception:')
        print(ex)

