import boto3
from botocore.exceptions import NoCredentialsError

def upload_file_to_s3(file_obj, filename, content_type):
    s3 = boto3.client(
        's3',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='us-east-2'  # pon tu región aquí
    )
    bucket_name = 'ceti360workq'

    try:
        s3.upload_fileobj(
            Fileobj=file_obj,
            Bucket=bucket_name,
            Key=filename,
            ExtraArgs={'ContentType': content_type}
        )
        # Construimos la URL pública del archivo (ajusta según tu bucket)
        url = f"https://{bucket_name}.s3.{s3.meta.region_name}.amazonaws.com/{filename}"
        return url
    except NoCredentialsError:
        raise Exception("Credenciales AWS no configuradas correctamente.")
