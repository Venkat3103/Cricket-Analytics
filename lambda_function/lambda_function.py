import urllib.request
import zipfile
import os
import boto3
from io import BytesIO  # Import BytesIO from io module

def lambda_handler(event, context):
    # Fetch the zip file from the URL for all games
    all_zip_url = "https://cricsheet.org/downloads/recently_added_2_json.zip"
    # Open the zip file as a stream
    with urllib.request.urlopen(all_zip_url) as response:
        with zipfile.ZipFile(BytesIO(response.read()), 'r') as z:
            # Read the README.txt file into memory
            with z.open('README.txt') as readme_file:
                readme_contents = readme_file.readlines()

            # Process README.txt contents
            match_info = {}
            for line in readme_contents[24:]:
                line = line.strip()
                if line:  # Check if the line is not empty
                    fields = line.split(b' - ')
                    match_id = fields[4].decode('utf-8')  # Match ID
                    gender = fields[3].decode('utf-8')    # Gender
                    team_type = fields[1].decode('utf-8') # Team Type
                    match_type = fields[2].decode('utf-8') # Match Type
                    match_info[match_id] = (gender, team_type, match_type)

            # Process the JSON files and save them to S3 based on the extracted match info
            s3 = boto3.client('s3')
            for filename in z.namelist():
                if filename.endswith('.json'):
                    # Extract match ID from filename
                    match_id = filename.split('.')[0]
                    
                    # Get the destination directory based on the match info
                    if match_id in match_info:
                        gender, team_type, match_type = match_info[match_id]
                        
                        # Define the S3 directory structure based on gender, team type, and match type
                        s3_key = f"ball-by-ball-data/gender={gender}/team_type={team_type}/match_type={match_type}/{filename}"
                        
                        # Upload the JSON file to S3
                        with z.open(filename) as json_file:
                            s3.upload_fileobj(json_file, 'ball-by-ball-data', s3_key)

    return "JSON files uploaded to S3 according to the specified partitioning rules"
