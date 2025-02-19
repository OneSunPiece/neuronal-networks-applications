# Libraries
import json
# ML Libraries
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import img_to_array
# Others
import numpy as np
from PIL import Image
import base64
import pickle
import boto3
import os
import io


S3_BUCKET: str = 'myawzbucket'

# Temporary paths to store files in the Lambda env
LAMBDA_PATH_MODEL:str = '/tmp/model_images.h5'
# S3 paths to store files in the Lambda env
S3_PATH_MODEL:str = 'images/model_images.h5'

# Initialize the S3 client
s3 = boto3.client('s3')

# global variables
global model
global status_error

def load_model_from_s3(lambda_path,s3_path)->None:
    """
    Load the model from S3 if it's not already loaded.
    return: model
    params: None
    raise: Exception if the model file does not exist in S3
    """
    global model

    # Check if the files exists
    if not os.path.exists(lambda_path):
        print("Downloading from S3...")
        print(f'{S3_BUCKET} --- {s3_path} --- {lambda_path}')
        s3.download_file(S3_BUCKET, s3_path, lambda_path)
        print("Model downloaded.")
    # Load the model
    model = tf.keras.models.load_model(lambda_path)
    print("Model loaded.")

def is_valid_data(input_data):
    """
    Validate the input data.
    return: True if the input is valid, else a JSON response with an error message
    params: input_data (list of numbers)
    raise: Exception if the input data is invalid
    """
    # Check if the input data is empty
    if not input_data:
        status_error = {
            'statusCode': 400,
            'body': json.dumps({'ERROR': 'Invalid input. No input data'})
        }
        return False
    else:
        status_error = None
        return True

def load_test_image():
    """
    Load the model from S3 if it's not already loaded.
    return: model
    params: None
    raise: Exception if the model file does not exist in S3
    """
    print("Downloading TEST IMAGE from S3...")
    s3.download_file(S3_BUCKET, 'images/pants.jpg', '/tmp/pants.jpg')
    print("Image downloaded.")
    img_path = '/tmp/pants.jpg'
    test_image = image.load_img(img_path, target_size=(244, 244))
    print("Image loaded.")

    return test_image

def import_model():
    """
    import the pickle files
    """
    global model
    with open(LAMBDA_PATH_MODEL, 'rb') as f:
        model = pickle.load(f)
    return model

def process_image(image_input):
    """
    Process the image to be used in the model.
    return: image_array
    params: image_path (str)
    raise: Exception if the image is not found
    """
    # Convert the image to an array
    # tf.keras.utils.img_to_array(img, data_format=None, dtype=None)

    img_array = img_to_array(image_input)
    # Expand the dimensions of the image
    img_array = np.expand_dims(img_array, axis=0)
    # Normalize the image
    img_array = img_array / 255.0
    return img_array

def make_prediction(img_array):
    # Diccionario de clases (ajusta según el orden de tu dataset)
    class_labels = ['jeans', 'sofa', 'tshirt', 'tv']
    # Realizar predicción
    predictions = model.predict(img_array)
    predicted_class = class_labels[np.argmax(predictions)]
    return predicted_class

def lambda_handler(event, _):
    """
    Lambda function handler.
    return: JSON response
    params: event (API Gateway input), context (Lambda context)
    raise: Exception if the input data is invalid or the model fails
    """
    global model
    global status_error

    class_labels = ['jeans', 'sofa', 'tshirt', 'tv']
    test_image = load_test_image()
    # Try to get the input data from the event
    try:
        print('Getting input data...')
        body = json.loads(event['body'])
        print('Extracting data...')
        input_data = body['data']
        image_bytes = base64.b64decode(input_data)
        # Convert to PIL image
        pil_image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(pil_image)

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'ERROR': 'Invalid input. No input data'})
        }

    try:
        print("Downloading model...")
        load_model_from_s3(LAMBDA_PATH_MODEL, S3_PATH_MODEL)
        # preprocesar la imagen
        print('Processing image...')
        print(test_image)
        img_array = process_image(test_image)
        # Realizar predicción
        print('Making prediction...')
        predictions = model.predict(img_array)
        predicted_class = class_labels[np.argmax(predictions)]
        print(f"Predicted class: {predicted_class}")

        return {
            'statusCode': 200,
            'body': json.dumps({'prediction': predicted_class})
        }
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': [json.dumps({'error': str(e)}), 'aaaaaa']
        }