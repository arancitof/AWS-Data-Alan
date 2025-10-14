#Importamos las librerias necesarias
import json
import boto3
import pandas as pd
from io import StringIO

#Establecemos la conexión a s3 
s3_client = boto3.client('s3')
 
def lambda_handler(event, context):
    source_bucket = 'xideralaws-curso-benjamin2'
    target_bucket = 'xideralaws-curso-alan'
    source_prefix = 'raw/'
    #Nombramos la carpeta y el nombre del archivo CSV
    target_key = "processed/server_status.csv"


    #Aquí se leen los archivos desde el bucket de origen
    try:
        response = s3_client.list_objects_v2(Bucket=source_bucket, Prefix=source_prefix)
        if 'Contents' not in response:
            print('El bucket de origen esta vacío')
            return{'statusCode': 200, 'body': json.dumps('No hay archivos para procesar.')}

        all_objects = response['Contents']
    except Exception as e:
        print("Error al traer los objetos del bucket")
        raise e

    
    data_frames = []  
    #Toda la logica que ya teniamos
    for obj in all_objects:
        key = obj['Key']
        if key.endswith('.json'):
            try:
                file_obj = s3_client.get_object(Bucket=source_bucket, Key=key)
                content = file_obj['Body'].read().decode('utf-8')
                json_data = json.loads(content)
                df_temp = pd.json_normalize(json_data)
                data_frames.append(df_temp)
            except Exception as e:
                print(f"Advertencia: No se pudo procesar el archivo '{key}'. Error: {e}")
                continue

    #Combinamos los datos y los trasnformamos
    df = pd.concat(data_frames, ignore_index=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    #IMPORTANTE
    #Convertimos el DF a CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    #Guardamos el archivo al bucket de destino
    try:
        s3_client.put_object(
            Bucket=target_bucket,
            Key=target_key,
            Body=csv_buffer.getvalue()
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f'¡Éxito! Archivo guardado en s3://{target_bucket}/{target_key}')
        }
    except Exception as e:
        return {
            "status":"error",
            "message":str(e)
        }
 
