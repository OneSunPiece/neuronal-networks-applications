import os
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, median_absolute_error, mean_absolute_percentage_error

# Crear carpeta para guardar resultados
os.makedirs('forecast', exist_ok=True)

# Cargar y preparar datasets
def load_data():
    df_train = pd.read_csv('data/processed/cleaned_data.csv')
    df_train['Date'] = pd.to_datetime(df_train['Date'])
    df_train.sort_values('Date', inplace=True)
    df_test = pd.read_csv('data/processed/cleaned_test_data.csv')
    df_test['Date'] = pd.to_datetime(df_test['Date'])
    df_test.sort_values('Date', inplace=True)
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

# Realizar la predicción recursiva de los siguientes períodos
def forecast_series(model, scaler, sales_scaled, window_size=4, n_forecast=30):
    current_sequence = sales_scaled[-window_size:].copy()
    forecast_scaled = []
    for _ in range(n_forecast):
        input_seq = current_sequence.reshape(1, window_size, 1)
        pred_scaled = model.predict(input_seq, verbose=0)
        forecast_scaled.append(pred_scaled[0, 0])
        current_sequence = np.append(current_sequence[1:], [[pred_scaled[0, 0]]], axis=0)
    forecast_full = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1, 1))
    return forecast_full

# Obtener las fechas del primer mes de predicción a partir del test
def get_forecast_dates(test_data):
    test_data = test_data.copy()
    test_data.sort_values('Date', inplace=True)
    all_forecast_dates = test_data['Date'].reset_index(drop=True)
    first_forecast_date = all_forecast_dates.iloc[0]
    mask_first_month = (all_forecast_dates.dt.month == first_forecast_date.month) & (all_forecast_dates.dt.year == first_forecast_date.year)
    forecast_dates_first_month = all_forecast_dates[mask_first_month].reset_index(drop=True)
    return forecast_dates_first_month

# Obtener los últimos días reales del conjunto de entrenamiento
def get_actual_last(train_data, days=120):
    last_train_date = train_data['Date'].max()
    start_date = last_train_date - pd.Timedelta(days=days)
    actual_last = train_data[train_data['Date'] >= start_date][['Date', 'Weekly_Sales']].copy()
    actual_last.rename(columns={'Weekly_Sales': 'Sales'}, inplace=True)
    return actual_last

# Graficar el forecast y guardar la imagen
def plot_forecast(actual_last, forecast_df, store, dept, forecast_color='tab:blue'):
    plt.figure(figsize=(12,6))
    plt.plot(actual_last['Date'], actual_last['Sales'], label='Ventas Reales (Últimos 120 días)', marker='o')
    plt.plot(forecast_df['Date'], forecast_df['Sales'], label='Pronóstico (Primer Mes Predicho)', marker='x', linestyle='--', color=forecast_color)
    if (not actual_last.empty) and (not forecast_df.empty):
        plt.plot([actual_last['Date'].iloc[-1], forecast_df['Date'].iloc[0]],
                 [actual_last['Sales'].iloc[-1], forecast_df['Sales'].iloc[0]],
                 linestyle='--', color=forecast_color)
    plt.title(f'Store {store} Dept {dept} - Forecast')
    plt.xlabel('Fecha')
    plt.ylabel('Weekly Sales')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_filename = f"forecast/store_{store}_dept_{dept}.png"
    plt.savefig(plot_filename)
    plt.close()
    return plot_filename

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

# Graficar las predicciones in-sample junto con los datos reales del entrenamiento
def plot_train_predictions(train_data, predictions, window_size=4):
    actual = train_data['Weekly_Sales'].values[window_size:]
    dates = train_data['Date'].values[window_size:]
    plt.figure(figsize=(12,6))
    plt.plot(train_data['Date'], train_data['Weekly_Sales'], label="Ventas Reales", marker='o', linestyle='-')
    plt.plot(dates, predictions, label="Predicción In-Sample", marker='x', linestyle='--')
    plt.title("Predicción In-Sample (Entrenamiento)")
    plt.xlabel("Fecha")
    plt.ylabel("Ventas Semanales")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plot_filename = "forecast/train_in_sample_predictions.png"
    plt.savefig(plot_filename)
    plt.close()
    print(f"Guardado gráfico de predicciones in-sample en: {plot_filename}")

