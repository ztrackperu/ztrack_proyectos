# Usar la imagen oficial de Python 3.13 como base
FROM python:3.13-slim

# Instalar las dependencias necesarias para psycopg2 (si usas PostgreSQL)
#RUN apt-get update && apt-get install -y \
RUN apt-get clean && apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear un directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos al contenedor
COPY requirements.txt /app/

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
#COPY . /app/

# Copiar el código de la aplicación (debe estar en ./app)
#COPY ./app /app/

# Exponer el puerto en el que FastAPI correrá
EXPOSE 8000

# Ejecutar FastAPI usando Uvicorn
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#archivo main afuera de la carpeta app
#CMD ["uvicorn", "app/server/app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#CMD ["uvicorn", "app/server/app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["python", "app/main.py"]


