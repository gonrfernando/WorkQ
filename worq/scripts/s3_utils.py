import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def upload_file_to_s3(file_obj, filename, content_type):
    s3 = boto3.client(
        's3',
        #aws_access_key_id='',
        #aws_secret_access_key='',
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
    
def delete_file_from_s3(filename):
    s3 = boto3.client(
        's3',
        #aws_access_key_id='',
        #aws_secret_access_key='',
        region_name='us-east-2'
    )
    bucket_name = 'ceti360workq'

    try:
        s3.delete_object(Bucket=bucket_name, Key=filename)
        return True
    except ClientError as e:
        print(f"Error al eliminar archivo de S3: {e}")
        return False

def generate_presigned_url(filename, expiration=3600):
    s3 = boto3.client(
        's3',
        #aws_access_key_id='',
        #aws_secret_access_key='',
        region_name='us-east-2'
    )
    bucket_name = 'ceti360workq'

    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        raise Exception(f"Error generating presigned URL: {str(e)}")