# Procesar y generar el forecast para una tienda y departamento dados
def process_forecast(store, dept, df_train, df_test, window_size=4, n_forecast=30):
    train_data = df_train[(df_train['Store'] == store) & (df_train['Dept'] == dept)].copy()
    train_data.sort_values('Date', inplace=True)
    if len(train_data) < window_size + 1:
        print(f"Datos insuficientes para Store {store} Dept {dept}.")
        return None, None
    model, scaler, sales_scaled = build_and_train_model(train_data, window_size=window_size)
    forecast_full = forecast_series(model, scaler, sales_scaled, window_size=window_size, n_forecast=n_forecast)
    test_data = df_test[(df_test['Store'] == store) & (df_test['Dept'] == dept)].copy()
    test_data.sort_values('Date', inplace=True)
    if test_data.empty:
        print(f"No hay datos de test para Store {store} Dept {dept}.")
        return None, None
    forecast_dates_first_month = get_forecast_dates(test_data)
    n_first_month = len(forecast_dates_first_month)
    forecast_first_month = forecast_full[:n_first_month]
    forecast_df = pd.DataFrame({'Date': forecast_dates_first_month, 'Sales': forecast_first_month.flatten()})
    actual_last = get_actual_last(train_data, days=120)
    combined_df = pd.concat([actual_last, forecast_df], ignore_index=True)
    plot_filename = plot_forecast(actual_last, forecast_df, store, dept, forecast_color='tab:blue')
    csv_filename = f"forecast/store_{store}_dept_{dept}.csv"
    combined_df.to_csv(csv_filename, index=False)
    print(f"Guardado gráfico en: {plot_filename}")
    print(f"Guardado dataframe en: {csv_filename}")
    return combined_df, plot_filename

# Evaluar el modelo utilizando parte de los datos de entrenamiento (RMSE, MAE, R2, MedAE, MAPE)
def evaluate_model(train_data, window_size=4, n_forecast=30, epochs=50, batch_size=32):
    if len(train_data) < window_size + n_forecast:
        print("Datos insuficientes para evaluación.")
        return None
    train_train = train_data.iloc[:-(n_forecast)]
    eval_data = train_data.iloc[-(window_size+n_forecast):].copy()
    model, scaler, _ = build_and_train_model(train_train, window_size=window_size, epochs=epochs, batch_size=batch_size)
    sales_eval = eval_data['Weekly_Sales'].values.reshape(-1, 1)
    sales_scaled_eval = scaler.transform(sales_eval)
    forecast_scaled = []
    current_sequence = sales_scaled_eval[:window_size].copy()
    for _ in range(n_forecast):
        input_seq = current_sequence.reshape(1, window_size, 1)
        pred_scaled = model.predict(input_seq, verbose=0)
        forecast_scaled.append(pred_scaled[0, 0])
        current_sequence = np.append(current_sequence[1:], [[pred_scaled[0, 0]]], axis=0)
    forecast_eval = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1, 1))
    actual_eval = sales_eval[window_size:]
    mse = mean_squared_error(actual_eval, forecast_eval)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(actual_eval, forecast_eval)
    r2 = r2_score(actual_eval, forecast_eval)
    medae = median_absolute_error(actual_eval, forecast_eval)
    mape = mean_absolute_percentage_error(actual_eval, forecast_eval)
    return rmse, mae, r2, medae, mape

if __name__ == "__main__":
    window_size = 4
    n_forecast = 30
    store_input = input("Ingrese el número de tienda: ")
    dept_input = input("Ingrese el número de departamento: ")
    try:
        store = int(store_input)
        dept = int(dept_input)
    except ValueError:
        print("Entrada inválida. Se requieren números enteros.")
        exit(1)
    df_train, df_test = load_data()
    process_forecast(store, dept, df_train, df_test, window_size=window_size, n_forecast=n_forecast)
    train_data = df_train[(df_train['Store'] == store) & (df_train['Dept'] == dept)].copy()
    metrics = evaluate_model(train_data, window_size=window_size, n_forecast=n_forecast)
    if metrics is not None:
        rmse, mae, r2, medae, mape = metrics
        print("Métricas de Evaluación:")
        print(f" - RMSE: {rmse:.2f}")
        print(f" - MAE: {mae:.2f}")
        print(f" - R²: {r2:.2f}")
        print(f" - MedAE: {medae:.2f}")
        print(f" - MAPE: {mape*100:.2f}%")
        # Guardar métricas en CSV
        metrics_dict = {
            "Store": store,
            "Dept": dept,
            "RMSE": rmse,
            "MAE": mae,
            "R2": r2,
            "MedAE": medae,
            "MAPE": mape
        }
        metrics_df = pd.DataFrame([metrics_dict])
        metrics_csv_filename = f"forecast/metrics_store_{store}_dept_{dept}.csv"
        metrics_df.to_csv(metrics_csv_filename, index=False)
        print(f"Guardadas métricas en: {metrics_csv_filename}")
    # Generar y graficar predicciones in-sample para el conjunto de entrenamiento
    model, scaler, sales_scaled = build_and_train_model(train_data, window_size=window_size)
    train_predictions = forecast_on_train(model, scaler, sales_scaled, window_size=window_size)
    plot_train_predictions(train_data, train_predictions, window_size=window_size)
