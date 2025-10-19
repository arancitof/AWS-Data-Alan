#Primero importamos todas las librerías
import awswrangler as wr
import pandas as pd

def lambda_handler(event, context):
    
    #Primero Extraemos los datos limpios del bucket
    bucket_origen = event['bucket']
    carpeta_origen = event['key_folder']
    ruta_origen = f's3://{bucket_origen}/{carpeta_origen}'
    
    print(f'Procesando archivos limpios del metro{ruta_origen}')
    
    try:
        #Leemos los archivos limpios desde nuestro parquet
        df = wr.s3.read_parquet(path = ruta_origen)
        
        #Definimos el bucket y la carpeta del destino de los KPI's
        bucket_destino = 'xideralaws-curso-alan'
        carpeta_destino = 'metro-kpi-data/'

        afluencia_total_general = int(df['afluencia'].sum())
        # Guardamos este número como un archivo JSON simple
        wr.s3.to_json(
            df=pd.DataFrame({'afluencia_total': [afluencia_total_general]}),
            path=f's3://{bucket_destino}/{carpeta_destino}kpi_afluencia_total.json',
            orient='records',
            # Se como un objeto JSON, no líneas separadas
            lines=False 
        )
        
        """ Para cada KPI agrupamos y transformamos para que Streamlite no tenga cardado esta parte """
        #KPI 1: Afluencia Total por línea del metro
        afluencia_linea = df.groupby('linea')['afluencia'].sum().sort_values(ascending = False).reset_index()
        #Guardamos el "Reporte" en s3
        wr.s3.to_parquet(
            df = afluencia_linea,
            path = f's3://{bucket_destino}/{carpeta_destino}kpi_afluencia_linea/',
            dataset = True,
            mode = 'overwrite'
        )
        
        #KPI 2: Top 10 de estaciones con mayor afluencia
        top_10_estaciones = df.groupby('estacion')['afluencia'].sum().nlargest(10).reset_index()
        #Guardamos en s3
        wr.s3.to_parquet(
            df = top_10_estaciones,
            path = f's3://{bucket_destino}/{carpeta_destino}kpi_top_10_estaciones/',
            dataset = True,
            mode = 'overwrite'
        )
        
        #KPI 3: Distribución por tipo de Pago
        tipo_pago_dist = df.groupby('tipo_pago')['afluencia'].sum().reset_index()
        wr.s3.to_parquet(
            df = tipo_pago_dist,
            path = f's3://{bucket_destino}/{carpeta_destino}kpi_tipo_pago_dist/',
            dataset = True,
            mode = 'overwrite'
        )
        
        #KPI 4: Afluencia Promedio por dia de la semana
        if 'dia_semana' in df.columns:
            kpi4_agg = df.groupby('dia_semana').agg(
                afluencia_total=('afluencia', 'sum'),
                num_registros=('afluencia', 'size') # 'size' cuenta todas las filas del grupo
            ).reset_index()
            
            # Renombramos la columna de suma para consistencia
            kpi4_agg.rename(columns={'afluencia_total': 'afluencia'}, inplace=True)
            wr.s3.to_parquet(
                df=kpi4_agg,
                path=f's3://{bucket_destino}/{carpeta_destino}kpi_promedio_dia_semana/',
                dataset=True,
                mode='overwrite'
            )

        # KPI 5 - Histórico Mensual TOTAL
        agg_hist_mes = df.groupby(['anio', 'mes'])['afluencia'].sum().reset_index()
        # Forma correcta de crear la columna de fecha
        date_components = agg_hist_mes[['anio', 'mes']].copy()
        date_components.rename(columns={'anio': 'year', 'mes': 'month'}, inplace=True)
        date_components['day'] = 1
        agg_hist_mes['fecha_mes'] = pd.to_datetime(date_components)
        
        wr.s3.to_parquet(
            df=agg_hist_mes,
            # Guardamos como archivo único
            path=f's3://{bucket_destino}/{carpeta_destino}kpi_historico_mensual.parquet',
        )
        
        print("\n Todos los KPIs han sido pre-calculados.")
        return {'statusCode': 200, 'body': 'Agregación ejecutada con éxito!'}
        
    except Exception as e:
        print(f"❌ ERROR (KPlambda): El proceso falló. Causa: {e}")
        raise e



