import json
import requests
import base64
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
        credentials = None
        try:
            with open(settings.GCP_BUCKET_CREDENTIALS_ADDRESS, 'r') as f:
                credentials_info = json.load(f)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info)
        except Exception as e:
            print(e)
            raise Exception("Invalid GCP credentials")

        gcp_client = storage.Client(credentials=credentials)
        bucket = gcp_client.bucket(settings.TICKET_BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(photo_content, content_type='image/jpeg')

        return True

    except Exception as e:
        raise e
