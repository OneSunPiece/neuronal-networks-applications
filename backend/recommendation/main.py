import pandas as pd
import pickle
import json
import boto3
import os

#global top_k_neighbors
#global name_to_idx_map
#global frame 
global status_error

S3_BUCKET: str = 'myawzbucket'

# TOP_NEIGHBORS
TOP_NEIGHBORS_PATH:str = '/tmp/top_k_neighbors.pkl'
# NAME_TO_IDX_MAP
NAME_TO_IDX_MAP_PATH:str = '/tmp/name_to_idx_map.pkl'
# FRAME
FRAME_PATH:str = '/tmp/frame.pkl'

# S3 paths 
TOP_NEIGHBORS_PATH_S3:str = 'recommendations/top_k_neighbors.pkl'
NAME_TO_IDX_MAP_PATH_S3:str = 'recommendations/name_to_idx_map.pkl'
FRAME_PATH_S3:str = 'recommendations/frame.pkl'

s3 = boto3.client('s3')

def is_valid_data(input_data):
    """
    Validate the input data.
    return: True if the input is valid, else a JSON response with an error message
    params: input_data (list of numbers)
    raise: Exception if the input data is invalid
    """

    # Check if the input data is a list
    if not input_data or not isinstance(input_data, str):
        status_error = {
            'statusCode': 400,
            'body': json.dumps({'ERROR': 'Invalid input. Provide an integer for the input data.'})
        }
        return False
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

def load_files_from_s3(lambda_path,s3_path)->None:
    """
    Load the model from S3 if it's not already loaded.
    return: model
    params: None
    raise: Exception if the model file does not exist in S3
    """
    
    # Check if the files exists
    if not os.path.exists(lambda_path):
        print("Downloading from S3...")
        print(f'{S3_BUCKET} --- {s3_path} --- {lambda_path}')
        s3.download_file(S3_BUCKET, s3_path, lambda_path)
        print("Files downloaded.")
    
    print("All Loaded in the lambda")

def import_files():
    """
    import the pickle files
    """

    with open('/tmp/top_k_neighbors.pkl', 'rb') as f:
        top_k_neighbors = pickle.load(f)
    with open('/tmp/name_to_idx_map.pkl', 'rb') as f:
        name_to_idx_map = pickle.load(f)
    with open('/tmp/frame.pkl', 'rb') as f:
        frame = pickle.load(f)
    return top_k_neighbors, name_to_idx_map, frame

def find_index_by_name(product_name,name_to_idx_map):

    return name_to_idx_map.get(product_name, -1)

def get_similar_products(product_query, name_to_idx_map,top_k_neighbors,frame, k=10):
    """
    1) Check the product_query 
    2) Retrieve the product index.
    3) Extract top-k neighbors.
    4) Return recommended items as a DataFrame.
    """
    idx = find_index_by_name(product_query,name_to_idx_map)
    
    if idx == -1:
        print(f"Product '{product_query}' not found in the dataset.")
        return pd.DataFrame()
    
    neighbors_indices = top_k_neighbors[idx][:k]
    
    rec_df = frame.iloc[neighbors_indices].copy()
    rec_df = rec_df[['manufacturer','name','ratings','no_of_ratings','discount_price','actual_price']]
    rec_df.reset_index(drop=True, inplace=True)
    return rec_df

def lambda_handler(event, context):
    global status_error
    try:
        body = event.get("body")
        if body:
            # Parse the JSON string
            print(f'Parsing stuff ::: {body}')
            parsed_body = json.loads(body)
            # Access the "features" key inside "data"
            print('Getting data')
            input_data = parsed_body.get("data")
            # Get the type and length of the input data
            print('Getting TYPES')
            type_data = type(input_data)
            # Debugging logs
            print(f'Input Data: {str(input_data)}')
            print(f'Type: {type_data}')
        
            # Validate input
            if is_valid_data(input_data):
                print('Valid Input')

                # Download the files from S3
                print("Downloading from S3...")
                load_files_from_s3(TOP_NEIGHBORS_PATH, TOP_NEIGHBORS_PATH_S3)
                load_files_from_s3(NAME_TO_IDX_MAP_PATH, NAME_TO_IDX_MAP_PATH_S3)
                load_files_from_s3(FRAME_PATH, FRAME_PATH_S3)
  

                # Get the ready to use data
                top_k_neighbors, name_to_idx_map, frame = import_files()
                print("Variables ready")

                # Put the number of the product here
                product = input_data
                #product = frame['name'].iloc[selected_product]
                print(f'Product: {product}')

                # Get recommended products
                recommended_product = get_similar_products(product, name_to_idx_map,top_k_neighbors, frame, k=10)

                # Convert the DataFrame to a list of dictionaries
                recommended_product_list = recommended_product.to_dict(orient='records')
                print(f'Recommended Product: {recommended_product_list}')

                return {
                    'statusCode': 200,
                    'body': json.dumps(recommended_product_list)
                }

            else:
                return status_error

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': [json.dumps({'error': str(e)}), 'Bad stuff happend :c']
        }