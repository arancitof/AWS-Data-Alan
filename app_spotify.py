# ===== Dashboard para visualizar datos de Spotify
# Primero importamos las librerias necesarias para trabajar
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== Configuración de la página =====
st.set_page_config(page_title = "Dashboard de Canciones Populares en Spotify",
                   page_icon = "🎵",
                   layout = "wide"
                  )

# ===== Cargar los datos =====
@st.cache_data
def load_data():
    #Leemos el archivo CSV
    df = pd.read_csv("Popular_Spotify_Songs (1).csv" , encoding = "latin1")

    #Limpiamos los datos para evitar trabajar con campos vacios
    df.dropna(subset = ["track_name" , "artist(s)_name"], inplace = True)
    #Cambios los valores de la columna Streams a valores numericos
    df["streams"] = pd.to_numeric(df["streams"], errors = "coerce")
    #Si despues de este cambio hay valores nulos, los eliminamos
    df.dropna(subset=['streams'], inplace=True)
    #Hacemos lo mismo para la columna "in_shazam_charts"
    df['in_shazam_charts'] = df['in_shazam_charts'].str.replace(',', '', regex=False)
    df['in_shazam_charts'] = pd.to_numeric(df['in_shazam_charts'], errors='coerce').fillna(0)
    #De igual forma en la columna KEY (CC = Suposicion de que es Do natural)
    df['key'] = df['key'].fillna("CC")

    return df

df = load_data()

# ===== Barra de filtrado Lateral =====
st.sidebar.header("Filtros Interactivos")

# Filtro por año de lanzamiento
years = sorted(df['released_year'].unique(), reverse = True)
selected_year = st.sidebar.selectbox(
    "Selecciona un Año",
    options=years,
)

# Aplicar filtro de año al DataFrame
df_filtered_by_year = df[df['released_year'] == selected_year]

# ===== Construcción de la página principal =====
st.title("🎵 Dashboard de Canciones Populares de Spotify 🎵")
st.markdown(f"Análisis de las canciones más populares del año **{selected_year}**.")
st.markdown("---")

# ===== KPI-s (Indicadores Clave de Rendimiento) =====
if not df_filtered_by_year.empty:
    #Calculamos el número total de canciones
    total_songs = df_filtered_by_year.shape[0]
    #De esas canciones, sumamos todos los Streams
    total_streams = int(df_filtered_by_year['streams'].sum())

    #Creamos dos columnas
    col1, col2 =st.columns(2)
    col1.metric("Canciones en el Año", f"{total_songs}")
    col2.metric("Total de Streams", f"{total_streams / 1_000_000_000:.2f}B")
else:
    st.warning("No hay datos disponibles para el año seleccionado.")
st.markdown("---")

# ===== Aquí traigo los graficos que ya había hecho =====
st.header(f"Análisis detallado para {selected_year}")

#TOP 5 Artistas más escuchados
st.subheader(f"🏆 Top 5 Artistas más escuchados en {selected_year}")
if not df_filtered_by_year.empty:
    top_artists_year = df_filtered_by_year.groupby('artist(s)_name')['streams'].sum().nlargest(5)
    fig1 = px.bar(top_artists_year,
                  x=top_artists_year.values,
                  y=top_artists_year.index,
                  orientation='h',
                  labels={'x': 'Total de Streams', 'y':"Artista"},
                  text=top_artists_year.values,
                  color=top_artists_year.values,
                  color_continuous_scale=px.colors.sequential.Viridis)
    fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No hay artistas para mostrar para este año.")

col_growth, col_key = st.columns(2)

#Crecimiento del Artista más escuchado por año
with col_growth:
    st.subheader("📈 Crecimiento del Artista Top del Año")
    if not df_filtered_by_year.empty:
        # Cambiamos la logica para ahora encontrar el artista más escuchado de es año
        top_artist_in_year = df_filtered_by_year.groupby('artist(s)_name')['streams'].sum().idxmax()

        # Filtramos los datos de los últimos 10 años para ese artista
        ten_years_ago = df['released_year'].max() - 10
        artist_df_recent = df[(df['artist(s)_name'] == top_artist_in_year) & (df['released_year'] > ten_years_ago)]

        if not artist_df_recent.empty:
            streams_growth = artist_df_recent.groupby('released_year')['streams'].sum().sort_index()
            fig2 = px.line(streams_growth,
                           x=streams_growth.index,
                           y=streams_growth.values,
                           markers=True,
                           labels={'x': 'Años', 'y': 'Total de Streams'},
                           title=f'Evolución de Streams para: {top_artist_in_year}')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info(f"No hay datos de crecimiento para {top_artist_in_year} en los últimos 10 años.")
    else:
        st.info("Selecciona un año con datos para ver el crecimiento del artista.")

#Tonalidad Musical más exitosa
with col_key:
    st.subheader(f"🎶 Tonalidad más exitosa en {selected_year}")
    if not df_filtered_by_year.empty:
        #Ahora filtramos por año
        successful_keys_year = df_filtered_by_year.groupby('key')['streams'].sum().sort_values(ascending=False)

        fig3 = px.bar(successful_keys_year,
                      x=successful_keys_year.index,
                      y=successful_keys_year.values,
                      labels={'x': 'Tonalidad Musical (Key)', 'y': 'Total de Streams'},
                      color=successful_keys_year.values,
                      color_continuous_scale=px.colors.sequential.Plasma
                     )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No hay datos de tonalidad para este año.")


# ===== Tabla de datos adicionales de las canciones filtradas =====
if top_artist_in_year:
    st.subheader(f"💿 Detalle de Canciones de {top_artist_in_year} en {selected_year}")
    #Filtramos por el artistas más popular de ese año
    df_top_artist_details = df_filtered_by_year[df_filtered_by_year['artist(s)_name'] == top_artist_in_year]

    st.dataframe(df_top_artist_details[[
        'track_name', 'streams', 'danceability_%', 
        'valence_%', 'energy_%', 'key', 'mode'
    ]], height=300)
else:
    st.subheader(f"💿 Detalle de Canciones en {selected_year}")
    st.info("No hay un artista principal para mostrar detalles.")
   


    
    

    


