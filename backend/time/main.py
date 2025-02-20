import os
import pandas as pd
import numpy as np
import boto3
import json
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout # type: ignore

train_df = None
test_df = None
status_error = None

s3 = boto3.client('s3')

# Temporary paths to store files in the Lambda env
DATA_PATH_TRAIN:str = '/tmp/cleaned_data.csv'
DATA_PATH_TEST:str = '/tmp/cleaned_test_data.csv'
# S3 paths to store files in the Lambda env
S3_BUCKET: str = 'myawzbucket'
TRAIN_FILE_NAME:str = 'cleaned_data.csv'
TEST_FILE_NAME:str = 'cleaned_data.csv'

# Column names for the input data
DEPARTMENTS:list = [x for x in range(1, 4)]
SHOPS:list = [x for x in range(1, 4)]


INPUT_LEN:int = 2 # LEN of data input

def load_files_from_s3()->None:
    """
    Load the model from S3 if it's not already loaded.
    return: model
    params: None
    raise: Exception if the model file does not exist in S3
    """
    global train_df
    global test_df
    
    # If the model is already loaded, return it
    if train_df is not None and not train_df.empty and test_df is not None and not test_df.empty:
        print("Dataset already loaded.")
        return None

    # Check if the files exists
    if not os.path.exists(DATA_PATH_TRAIN):
        print("Downloading TRAIN dataset from S3...")
        s3.download_file(S3_BUCKET, TRAIN_FILE_NAME, DATA_PATH_TRAIN)
        print("Train dataset downloaded.")
    if not os.path.exists(DATA_PATH_TEST):
        print("Downloading TEST dataset from S3...")
        s3.download_file(S3_BUCKET, TEST_FILE_NAME, DATA_PATH_TEST)
    
    # If the file exist but is not loaded, load it
    if train_df is None:
        print("Loading train dataset...")
        train_df = pd.read_csv(DATA_PATH_TRAIN)
        train_df['Date'] = pd.to_datetime(train_df['Date'])
        train_df.sort_values('Date', inplace=True)
    if test_df is None:
        print("Loading test dataset...")
        test_df = pd.read_csv(DATA_PATH_TEST)
        test_df['Date'] = pd.to_datetime(test_df['Date'])
        test_df.sort_values('Date', inplace=True)
    
    print("All Loaded")

def is_valid_data(input_data):
    """
    Validate the input data.
    return: True if the input is valid, else a JSON response with an error message
    params: input_data (list of numbers)
    raise: Exception if the input data is invalid
    """
    global status_error
    # Check if the input data is a list
    if not input_data or not isinstance(input_data, list):
        status_error = {
            'statusCode': 400,
            'body': json.dumps({'ERROR': 'Invalid input. Provide a list for the input data.'})
        }
        return False
    # Check if the input data is empty
    if not input_data:
        status_error = {
            'statusCode': 400,
            'body': json.dumps({'ERROR': 'Invalid input. No input data'})
        }
        return False
    # Check if the input data has the correct length
    if len(input_data) != INPUT_LEN:
        status_error = {
            'statusCode': 400,
            'body': json.dumps({'ERROR': f'Invalid input. Provide a list of {INPUT_LEN} numbers in "data".'})
        }
        return False
    else:
        return True

# Cargar y preparar datasets
def load_data():
    df_train = pd.read_csv(DATA_PATH_TRAIN)
    
    df_test = pd.read_csv(DATA_PATH_TEST)

    return df_train, df_test

# Convertir la serie escalada en secuencias de ventanas (X, y)
def create_dataset(data, window_size=4):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size])
    return np.array(X), np.array(y)

# Construir y entrenar el modelo LSTM en los datos de entrenamiento
def build_and_train_model(train_data, window_size=4, epochs=50, batch_size=32):
    scaler = MinMaxScaler()
    sales = train_data['Weekly_Sales'].values.reshape(-1, 1)
    sales_scaled = scaler.fit_transform(sales)
    X, y_seq = create_dataset(sales_scaled, window_size)
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(window_size, 1)))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y_seq, epochs=epochs, batch_size=batch_size, verbose=0)
    return model, scaler, sales_scaled

# Obtener las fechas del primer mes de predicción a partir del test
def get_forecast_dates(test_data):
    test_data = test_data.copy()
    test_data.sort_values('Date', inplace=True)
    all_forecast_dates = test_data['Date'].reset_index(drop=True)
    first_forecast_date = all_forecast_dates.iloc[0]
    mask_first_month = (all_forecast_dates.dt.month == first_forecast_date.month) & (all_forecast_dates.dt.year == first_forecast_date.year)
    forecast_dates_first_month = all_forecast_dates[mask_first_month].reset_index(drop=True)
    print(f"First forecast month: {forecast_dates_first_month.iloc[0]}")
    return forecast_dates_first_month

# Obtener los últimos días reales del conjunto de entrenamiento
def get_actual_last(train_data, days=120):
    last_train_date = train_data['Date'].max()
    start_date = last_train_date - pd.Timedelta(days=days)
    actual_last = train_data[train_data['Date'] >= start_date][['Date', 'Weekly_Sales']].copy()
    actual_last.rename(columns={'Weekly_Sales': 'Sales'}, inplace=True)
    return actual_last

# Función para generar predicciones in-sample en el conjunto de entrenamiento
def forecast_on_train(model, scaler, sales_scaled, window_size=4):
    predictions = []
    for i in range(window_size, len(sales_scaled)):
        input_seq = sales_scaled[i-window_size:i].reshape(1, window_size, 1)
        pred_scaled = model.predict(input_seq, verbose=0)
        predictions.append(pred_scaled[0, 0])
    predictions = np.array(predictions).reshape(-1, 1)
    predictions_inverted = scaler.inverse_transform(predictions)
    return predictions_inverted

