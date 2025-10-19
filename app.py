
import io
import sys
import math
import numpy as np
import pandas as pd
import streamlit as st# ===== Dashboard para visualizar los datos limpios =====
#Importamos las librerias necesarias
import streamlit as st
import pandas as pd
import plotly.express as px
import awswrangler as wr


# =====> Configuración de la metaData de la Pagina <=====
st.set_page_config(
    page_title = 'Dashboard del Sistema de Transporte Colectivo (Metro CDMX)',
    page_icon = '🚇',
    layout = 'wide'
)

# =====> Titulo Principal del Dashboard <=====
st.title(' 🚇Dashboard del Sistema de Transporte Colectivo Metro-CDMX')
st.markdown('---')

# ===== > Datos de s3 necesarios <=====
BUCKET = 'xideralaws-curso-alan'
#Datos de la lambda
CARPETA_KPI = 'metro-kpi-data/'

# =====> Carga de los datos desde el archivo Parquet de datos limpios <=====
#Evitamos que Streamlit no recargue los datos cada vez
@st.cache_data
def cargar_kpis_desde_s3(bucket, carpeta_kpi):
    print (f"Cargando los KPIs desde s3://{bucket}/{carpeta_kpi}")
    kpis = {}
    kpi_paths = {
        'afluencia_total': f"s3://{bucket}/{carpeta_kpi}kpi_afluencia_total.json",
        'afluencia_linea': f"s3://{bucket}/{carpeta_kpi}kpi_afluencia_linea/",
        'top_10_estaciones': f"s3://{bucket}/{carpeta_kpi}kpi_top_10_estaciones/",
        'dist_pago': f"s3://{bucket}/{carpeta_kpi}kpi_tipo_pago_dist/",
        'promedio_dia': f"s3://{bucket}/{carpeta_kpi}kpi_promedio_dia_semana/",
        'historico': f"s3://{bucket}/{carpeta_kpi}kpi_historico_mensual.parquet" 
    }
    #Iteramos sobre el kpis_paths para cargar los kpis desde s3
    for name, path in kpi_paths.items():
        #Intentamos leer cada comprimido parquet
        try:
            if path.endswith('.json'):
                # Leemos el JSON simple para la afluencia total
                kpis[name] = wr.s3.read_json(path=path, orient='records')
            else:
                # Leemos los Parquet para los demás
                is_dataset = not path.endswith('.parquet')
                kpis[name] = wr.s3.read_parquet(path=path, dataset=is_dataset)
            
            print(f"  ✅ KPI Total '{name}' cargado.")
        except Exception as e:
            print(f"  ❌ ERROR al cargar KPI Total '{name}': {e}")
            kpis[name] = pd.DataFrame() if not path.endswith('.json') else pd.DataFrame([{'afluencia_total': 0}]) # Default para el total
            
    return kpis
        
        
#Llamamos a la funcion para cargar los datos 
kpis_totales = cargar_kpis_desde_s3(BUCKET, CARPETA_KPI)

# ===========> Cuerpo del Dashboard <=============
#Metricas Principales 
# =====> KPIS (Indicadores Clave de Desempeño) del Proyecto <=====
st.header('📊 Resumen General (Todo el Histórico)')

col1, col2, col3 = st.columns(3)
afluencia_total_general = kpis_totales.get('afluencia_total', pd.DataFrame([{'afluencia_total': 0}])).iloc[0]['afluencia_total']
col1.metric("Afluencia Total Histórica", f"{afluencia_total_general:,}")

# Promedio Diario (calculado desde el KPI 4 pre-calculado)
if not kpis_totales['promedio_dia'].empty and 'afluencia' in kpis_totales['promedio_dia'].columns and 'num_registros' in kpis_totales['promedio_dia'].columns:
    promedio_diario_general = int(kpis_totales['promedio_dia']['afluencia'].sum() / kpis_totales['promedio_dia']['num_registros'].sum())
    col2.metric("Promedio Diario General", f"{promedio_diario_general:,}")
else:
    col2.metric("Promedio Diario General", "N/A")

# Estación Top (del KPI 2 pre-calculado)
if not kpis_totales['top_10_estaciones'].empty:
    top_estacion_general = kpis_totales['top_10_estaciones'].iloc[0]['estacion']
    col3.metric("Estación Top Histórica", top_estacion_general.title())
else:
    col3.metric("Estación Top Histórica", "N/A")

st.markdown("---")
# =====> KPI 1: Afluencia Total por línea del metro <=====
st.header('📊 Afluencia Total (Todos los años)')

