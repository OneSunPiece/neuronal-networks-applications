# Pronóstico de Ventas Semanales con LSTM

## Propósito del Desarrollo

Este proyecto tiene como objetivo desarrollar una solución de deep learning basada en redes LSTM para pronosticar las ventas semanales de forma granular (por tienda y departamento). El objetivo es predecir las ventas futuras y proporcionar información valiosa que facilite la toma de decisiones estratégicas en entornos comerciales.

## Análisis y Preprocesamiento de Datos

Antes de construir el modelo de pronóstico, se realizó un análisis exploratorio y un preprocesamiento exhaustivo en un notebook de Jupyter. Los pasos clave incluyen:

- **Integración de Datos**: Se combinaron múltiples datasets (por ejemplo, datos de entrenamiento, información de tiendas y características adicionales) en un único dataframe utilizando llaves comunes como `Store`, `Date` e `IsHoliday`.
- **Limpieza de Datos**: Se eliminaron registros inconsistentes (por ejemplo, ventas semanales negativas) y se trataron los valores nulos, en su mayoría reemplazándolos por 0.
- **Ingeniería de Características**: Se convirtieron las columnas de fecha a formato datetime y se extrajeron características temporales (año, mes, semana). Además, se crearon indicadores para los feriados, permitiendo capturar los efectos estacionales.
- **Análisis Exploratorio**: Se generaron visualizaciones y resúmenes estadísticos para comprender las tendencias, la estacionalidad y el impacto de los feriados en las ventas.

## Consumo del Modelo

El modelo se implementa en un script Python independiente, el cual encapsula todo el flujo de trabajo:

1. **Carga de Datos**: Lee los datos preprocesados de entrenamiento y prueba desde el directorio `data/processed/`.
2. **Entrenamiento del Modelo**: Se filtran los datos según la tienda y el departamento proporcionados, se escala la variable de ventas y se entrena un modelo LSTM.
3. **Pronóstico**:  
   - Se realizan predicciones recursivas para el primer mes (30 períodos) de forma out-of-sample.
   - Se generan también predicciones in-sample para evaluar el rendimiento del modelo en los datos de entrenamiento.
4. **Visualización**:  
   - Se genera un gráfico que muestra los últimos 120 días de ventas reales concatenados con el pronóstico del primer mes, con una línea de conexión para asegurar continuidad visual.
   - Se grafica, además, para cada punto del conjunto de entrenamiento la predicción in-sample (utilizando únicamente los datos previos), permitiendo comparar los valores reales con los predichos.
5. **Generación de Salidas**: Se guardan el gráfico y un archivo CSV con los datos combinados (reales y pronosticados) en la carpeta `forecast/`.

## Evaluación del Modelo

El script incluye funciones para evaluar el rendimiento del modelo utilizando diversas métricas:

- **RMSE (Root Mean Squared Error)**
- **MAE (Mean Absolute Error)**
- **R² (Coeficiente de Determinación)**
- **MedAE (Median Absolute Error)**
- **MAPE (Mean Absolute Percentage Error)**

Estas métricas se calculan utilizando una parte de los datos de entrenamiento (in-sample) para conocer la precisión y robustez del modelo.

## Requisitos

Las dependencias necesarias se encuentran listadas en el archivo `requirements.txt`. Para instalar todas las dependencias, ejecute:

```bash
pip install -r requirements.txt
```

## Ejemplo de Uso
Para ejecutar el modelo de pronóstico, se debe correr el script desde la línea de comandos. El script solicitará al usuario ingresar el número de tienda y el número de departamento. Por ejemplo:

```bash
$ python forecast_script.py
Ingrese el número de tienda: 1
Ingrese el número de departamento: 1
Guardado gráfico en: forecast/store_1_dept_1.png
Guardado dataframe en: forecast/store_1_dept_1.csv
Métricas de Evaluación:
 - RMSE: 1234.56
 - MAE: 789.01
 - R²: 0.85
 - MedAE: 678.90
 - MAPE: 12.34%
Guardado gráfico de predicciones in-sample en: forecast/train_in_sample_predictions.png
```

En este ejemplo, el script procesa los datos para la tienda 1 y el departamento 1, entrena el modelo LSTM, pronostica las ventas para el primer mes, evalúa el rendimiento del modelo y genera gráficos tanto de los pronósticos out-of-sample como de las predicciones in-sample.