# Realizar la predicción recursiva de los siguientes períodos
def forecast_series(model, scaler, sales_scaled, window_size=4, n_forecast=30):
    current_sequence = sales_scaled[-window_size:].copy()
    forecast_scaled = []

    for _ in range(n_forecast):
        input_seq = current_sequence.reshape(1, window_size, 1)
        pred_scaled = model.predict(input_seq, verbose=0)
        forecast_scaled.append(pred_scaled[0, 0])

        # Actualizar la secuencia: eliminar el primer valor e incluir la predicción
        current_sequence = np.append(current_sequence[1:], [[pred_scaled[0, 0]]], axis=0)

    forecast_full = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1, 1))
    return forecast_full

#

def build_and_train_model(train_data, window_size=4, epochs=50, batch_size=32):
    # Escalar la variable 'Weekly_Sales'
    scaler = MinMaxScaler()
    sales = train_data['Weekly_Sales'].values.reshape(-1, 1)
    sales_scaled = scaler.fit_transform(sales)

    # Crear dataset para entrenar el modelo
    X, y_seq = create_dataset(sales_scaled, window_size)

    # Definir el modelo LSTM
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(window_size, 1)))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # Entrenar el modelo
    model.fit(X, y_seq, epochs=epochs, batch_size=batch_size, verbose=0)

    return model, scaler, sales_scaled


def process_forecast(store, dept, df_train, df_test, window_size=4, n_forecast=30):
    # Filtrar datos de train para la tienda y dept especificados
    train_data = df_train[(df_train['Store'] == store) & (df_train['Dept'] == dept)].copy()
    train_data.sort_values('Date', inplace=True)

    # Verificar que haya suficientes datos para entrenar
    if len(train_data) < window_size + 1:
        print(f"Datos insuficientes para Store {store} Dept {dept}.")
        return None, None

    # Entrenar el modelo
    model, scaler, sales_scaled = build_and_train_model(train_data, window_size=window_size)

    # Realizar la predicción recursiva de n_forecast períodos
    forecast_full = forecast_series(model, scaler, sales_scaled, window_size=window_size, n_forecast=n_forecast)

    # Obtener los últimos 120 días reales del train
    actual_last = get_actual_last(train_data, days=120)
    
    # Obtener las fechas del primer mes predicho a partir del test
    forecast_dates_first_month = add_weekly_forecast(actual_last, forecast_full)
    #print(f'forecast_dates_first_month:\n {forecast_dates_first_month}')
    #n_first_month = len(forecast_dates_first_month)

    #  guardar el gráfico
    # plot_forecast(actual_last, forecast_df, store, dept, forecast_color='tab:green')
    
    return forecast_dates_first_month

def add_weekly_forecast(df, forecast_sales):
    """
    Añade una lista de valores de ventas al DataFrame con las siguientes 5 fechas semanales.
    
    :param df: DataFrame con columnas 'Date' y 'Sales'
    :param forecast_sales: Lista de valores de ventas a añadir
    :return: DataFrame actualizado con las nuevas fechas y valores de ventas
    """
    if 'Date' not in df.columns or 'Sales' not in df.columns:
        raise ValueError("El DataFrame debe contener las columnas 'Date' y 'Sales'")
    # truncar los primeros 5 valores de forecast_sales
    forecast_sales = forecast_sales[:5]
    print(f'forecast_sales {forecast_sales}')
    
    # Obtener la última fecha del DataFrame
    last_date = df['Date'].max()
    
    # Generar las siguientes 5 fechas semanales
    new_dates = [last_date + pd.Timedelta(weeks=i) for i in range(1, 6)]
    
    # Crear un DataFrame con las nuevas fechas y valores de ventas
    new_data = pd.DataFrame({
        'Date': new_dates,
        'Sales': forecast_sales.flatten()
    })
    #print(f'new_data {new_data}')
    # Concatenar el DataFrame original con el nuevo DataFrame
    updated_df = pd.concat([df, new_data], ignore_index=True)
    
    return updated_df

def lambda_handler(event, _):
    """
    Lambda function handler.
    return: JSON response
    params: event (API Gateway input), context (Lambda context)
    raise: Exception if the input data is invalid or the model fails
    """
    global train_df
    global test_df
    global status_error

    # Set the window size and number of forecast periods
    window_size = 4
    n_forecast = 30

    try:
        body = event.get("body")
        if body:
            # Parse the JSON string
            parsed_body = json.loads(body)
            # Access the "features" key inside "data"
            input_data = parsed_body.get("data")
            # Get the type and length of the input data
            type_data = type(input_data)
            input_items = len(input_data)
            # Debugging logs
            print(f'Input Data: {str(input_data)}')
            print(f'Type: {type_data}')
            print(f'Length: {input_items}')
        
        # Validate input
        if is_valid_data(input_data):
            # get the dept and store values from the input
            print('Processing data...')
            dept = int(input_data[0])
            store = int(input_data[1])

            # Load the DATA if not already loaded
            print('Loading files...')
            load_files_from_s3()

            # Make the forecast
            print('Making forecast...')
            forecasted_serie = process_forecast(store, dept, train_df, test_df, window_size=window_size, n_forecast=n_forecast)
            print(f"Train Predictions: {forecasted_serie}")
            
            # Transform the Date column to string
            forecasted_serie["Date"] = forecasted_serie["Date"].astype(str)
            # Convert the DataFrame to a list of dictionaries
            json_response = forecasted_serie.to_dict(orient="records")
            # Return the prediction
            return {
                'statusCode': 200,
                'body': json.dumps({'prediction': json_response})
            }
        else:
            return status_error
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': [json.dumps({'error': str(e)}), input_data]
        }