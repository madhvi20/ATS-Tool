import os
import json
import csv
from google.cloud import vision_v1 as vision
from uploader import upload_to_gcs, download_from_gcs

def scan_document(client, file_path, bucket_name, output_dir='output'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    extracted_text = ""

    try:
        destination_blob_name = os.path.basename(file_path)
        upload_to_gcs(bucket_name, file_path, destination_blob_name)
        gcs_uri = f'gs://{bucket_name}/{destination_blob_name}'
        
        if file_path.lower().endswith('.pdf') or file_path.lower().endswith('.tiff'):
            gcs_source = vision.GcsSource(uri=gcs_uri)
            input_config = vision.InputConfig(gcs_source=gcs_source, mime_type='application/pdf' if file_path.lower().endswith('.pdf') else 'image/tiff')
            output_gcs_uri = f'gs://{bucket_name}/{output_dir}/{os.path.basename(file_path).replace(".", "_output.")}.json'
            output_config = vision.OutputConfig(gcs_destination=vision.GcsDestination(uri=output_gcs_uri), batch_size=1)

            request = vision.AsyncBatchAnnotateFilesRequest(
                requests=[vision.AsyncAnnotateFileRequest(
                    features=[vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
                    input_config=input_config,
                    output_config=output_config
                )]
            )
            operation = client.async_batch_annotate_files(request=request)

            print("Waiting for operation to complete...")
            response = operation.result(timeout=300)  # Wait up to 5 minutes

            if response.responses and response.responses[0].error.message:
                raise Exception(f"API error: {response.responses[0].error.message}")

            output_blob_name = f'{output_dir}/{os.path.basename(file_path).replace(".", "_output.")}.json'
            local_output_file = os.path.join('output', f'{os.path.basename(file_path).replace(".", "_output.")}.json')
            download_from_gcs(bucket_name, output_blob_name, local_output_file)

            with open(local_output_file, 'r') as f:
                results_json = json.load(f)
            
            for page in results_json['responses']:
                extracted_text += page.get('fullTextAnnotation', {}).get('text', '')

        elif file_path.lower().endswith(('.jpeg', '.jpg', '.png', '.gif', '.bmp')):
            with open(file_path, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
        
            if response.error.message:
                raise Exception(f'API error: {response.error.message}')
        
            texts = response.text_annotations
            extracted_text = texts[0].description if texts else ''
        
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as text_file:
                extracted_text = text_file.read()
        
        else:
            raise Exception("Unsupported input file format.")
        
        return extracted_text
    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        return ""

def bulk_scan_documents(input_folder, output_path):
    client = vision.ImageAnnotatorClient.from_service_account_json('service_account.json')
    bucket_name = 'bucketnameop'  
    extracted_data = []

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        print(f"Scanning: {file_path}")
        extracted_text = scan_document(client, file_path, bucket_name)
        if extracted_text:
            extracted_data.append({'filename': filename, 'extracted_text': extracted_text})
    
    if extracted_data:
        keys = extracted_data[0].keys()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(extracted_data)
        print(f"Extraction complete. Data saved to {output_path}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    input_folder = 'input'
    output_path = 'output/extracted_data.csv'  
    bulk_scan_documents(input_folder, output_path)