#Definimos los colores que tienen las lineas del METRO
if not kpis_totales['afluencia_linea'].empty:
    mapa_colores_lineas = {
        'linea 1': '#f56394',
        'linea 2': '#0064a8',
        'linea 3': '#ae9d27',
        'linea 4': '#6fb7ae',
        'linea 5': '#fddf00',
        'linea 6': '#ff1100',
        'linea 7': '#ff6309',
        'linea 8': '#018749',
        'linea 9': '#5b2c2a',
        'linea a': '#a3277c',
        'linea b': '#a8a8a8',
        'linea 12': '#b99e51',
    }
    #Uso una variable local para facilitar la claridad
    df_plot = kpis_totales['afluencia_linea']

    #Construimos la grafica
    fig_lineas = px.bar(
            kpis_totales['afluencia_linea'].sort_values('afluencia', ascending = False),
            x = 'linea' , 
            y = 'afluencia' , 
            title = 'Afluencia por Línea' , 
            text_auto = True, 
            color = 'linea',
            color_discrete_map = mapa_colores_lineas
        )
    fig_lineas.update_traces(texttemplate = '%{y: , .0f}')
    st.plotly_chart(fig_lineas, use_container_width = True)
else:
    st.warning("No se pudieron cargar los datos de Afluencia por Línea.")
st.markdown("---")

# =====> KPI 2: Top 10 de estaciones con mayor afluencia <=====
st.subheader('📈 Top 10 de Estaciones con Mayor Afluencia')
if not kpis_totales['top_10_estaciones'].empty:
    df_plot_top10 = kpis_totales['top_10_estaciones']
    #Construimos la grafica
    fig_top10 = px.bar(
        df_plot_top10.sort_values('afluencia'),
        y = 'estacion',
        x = 'afluencia',
        orientation = 'h',
        title = 'Top 10 de Estaciones con Mayor Afluencia',
        text_auto = True
        )
    fig_top10.update_traces(texttemplate = '%{x: , .0f}')
    fig_top10.update_layout(yaxis = { 'categoryorder': 'total ascending' })
    st.plotly_chart(fig_top10, use_container_width = True)
else:
    st.warning("No se pudieron cargar los datos del Top 10 de Estaciones.")
st.markdown("---")

# =====> KPI 3 y 4: Distribución por tipo de Pago, afluencia promedio <=====
col_kpi3, col_kpi4 = st.columns(2)
with col_kpi3:
    st.subheader(' 💳 Distribucion por tipo de pago')
    if not kpis_totales['dist_pago'].empty:
    #Construimos la grafica
        fig_pago_pie = px.pie(
            kpis_totales['dist_pago'],
            values = 'afluencia',
            names = 'tipo_pago',
            title = 'Distribución por Tipo de Pago',
            hole = 0.4,
        )
        fig_pago_pie.update_traces(
            textposition = 'inside',
            textinfo = 'percent + label',
            textfont = dict(size = 14)
        )
        fig_pago_pie.update_layout(
            height = 400
        )
        st.plotly_chart(fig_pago_pie , use_container_width = True)
    else:
        st.info("No hay datos de 'Tipo de Pago'.")
with col_kpi4:
    st.subheader("Promedio por Día de la Semana")
    if not kpis_totales['promedio_dia'].empty:
        df_plot_dia_agg = kpis_totales['promedio_dia']
        if 'afluencia' in df_plot_dia_agg.columns and 'num_registros' in df_plot_dia_agg.columns:
             df_plot_dia_agg['promedio'] = df_plot_dia_agg['afluencia'] / df_plot_dia_agg['num_registros']
             df_plot_dia = df_plot_dia_agg[['dia_semana', 'promedio']].rename(columns={'promedio':'afluencia'})
             orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
             df_plot_dia['dia_semana'] = pd.Categorical(df_plot_dia['dia_semana'], categories=orden_dias, ordered=True)
             fig_dias = px.bar(df_plot_dia.sort_values('dia_semana'), x='dia_semana', y='afluencia',
                               title="Promedio de Afluencia por Día", text_auto=True)
             fig_dias.update_traces(texttemplate='%{y:,.0f}')
             st.plotly_chart(fig_dias, use_container_width=True)
        else:
             st.warning("Faltan columnas para calcular el promedio por día.")
    else:
        st.info("No hay datos de 'Promedio por Día'.")
st.markdown("---")

