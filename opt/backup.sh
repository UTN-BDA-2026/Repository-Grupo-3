#!/bin/bash

# 1. Obtener la ruta absoluta del directorio donde está guardado este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 2. Cargar las variables de entorno (apunta a la carpeta App de tu proyecto)
ENV_FILE="$DIR/../App/.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Error: No se encontró el archivo $ENV_FILE"
    exit 1
fi

# 3. Definir variables dinámicas
FECHA=$(date +%Y-%m-%d_%H-%M-%S)
DIRECTORIO_BACKUP="$DIR/backups_locales" # Se creará al lado del script
TEMP_DUMP="/tmp/salon_temp_dump.sql"
ARCHIVO_HASH="$DIRECTORIO_BACKUP/ultimo_hash.txt"
NOMBRE_ARCHIVO="salon_backup_$FECHA.sql.gz.enc"
RUTA_COMPLETA="$DIRECTORIO_BACKUP/$NOMBRE_ARCHIVO"

# Crear la carpeta de backups si no existe
mkdir -p "$DIRECTORIO_BACKUP"

# 4. Extraer la base de datos a un archivo temporal
echo "Extrayendo base de datos..."
docker exec salon_db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DEV_DB" > $TEMP_DUMP

# 5. Calcular el hash (Ignorando las líneas de comentarios)
HASH_ACTUAL=$(grep -v "^--" $TEMP_DUMP | md5sum | awk '{print $1}')

# 6. Leer el hash del backup anterior (si existe)
HASH_ANTERIOR=""
if [ -f "$ARCHIVO_HASH" ]; then
    HASH_ANTERIOR=$(cat "$ARCHIVO_HASH")
fi

# 7. Comparar hashes para ver si hubo cambios
if [ "$HASH_ACTUAL" == "$HASH_ANTERIOR" ]; then
    echo "No se detectaron cambios en la base de datos. Se omite el backup."
    rm $TEMP_DUMP
    exit 0
fi

echo "Cambios detectados. Procediendo con el cifrado..."

# 8. Comprimir y cifrar el archivo
gzip -c $TEMP_DUMP | openssl enc -aes-256-cbc -salt -pbkdf2 -pass pass:"$PASSWORD_CIFRADO" > $RUTA_COMPLETA

# 9. Subir a Google Drive usando Rclone
echo "Subiendo a Google Drive..."
rclone copy $RUTA_COMPLETA "$RCLONE_DESTINO"

# 10. Guardar el nuevo hash y Limpiar
echo $HASH_ACTUAL > $ARCHIVO_HASH
echo "Limpiando archivos antiguos..."
find "$DIRECTORIO_BACKUP" -type f -name "*.sql.gz.enc" -mtime +7 -exec rm {} \;
rm $TEMP_DUMP

echo "Proceso finalizado exitosamente."