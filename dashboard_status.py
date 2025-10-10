# =====Dashboard para vizualizar estados del servidos =====

#Importamos las librerías necesarias
import streamlit as st
import boto3
import pandas as pd
import json
from io import StringIO
import plotly.express as px

# ===== Configuración de la pagina =====
st.set_page_config(page_title = "Dashboard para visualizar estados del servidor", 
                   page_icon = "📄",
                   layout = "wide"
                  )

s3 = boto3.client("s3")

# =====Lógica para traer los datos =====
def actualizar():
    bucket_name = "xideralaws-curso-benjamin2"
    prefix = "raw/"
    response = s3.list_objects_v2(Bucket=bucket_name , Prefix=prefix)
    data_frames = []

    for obj in response["Contents"]:
        #Le pasamos lo que ya teníamos
        bucket_name = "xideralaws-curso-benjamin2"
        prefix = "raw/"

        response = s3.list_objects_v2(Bucket=bucket_name , Prefix=prefix)
        
        data_frames = []

        #Si no hay contenido
        if 'Contents' not in response:
            #Solo devuelve el Data Frame vacío
            return pd.DataFrame()

        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".json"):
                file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                content = file_obj["Body"].read().decode("utf-8")
                json_data = json.loads(content)
                df_temp = pd.json_normalize(json_data)
                data_frames.append(df_temp)
                
        if not data_frames:
            return pd.DataFrame()
        
        df = pd.concat(data_frames , ignore_index=True)
        
        # Hacemos la transformación de la fecha aquí mismo
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

# ===== Pagina Principal =====
st.title("Dashboard para visualizar estados del servidor ✅")

#Llamamos a la función para actualizar  los datos más recientes
df = actualizar()

#===== Análisis de los datos ====
st.header("Análisis de Estatus por Servidor")

if df.empty:
    st.warning("No hay datos disponibles para mostrar.")
else:
    #Aquí agrupamos por servidor, status y contamos
    #Agrupa por server y status
    #Guárdalo en al variable status_counts
    #.size dime cuantos elementos hay
    #.reset_index resetea y organiza en una tabla con una tercera columna "count"
    status_counts = df.groupby(["server_id", "status"]).size().reset_index(name="count")
    
    #Reorganizamos la tabla
    #server_id => filas
    #status => columnas
    #count => valores
    pivoted_df = status_counts.pivot_table(
        index="server_id",
        columns="status",
        values="count",
        fill_value=0
    )
    
st.write("Tabla de Resumen")
st.dataframe(pivoted_df)

st.write("Gráfico de Barras")
st.bar_chart(pivoted_df)

# ===== Como practica agrego una gráfica de pastel
#primero separamos las gráficas 
st.markdown("---")

# ===== Sección de la gráfica de pastel =====
st.header("Distribución general de los servidores")

#Contamos el total de status para cada tipo
#del dt secciona toma la columna 'status'
#Cuenta lo valores y guárdalos en una variables total_status_counts
total_status_counts = df['status'].value_counts()

#Creamos la figura de pastel
fig_pie = px.pie(
    total_status_counts,
    values=total_status_counts.values,
    names=total_status_counts.index,
    title="Distribución total de estados de los servidores"
)

#Mostramos la figura
st.plotly_chart(fig_pie)

#Un botoncito para darle presentación
if st.button('Refrescar Datos 🔄'):
    pass
        