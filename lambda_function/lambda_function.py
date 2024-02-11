import os
import zipfile
import urllib.request
import boto3

def lambda_handler(event, context):
    # Fetch the zip file from the URL
    zip_url = "https://cricsheet.org/downloads/recently_added_2_json.zip"
    zip_filename = "/tmp/recently_added_2_json.zip"
    urllib.request.urlretrieve(zip_url, zip_filename)

    # Extract the zip file
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall("/tmp/")

    # Upload all JSON files to the S3 bucket
    s3 = boto3.client('s3')
    bucket_name = "ball-by-ball-data"
    for root, dirs, files in os.walk("/tmp/"):
        for file in files:
            if file.endswith(".json"):
                s3.upload_file(os.path.join(root, file), bucket_name, file)

    return {
        'statusCode': 200,
        'body': 'Files uploaded successfully!'
    }
