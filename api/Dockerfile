# Usamos una imagen base ligera de Python
FROM python:3.11-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos los archivos de dependencias y la API
COPY requirements.txt .
COPY main.py .

# Instalamos las dependencias sin cache para mantener la imagen ligera
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto 8080 (Cloud Run asignará la variable PORT)
EXPOSE 8080

# Comando para iniciar la API
CMD ["python", "main.py"]
