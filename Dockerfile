# Usa una imagen base de Python ligera
FROM python:3.9-slim

# Actualiza el sistema e instala rdiff-backup
RUN apt-get update && \
    apt-get install -y rdiff-backup && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Define rdiff-backup como comando por defecto
ENTRYPOINT ["rdiff-backup"]