# =====> KPI 5: Histórico <=====
st.subheader("Evolución Histórica de Afluencia Total (Mensual)")
if not kpis_totales['historico'].empty:
    df_hist_plot = kpis_totales['historico']
    df_hist_plot['fecha_mes'] = pd.to_datetime(df_hist_plot['fecha_mes'])
    
    # Filtro visual opcional para el histórico
    lista_anios_hist = sorted(df_hist_plot['anio'].unique(), reverse=True)
    anio_hist_sel = st.selectbox("Filtrar Histórico por Año:", options=['Todos'] + lista_anios_hist, key="filtro_hist")
    
    if anio_hist_sel != 'Todos':
         df_hist_plot = df_hist_plot[df_hist_plot['anio'] == anio_hist_sel]
    
    if not df_hist_plot.empty:
         fig_hist = px.line(df_hist_plot.sort_values('fecha_mes'), x='fecha_mes', y='afluencia', title='Afluencia Total Mensual', markers=True)
         fig_hist.update_layout(yaxis_title="Afluencia Total Mensual", xaxis_title="Mes")
         st.plotly_chart(fig_hist, use_container_width=True)
    else:
         st.info("No hay datos históricos para el año seleccionado.")
else:
    st.warning("No se pudo cargar el KPI histórico pre-calculado.")

#Prueba de Deploy continuo...
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional
 
st.set_page_config(page_title="Netflix Data Dashboard", layout="wide")
 
# ----------------------
# Helpers
# ----------------------
@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)
 
def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # release_year -> numeric
    if "release_year" in out.columns:
        out["release_year_num"] = pd.to_numeric(out["release_year"], errors="coerce")
    # duration -> numeric (minutes for Movies / seasons for TV Show)
    if "duration" in out.columns:
        extracted = out["duration"].astype(str).str.extract(r"(\d+)")[0]
        out["duration_num"] = pd.to_numeric(extracted, errors="coerce")
    return out
 
def count_by_year(df: pd.DataFrame, content_type: Optional[str] = None) -> pd.Series:
    q = df
    if content_type in ("Movie", "TV Show"):
        q = q[q["type"] == content_type]
    if "release_year_num" not in q.columns:
        return pd.Series(dtype="int64")
    return q["release_year_num"].dropna().astype(int).value_counts().sort_index()
 
# ----------------------
# Sidebar
# ----------------------
st.sidebar.title("🎛️ Controles")
 
uploaded = st.sidebar.file_uploader("Sube tu CSV de Netflix (Kaggle)", type=["csv"])
sample_notice = """
**Nota**: Este dashboard está pensado para el dataset de Kaggle (Netflix Movies and TV Shows). 
Si tu CSV tiene columnas diferentes, ajusta las opciones de columnas más abajo.
"""
st.sidebar.info(sample_notice, icon="ℹ️")
 
pairplot_rows = st.sidebar.slider("Límite de filas para Pairplot (muestra aleatoria)", 200, 5000, 1000, step=100)
show_reg = st.sidebar.checkbox("Agregar línea de regresión en scatter (regplot)", value=False)
content_filter = st.sidebar.selectbox("Filtrar por tipo", ["Todos", "Movie", "TV Show"])
 
# ----------------------
# Main
# ----------------------
st.title("📺 Netflix Data Dashboard")
 
if uploaded is None:
    st.warning("Sube un CSV para comenzar (por ejemplo, `netflix_titles.csv`).")
    st.stop()
 
try:
    data = load_csv(uploaded)
except Exception as e:
    st.error(f"No se pudo leer el CSV: {e}")
    st.stop()
 
# Column mapping helpers (in case user CSV differs slightly)
default_release_col = "release_year" if "release_year" in data.columns else None
default_duration_col = "duration" if "duration" in data.columns else None
default_type_col = "type" if "type" in data.columns else None
 
with st.expander("⚙️ Mapear columnas (opcional)", expanded=False):
    release_col = st.selectbox("Columna de año de estreno", [None] + list(data.columns), index=(list(data.columns).index(default_release_col)+1 if default_release_col in data.columns else 0))
    duration_col = st.selectbox("Columna de duración", [None] + list(data.columns), index=(list(data.columns).index(default_duration_col)+1 if default_duration_col in data.columns else 0))
    type_col = st.selectbox("Columna de tipo (Movie / TV Show)", [None] + list(data.columns), index=(list(data.columns).index(default_type_col)+1 if default_type_col in data.columns else 0))
 
# If user mapped different names, align to canonical ones
data = data.copy()
if release_col and release_col != "release_year":
    data["release_year"] = data[release_col]
