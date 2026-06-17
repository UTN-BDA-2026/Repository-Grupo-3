import io
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

# Inicializamos el cliente de S3 apuntando a Cloudflare R2
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    region_name='auto' # R2 no usa regiones específicas como AWS
)

def upload_file_to_r2(file, folder="uploads"):
    """
    Sube un archivo a Cloudflare R2 y retorna la URL pública.
    """
    try:
        # 1. Limpiamos el nombre original (quita espacios y caracteres raros)
        filename = secure_filename(file.filename)
        
        # 2. Generamos un nombre único para evitar que se sobreescriban archivos
        # Ejemplo: contratos/a1b2c3d4_contrato_juan.pdf
        unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"
        
        # 3. Subimos el archivo a la nube
        s3_client.upload_fileobj(
            file,
            os.getenv('R2_BUCKET_NAME'),
            unique_filename,
            # Esto es VITAL para que el navegador muestre las imágenes/PDFs 
            # en lugar de forzar su descarga automáticamente.
            ExtraArgs={"ContentType": file.content_type} 
        )
        
        # 4. Construimos la URL final que guardaremos en PostgreSQL
        public_url = f"{os.getenv('R2_PUBLIC_URL')}/{unique_filename}"
        
        return public_url

    except ClientError as e:
        print(f"Error crítico subiendo archivo a R2: {e}")
        return None
def upload_bytes_to_r2(file_bytes, filename, folder="contratos_definitivos"):
    """
    Sube un archivo a Cloudflare R2 directamente desde la memoria RAM (bytes).
    """
    try:
        # Generamos el nombre único
        unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"
        
        # Convertimos los bytes crudos en un "objeto tipo archivo" que S3 pueda entender
        file_obj = io.BytesIO(file_bytes)
        
        # Subimos a la nube
        s3_client.upload_fileobj(
            file_obj,
            os.getenv('R2_BUCKET_NAME'),
            unique_filename,
            ExtraArgs={"ContentType": "application/pdf"} 
        )
        
        # Retornamos la URL pública
        public_url = f"{os.getenv('R2_PUBLIC_URL')}/{unique_filename}"
        return public_url

    except Exception as e:
        print(f"Error crítico subiendo bytes a R2: {e}")
        return None