import json
import base64
import boto3
from botocore.exceptions import NoCredentialsError
import time
# Others
import cgi
from io import BytesIO
#from requests_toolbelt.multipart import decoder

# Initialize the S3 client
s3 = boto3.client('s3')
BUCKET_NAME = 'mybucketforuploadimages'  # Replace with your actual bucket name

def do_stuff(multipart_data):
    # Initialize variables to hold the file and metadata
    file_content = None
    file_name = None
    file_type = None

    # Now you can access the file and metadata from the parsed data
    for part in multipart_data.parts:
        content_disposition = part.headers.get('Content-Disposition', '')
        if 'file' in content_disposition:
            # This is the file part
            file_content = part.content
            file_name = part.headers.get('Content-Disposition').split('filename="')[1].split('"')[0]
            file_type = part.headers.get('Content-Type')
            print(f"Received file: {file_name}, Type: {file_type}")

            # Process the file (e.g., save it to S3 or store it locally)
        elif 'fileName' in content_disposition:
            # This is the file name metadata
            file_name_metadata = part.content.decode('utf-8')
            print(f"Received file name metadata: {file_name_metadata}")
        elif 'fileType' in content_disposition:
            # This is the file type metadata
            file_type_metadata = part.content.decode('utf-8')
            print(f"Received file type metadata: {file_type_metadata}")
    return file_content

def extract_file_from_body(event):
    """
    Helper function to extract file content and metadata from the raw event body.
    Returns file_content, file_name, file_type, file_name_metadata, and file_type_metadata.
    """
    # Check if the body is base64 encoded (API Gateway might encode the body if binary data is sent)
    if event['isBase64Encoded']:
        body = base64.b64decode(event['body'])
    else:
        body = event['body'].encode('utf-8')

    # Create a BytesIO object from the raw binary body (useful for cgi parsing)
    body_io = BytesIO(body)

    # Parse the multipart form data
    form = cgi.FieldStorage(fp=body_io, headers=event['headers'], environ={'REQUEST_METHOD': 'POST'})

    file_content = None
    file_name = None
    file_type = None
    file_name_metadata = None
    file_type_metadata = None

    # Check for the file field in the form data
    if "file" in form:
        file_field = form["file"]
        file_content = file_field.file.read()  # Get the binary file content
        file_name = file_field.filename        # Get the filename
        file_type = file_field.type            # Get the file type (MIME type)
        print(f"Received file: {file_name}, Type: {file_type}")

    # Check for file name and type metadata
    file_name_metadata = form.getvalue("fileName", None)
    file_type_metadata = form.getvalue("fileType", None)
    if file_name_metadata:
        print(f"Received file name metadata: {file_name_metadata}")
    if file_type_metadata:
        print(f"Received file type metadata: {file_type_metadata}")

    return file_content, file_name, file_type, file_name_metadata, file_type_metadata

def lambda_handler(event, context):
    # Extract file and metadata using the helper function
    try:
        file_content, file_name, file_type, file_name_metadata, file_type_metadata = extract_file_from_body(event)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error PARSING the image to S3: {str(e)}'})
        }

    if file_content:
        try:
            # Decode the image data
            #image_data = base64.b64decode(file_content)

            # Define a file name (you can make it dynamic if needed)
            file_name = f'uploaded_image_{int(time.time())}.jpg'  # Change the name or make it dynamic

            # Set the parameters for the S3 upload
            s3_params = {
                'Bucket': BUCKET_NAME,
                'Key': file_name,  # The file name in S3
                'Body': file_content,  # The binary image data
                'ContentType': 'image/jpeg',  # Content type for the image
            }

            # Upload the image to S3
            s3.put_object(**s3_params)

            return {
                'statusCode': 200,
                'body': json.dumps(file_name)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'Error In that part uploading the image to S3: {str(e)}'})
            }
        except NoCredentialsError:
            return {
                'statusCode': 403,
                'body': json.dumps({'message': 'No credentials found for AWS S3.'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'message': f'Error saving the image to S3: {str(e)}'})
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'No image data found in the request body.'})
        }
    