if duration_col and duration_col != "duration":
    data["duration"] = data[duration_col]
if type_col and type_col != "type":
    data["type"] = data[type_col]
 
df = coerce_numeric_columns(data)
 
if content_filter in ("Movie", "TV Show") and "type" in df.columns:
    df_view = df[df["type"] == content_filter]
else:
    df_view = df
 
# ----------------------
# KPIs
# ----------------------
left, mid, right = st.columns(3)
with left:
    total = len(df_view)
    st.metric("Registros", f"{total:,}")
with mid:
    if "release_year_num" in df_view.columns:
        years = df_view["release_year_num"].dropna()
        if not years.empty:
            st.metric("Rango de años", f"{int(years.min())} — {int(years.max())}")
        else:
            st.metric("Rango de años", "N/D")
    else:
        st.metric("Rango de años", "N/D")
with right:
    if "duration_num" in df_view.columns:
        d = df_view["duration_num"].dropna()
        if not d.empty:
            st.metric("Duración/Temporadas (mediana)", f"{np.median(d):.0f}")
        else:
            st.metric("Duración/Temporadas (mediana)", "N/D")
    else:
        st.metric("Duración/Temporadas (mediana)", "N/D")
 
st.markdown("---")
 
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendencias", "🧪 Pairplot", "🔗 Correlaciones", "📊 Scatter"])
 
# ----------------------
# Tab 1: Trends
# ----------------------
with tab1:
    st.subheader("Títulos por año de estreno")
    counts = count_by_year(df_view, content_type=None if content_filter == "Todos" else content_filter)
    if counts.empty:
        st.info("No hay datos suficientes para esta vista.")
    else:
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(x=counts.index, y=counts.values, ax=ax)
        ax.set_xlabel("Año")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig, clear_figure=True)
 
# ----------------------
# Tab 2: Pairplot (numeric relations)
# ----------------------
with tab2:
    st.subheader("Relaciones entre columnas numéricas (pairplot)")
    numeric_cols = df_view.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.info("No hay columnas numéricas para mostrar. Asegúrate de haber convertido `release_year` y `duration`.")
    else:
        sel = st.multiselect("Selecciona columnas numéricas", numeric_cols, default=numeric_cols[:min(4,len(numeric_cols))])
        if len(sel) < 2:
            st.info("Selecciona al menos dos columnas.")
        else:
            # Sample to keep it lightweight
            plot_df = df_view[sel].dropna()
            if len(plot_df) > pairplot_rows:
                plot_df = plot_df.sample(pairplot_rows, random_state=42)
            with st.spinner("Generando pairplot..."):
                g = sns.pairplot(plot_df, diag_kind="hist")
                st.pyplot(g.fig, clear_figure=True)
 
# ----------------------
# Tab 3: Correlations
# ----------------------
with tab3:
    st.subheader("Matriz de correlación")
    numeric_df = df_view.select_dtypes(include="number").dropna(axis=1, how="all")
    if numeric_df.empty or numeric_df.shape[1] < 2:
        st.info("No hay suficientes columnas numéricas para calcular correlaciones.")
    else:
        corr = numeric_df.corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig, clear_figure=True)
 
# ----------------------
# Tab 4: Scatter / Regresiones
# ----------------------
with tab4:
    st.subheader("Relación con el año de estreno")
    if "release_year_num" not in df_view.columns:
        st.info("No existe `release_year_num`. Mapea y convierte primero la columna de año.")
    else:
        numeric_cols = [c for c in df_view.select_dtypes(include="number").columns if c != "release_year_num"]
        if not numeric_cols:
            st.info("No hay columnas numéricas para comparar.")
        else:
            ycol = st.selectbox("Variable numérica (Y)", numeric_cols, index=0)
            plot_df = df_view[["release_year_num", ycol]].dropna()
            if plot_df.empty:
                st.info("No hay datos suficientes para graficar.")
            else:
                fig, ax = plt.subplots(figsize=(10, 4))
                if show_reg:
                    sns.regplot(x="release_year_num", y=ycol, data=plot_df, ax=ax, scatter_kws=dict(s=20, alpha=0.6))
                else:
                    sns.scatterplot(x="release_year_num", y=ycol, data=plot_df, ax=ax, s=20)
                ax.set_xlabel("Año de estreno")
                ax.set_ylabel(ycol)
                st.pyplot(fig, clear_figure=True)
 
st.caption("Hecho con Streamlit • Seaborn • Matplotlib • Pandas")

#Prueba 2
#prueba de despliegue continuo 3
