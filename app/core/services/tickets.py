import json
import requests
from google.cloud import storage
from google.oauth2 import service_account

from app.core.config import settings


def upload_to_gcp(photo_content: bytes, destination_blob_name: str):
    """
    Uploads a photo to Google Cloud Storage bucket.
    Args:
        photo_content (bytes): The content of the photo.
        user_id (str): The ID of the user.
        bucket_name (str): The name of the GCP bucket.
        destination_blob_name (str): The name of the blob in the bucket.
    Returns:
        str: The path of the uploaded blob in the bucket.
    """
    try:
        credentials_info = json.loads(settings.GCP_BUCKET_CREDENTIALS)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info)

        # Initialize the Cloud Storage client with the credentials
        gcp_client = storage.Client(credentials=credentials)

        # Get the bucket
        bucket = gcp_client.bucket(settings.TICKET_BUCKET_NAME)

        # Create a blob object
        blob = bucket.blob(destination_blob_name)

        # Upload the photo content to the bucket
        blob.upload_from_string(photo_content, content_type='image/jpeg')

        print(f"File uploaded to {destination_blob_name}.")
        return True

    except Exception as e:
        raise e
