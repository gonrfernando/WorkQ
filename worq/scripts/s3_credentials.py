import boto3

def test_s3_connection():
    s3 = boto3.client(
        's3',
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='us-east-2'  # cambia por tu región
    )
    
    response = s3.list_buckets()
    print("Buckets disponibles:")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

if __name__ == '__main__':
    test_s3_connection()
