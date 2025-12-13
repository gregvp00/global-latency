# Usamos una imagen base ligera de Python (Linux Debian)
FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# IMPORTANTE: Instalamos 'iputils-ping' porque la imagen minimalista de Python 
# no trae el comando ping por defecto. También librerías para geopandas.
RUN apt-get update && apt-get install -y \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el script
COPY monitor.py .

# Comando por defecto al ejecutar el contenedor
CMD ["python", "monitor.py"]