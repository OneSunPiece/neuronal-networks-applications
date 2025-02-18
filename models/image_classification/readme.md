# Sistema de Clasificación de imagenes

## Objetivo

En este módulo, se aborda el problema de la clasificación automática de productos de comercio electrónico a partir de imágenes. Específicamente, se busca entrenar un modelo de deep learning capaz de reconocer y clasificar imágenes de cuatro categorías de productos:

- **Jeans**
- **Sofás**
- **Camisetas (T-shirts)**
- **Televisores (TVs)**

El propósito  es desarrollar un modelo basado en una red neuronal convolucional preentrenada (MobileNetV2) para identificar correctamente la categoría de un producto a partir de su imagen. Esto permitirá automatizar la organización y etiquetado de productos en plataformas de e-commerce, mejorando la experiencia del usuario y optimizando procesos de inventario.

### Dataset:

El conjunto de datos contiene imágenes de televisores, sofás, jeans y camisetas. Son datos de imágenes sin procesar y no estructurados extraídos de sitios web en línea. Todas las imágenes provienen de diferentes sitios. También es posible encontrar algunas imágenes irrelevantes en los datos; por ejemplo, en el conjunto de datos de televisores, puede haber imágenes de controles remotos.
Puede ser descargado en el siguiente enlace: https://www.kaggle.com/datasets/sunnykusawa/ecommerce-products-image-dataset/data

## Preprocesamiento:
En el caso de la carpeta televisores tiene imágenes que no corresponden, como controles de televisor, circuitos integrados o series de televisión por lo que se ha procedido limpiando esa clase manualmente antes de empezar.

Al hacer el conteo de imagenes por categoria, se llegó a los siguientes resultados:

Clase jeans: 199 imágenes
Clase sofa: 199 imágenes
Clase tshirt: 199 imágenes
Clase tv: 151 imágenes

No se hace necesario balancear las clases, pero dado que cada una contiene un número limitado de imágenes se hace generación y aumentación de datos, permitiendo entrenar simulando variaciones reales de las imágenes

### Diseño del Modelo:

**Generador de Imágenes para Entrenamiento**

Se crea un generador de datos a partir de las imágenes almacenadas en el directorio del dataset, aplicando las transformaciones definidas previamente en ImageDataGenerator utilizando el 80% de los datos. En esta parte también se hace un poco de preprocesamiento dado en este punto se redimensionan todas las imágenes a  244x244

**Generador de Imágenes para Entrenamiento Validación**

Se crea un generador de datos de validación a partir de las imágenes almacenadas en el dataset, aplicando las mismas transformaciones definidas en ImageDataGenerator pero utilizando el 20% de los datos.

### Construcción del Modelo con MobileNetV2

Creamos un modelo de clasificación de imágenes utilizando MobileNetV2 como extractor de características, y añadimos capas densas para realizar la clasificación en 4 categorías.

### Compilación y Entrenamiento del Modelo

Compilamos y entrenamos el modelo utilizando la estrategia de aprendizaje transferido con MobileNetV2.

En este punto se usa el algoritmo adam de optimización, funció de pérdida usada en clasificación multiclase y se mide la optimicación del modelo. Establecemos como máximo 30 epoch pero utilizando early_stopping para que el modelo se detenga si no mejora despues de 5 epoch.

### Guardado  Una vez entrenado el modelo, realizamos dos pasos clave:

# Guardar el modelo para su uso futuro.

Se guarda en formato .h5 ya que permite almacenar la arquitectura, pesos y configuración de entrenamiento en un solo archivo. Siendo compatible con TensorFlow y Keras, facilitando su carga posterior sin necesidad de reentrenarlo.
Dicho modelo .h5 se encuentra adjunto en el repositorio.


  
