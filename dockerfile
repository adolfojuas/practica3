# Imagen base con Python
FROM python:3.10

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Streamlit
EXPOSE 8080

# Ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
