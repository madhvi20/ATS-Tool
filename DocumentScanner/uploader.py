import os
from google.cloud import storage

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    try:
        storage_client = storage.Client.from_service_account_json('service_account.json')
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    except Exception as e:
        print(f"Failed to upload {source_file_name} to {destination_blob_name}: {e}")

def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    try:
        storage_client = storage.Client.from_service_account_json('service_account.json')
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")
    except Exception as e:
        print(f"Failed to download {source_blob_name} to {destination_file_name}: {e}")
