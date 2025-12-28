import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONEXIÓN A LA BASE DE DATOS (Aquí pondrás tus claves de Supabase)
url = "TU_URL_DE_SUPABASE"
key = "TU_API_KEY_DE_SUPABASE"
supabase = create_client(url, key)

st.set_page_config(page_title="Intranet Vital Ingenieros", layout="wide")

# ESTILO PERSONALIZADO (Color Marrón Oscuro/Ingeniería)
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #4b3621; color: white; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Portal de Gestión de Proyectos")

menu = ["Carga de Horas (Especialistas)", "Dashboard de Control (Jefe)"]
choice = st.sidebar.selectbox("Seleccione Modo", menu)

# --- MÓDULO 1: CARGA DE HORAS ---
if choice == "Carga de Horas (Especialistas)":
    st.header("📝 Registro Diario de Actividades")
    
    with st.form("form_horas"):
        nombre = st.text_input("Nombre del Especialista")
        
        # Traer proyectos de la base de datos
        proyectos_db = supabase.table("proyectos").select("*").execute().data
        dict_proyectos = {p['nombre']: p['id'] for p in proyectos_db}
        proyecto_sel = st.selectbox("Proyecto", list(dict_proyectos.keys()))
        
        # Traer entregables del proyecto seleccionado
        entregables_db = supabase.table("entregables").select("*").eq("proyecto_id", dict_proyectos[proyecto_sel]).execute().data
        dict_entregables = {e['nombre_entregable']: e['id'] for e in entregables_db}
        entregable_sel = st.selectbox("Entregable asociado", list(dict_entregables.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha de trabajo")
        with col2:
            horas = st.number_input("Horas consumidas", min_value=0.5, step=0.5)
            
        descripcion = st.text_area("Descripción de la tarea realizada")
        
        enviar = st.form_submit_button("Guardar Registro")
        
        if enviar:
            data = {
                "especialista_nombre": nombre,
                "proyecto_id": dict_proyectos[proyecto_sel],
                "entregable_id": dict_entregables[entregable_sel],
                "fecha": str(fecha),
                "horas_consumidas": horas,
                "descripcion": descripcion
            }
            supabase.table("registros_horas").insert(data).execute()
            st.success("¡Registro guardado correctamente!")

# --- MÓDULO 2: DASHBOARD DEL JEFE ---
elif choice == "Dashboard de Control (Jefe)":
    st.header("📊 Control de Presupuesto y Rendimiento")
    
    # Lógica de cálculo
    registros = supabase.table("registros_horas").select("*, proyectos(nombre), entregables(nombre_entregable)").execute().data
    df = pd.DataFrame(registros)
    
    if not df.empty:
        # Resumen por proyecto
        resumen = df.groupby('especialista_nombre')['horas_consumidas'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Horas por Especialista")
            st.bar_chart(resumen.set_index('especialista_nombre'))
            
        with col2:
            st.subheader("Últimos Registros")
            st.table(df[['fecha', 'especialista_nombre', 'horas_consumidas', 'descripcion']].tail(5))
    else:
        st.info("Aún no hay datos cargados.")