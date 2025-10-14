#Importamos las librerías necesarias 
import json
import boto3
import pandas as pd
from io import StringIO
import mysql.connector

# =====Conexiones a s3  =====
#Nos conectamos a s3
s3_client = boto3.client('s3')
#Configuración del destino 
TARGET_BUCKET = 'xideralaws-curso-alan'
TARGET_PREFIX = 'processed/reports_data_base'

""" Nos conectamos a base de datos
Usamos Variables de Entorno para darle dinamismo 
=====ADVERTENCIA=====
Para esta lambda no se usa AWS Secret Manager pero se agrega una guía para su implementación en GitHub """
DB_HOST = 'database-1.cd8w4cuu6a79.us-west-1.rds.amazonaws.com'
DB_USER = 'admin'
DB_PASSWORD = 'admin123123'
DB_NAME = 'awsdata'
DB_PORT = 3306

#Definimos las Consultas que haremos de la base de datos (Se guardan en un diccionario (Clave, valor))
#Clave => archivo para crear
#Valor => Consulta a ejecutar
#Para mayor legibilidad del coligo las queries de mas de una linea se ponen entre ("""") 
queries_to_run = {
    "todos_los_pedidos.csv": "SELECT * FROM pedidos;",
    "todos_los_clientes.csv": "SELECT * FROM clientes;",
    
    "gastos_totales_por_cliente.csv": """
        SELECT c.nombre, sum(p.total) AS total_pagado
        FROM clientes c
        JOIN pedidos p ON c.id = p.cliente_id
        GROUP BY c.id, c.nombre
        ORDER BY total_pagado DESC;
    """,
    
    "pedidos_por_fecha_unica.csv": """
        SELECT p.*, c.nombre AS nombre_cliente
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        WHERE p.fecha = '2025-08-15';
    """,
    
    "top_5_clientes_con_mas_gastos.csv": """
        SELECT c.nombre, SUM(p.total) AS total_gastado
        FROM clientes c
        JOIN pedidos p ON c.id = p.cliente_id
        GROUP BY c.id, c.nombre
        ORDER BY total_gastado DESC
        LIMIT 5;
    """,
    
    "promedio_compra_por_cliente.csv": """
        SELECT c.nombre, ROUND(AVG(p.total), 2) AS promedio_compra
        FROM clientes c
        JOIN pedidos p ON c.id = p.cliente_id
        GROUP BY c.id, c.nombre
        ORDER BY promedio_compra DESC;
    """,
    
    "ventas_totales_por_ciudad.csv": """
        SELECT c.cuidad, SUM(p.total) AS ventas_totales
        FROM clientes c
        JOIN pedidos p ON c.id = p.cliente_id
        GROUP BY c.cuidad
        ORDER BY ventas_totales DESC;
    """
}

def lambda_handler(event, context):
    connection = None
    #Generamos una lista para registrar los archivos creados
    files_created = []
    
    try:
        #Nos conectamos a la base de datos con mysql-connector
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            #Establecemos un tiempo de espera para lograr la conexión (en segundos)
            connect_timeout=10
        )
        
        #Como guardamos las queries en un diccionario, hay que iterar para ejecutarlas
        for filename, sql_query in queries_to_run.items():
            #Ejecutamos la consulta y guardamos en un Data Frame
            df = pd.read_sql_query(sql_query, connection)
            
            #Convertimos el DAta Frame en un CSV en memoria con StringIO
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            
            #Armamos la ruta completa a donde irán los archivos
            target_key = f"{TARGET_PREFIX}/{filename}"
            
            #Finalmente subimos el archivo a S3"
            s3_client.put_object(
                Bucket=TARGET_BUCKET,
                Key=target_key,
                Body=csv_buffer.getvalue()
            )
            
        # 3. Devolvemos un resumen de lo que hace lambda
        final_message = f"Proceso completado. Se crearon {len(files_created)} reportes."
        print(final_message)
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": final_message,
                "files_created": files_created
            })
        }
        
    except Exception as e:
        # Este error captura fallos en la conexión a la base de datos.
        error_message = f"Error Crítico - No se pudo conectar a la base de datos o fallo general: {e}"
        print(error_message)
        raise e
    
    finally:
        # 4. Cerramos la conexión al final de toda la ejecución.
        if connection and connection.is_connected():
            connection.close()
            print("Conexión a la base de datos cerrada.")




