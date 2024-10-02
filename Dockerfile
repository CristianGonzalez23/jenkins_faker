# Usar la imagen base de Python slim
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Actualizar el sistema e instalar dependencias
RUN apt-get update && \
    apt-get install -y python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copiar los archivos de la aplicación
COPY . .

# Crear un entorno virtual y activar, luego instalar las dependencias
RUN python3 -m venv venv && \
    ./venv/bin/pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["./venv/bin/python", "app.py"]
