#Lambda para leer y limpiar los datos desde el CSV Crudo

#Importamos las librerías necesarias 
import awswrangler as wr
import pandas as pd
import unicodedata
import re
#Para nombres con espacios o caracteres especiales 
import urllib.parse

""" Función super limpiadora universal marca sin registrar"""

def limpieza_universal(texto):
    #Validamos que recibimos texto
    if not isinstance(texto, str):
        return ""
    #Descubrí que varios datos tienen una mala codificación (Principalmente las lineas de metro)
    #Hay que forzar una compatibilidad con utf-8
    try: 
        texto = texto.encode('latin1').decode('utf-8' , errors='ignore')
    except: 
        pass
    #Descomponemos los caracteres con acento
    texto =unicodedata.normalize('NFD', texto)
    #Como necesitamos texto plano, sin acentos, quitamos todo lo que no forme parte de ASCII
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    #Transformamos todas las mayúsculas posibles a minúsculas
    texto = texto.lower()
    #Normalizamos el texto proveniente de malas codificaciones 
    texto = re.sub(r'l[aeiou]*[^a-z0-9\s]*nea', 'linea', texto, flags=re.IGNORECASE)
    #Quitamos los guiones ( - , _  ) y lo remplazamos por un espacio 
    texto = re.sub(r'[-_]', ' ', texto)
    #Quitamos espacios incensarios (doble espacio, espacio inicial o final)
    texto = re.sub(r'\s+', ' ', texto).strip()
    #Devolvemos el texto limpio
    return texto

""" Ahora normalizamos las lineas, ya que por malas codificaciones y guardado
estas lineas se muestras erróneamente en el dashboard, para evitar eso, las normalizamos
"""

def normalizar_lineas(texto):
    #Al texto le aplicamos nuestro super limpiador universal 
    texto = limpieza_universal(texto)
    #Creamos un diccionario de las correcciones que queremos 
    correcciones = {
        'linea 12' : 'linea 12' , 'linea 1' : 'linea 1' , 'linea 2': 'linea 2',
        'linea 3': 'linea 3', 'linea 4': 'linea 4', 'linea 5' : 'linea 5',
        'linea 6': 'linea 6', 'linea 7': 'linea 7', 'linea 8': 'linea 8',
        'linea 9': 'linea 9', 'linea a': 'linea a', 'linea b': 'linea b',  
    }
    #Ahora iteramos sobre el diccionario
    for patron, valor_correcto in correcciones.items():
        #Verifica Si el patron de cadena esta dentro del texto
        #Usamos \b para evitar que linea 12 == linea 1
        if re.search(r'\b' + re.escape(patron) + r'\b', texto):
            #Si coincide devuelve el valor corregido
            return valor_correcto
    return texto


""" Aquí va la función principal Lambda AWS """
def lambda_handler(event, context):
    """ Primero hay que saber si hay nuevos datos del CSV Crudo """
    
    #Trigger manual para disparar la lambda cuando se actualizan los datos del bucket
    #s3 manda un aviso (event) cuando se suben cosas al bucket
    #Podemos decir que va a este registro (el primero) y preguntamos en que bucket esta la alerta
    bucket_origen = event['Records'][0]['s3']['bucket']['name']
    #Ahora dime como se llama el archivo y codificalo correctamente 
    nombre_archivo_carpeta = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    #finalmente acama la ruta completa del archivo 
    ruta_origen = f's3://{bucket_origen}/{nombre_archivo_carpeta}'
    print(f'Se detecto un nuevo archivo en {ruta_origen}')
    
    """ Ya que encontramos los datos ahora si los extraemos  """
    #La librería awswrangler nos facilita la conexión a s3,
    try:
        #lee el CSV de s3 y conviértelo en un DataFrame de Pandas
        df = wr.s3.read_csv(path=ruta_origen, encoding='latin1')
        
        """ Ya tenemos los datos, ahora los transformamos """
        #Pero UPS, recuerda que tu csv provienen de la CDMX, hay que limpiarlos
        print('Limpiando los datos...')
        df.columns = [limpieza_universal(col) for col in df.columns]
        
        #Estas son las columnas conflictivas
        if 'linea' in df.columns: df ['linea'] = df['linea'].apply(normalizar_lineas)
        if 'estacion' in df.columns: df['estacion'] = df['estacion'].apply(limpieza_universal)
        if 'tipo_pago' in df.columns: df['tipo_pago'] = df['tipo_pago'].apply(limpieza_universal)

        df['fecha'] = pd.to_datetime(df['fecha'], errors = 'coerce')
        #Nos aseguramos de trabajar con valores numéricos y que no tenga valores vacíos en la columna (afluencia)
        df['afluencia'] = pd.to_numeric(df['afluencia'], errors = 'coerce').fillna(0).astype(int)
        df.dropna(subset = ['fecha'], inplace = True)

        #En el Kpi necesitamos separar la fecha por mes y por anio y dia de la semana
        df['anio'] = df['fecha'].dt.year
        df['mes'] = df['fecha'].dt.month
        try:
        #Por temas del idioma o del servidor, locale del day_name puede devolver los días en ingles
        #Para evitar eso, guardamos los días traducidos en un diccionario para que se vean en espanol en el dashboard
            df['dia_semana'] = df['fecha'].dt.day_name(locale = 'es_ES.UTF-8')
        except Exception as e:
            print(f"  ⚠️ Locale 'es_ES.UTF-8' no disponible ({e}). Usando inglés y traduciendo.")
            #Si no funciona toca hacerlo manualmente
            df ['dia_semana_ingles'] = df['fecha'].dt.day_name()
            dias_traduccion = {
                'monday': 'Lunes' , 'tuesday' : 'Martes' , 'wednesday' : 'Miercoles',
                'thursday' : 'Jueves' , 'friday' : 'Viernes' , 'saturday' : 'Sabado',
                'sunday' : 'Domingo'
            }
            # Convertimos a minúsculas ANTES de mapear y asignamos a la columna final
            df['dia_semana'] = df['dia_semana_ingles'].str.lower().map(dias_traduccion)
            # Manejo de Nulos por si acaso: si algo no se mapeó, lo dejamos como 'Desconocido'
            df['dia_semana'].fillna('Desconocido', inplace=True)
            # Eliminamos la columna temporal en inglés
            df.drop(columns=['dia_semana_ingles'], inplace=True)
            print("  ✅ Columna 'dia_semana' creada por traducción.")
        
            
        """ Finalmente Cargamos los datos limpios en una carpeta intermedia"""
        #Definimos el nombre del bucket
        bucket_destino = 'xideralaws-curso-alan'
        #Definimos la ruta de destino
        carpeta_destino = 'metro-cleaned-data/'
        ruta_destino = f"s3://{bucket_destino}/{carpeta_destino}"
        
        """ Ahora guardamos nuestro Data Frame en formato Parquet en la ruta de destino """
        wr.s3.to_parquet(
            df = df,
            path = ruta_destino,
            dataset = True,
            mode = "overwrite"
        )
            
        print(f"✅ FIN: Proceso ETL completado exitosamente.")
        return {'statusCode': 200, 'body': 'ETL ejecutado con éxito!'}
        
    except Exception as e:
        print(f"❌ ERROR: El proceso falló. Causa: {e}")
        raise e    
