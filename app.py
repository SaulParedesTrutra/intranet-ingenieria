import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONEXIÓN SEGURA (Usa los Secrets de Streamlit)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Error de conexión: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Intranet Vital Ingenieros", layout="wide", page_icon="🏗️")

# ESTILO VISUAL (Color Marrón Oscuro y Gris Ingeniería)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #4b3621; color: white; border-radius: 5px; }
    .stSelectbox, .stTextInput { border-radius: 5px; }
    h1 { color: #4b3621; }
    </style>
    """, unsafe_allow_html=True)

# BARRA LATERAL
st.sidebar.title("🛠️ Menú Principal")
menu = ["Carga de Horas (Especialistas)", "Dashboard de Control (Jefe)"]
choice = st.sidebar.selectbox("Seleccione una opción", menu)

st.sidebar.markdown("---")
st.sidebar.info("Utilice este portal para registrar el avance diario de sus proyectos.")

# --- MÓDULO 1: CARGA DE HORAS ---
if choice == "Carga de Horas (Especialistas)":
    st.title("📝 Registro Diario de Actividades")
    st.subheader("Complete el formulario para reportar sus horas")
    
    # Obtener Proyectos activos desde Supabase
    try:
        proyectos_db = supabase.table("proyectos").select("*").eq("estado", "Activo").execute().data
        if not proyectos_db:
            st.warning("No hay proyectos activos registrados en la base de datos.")
        else:
            dict_proyectos = {p['nombre']: p['id'] for p in proyectos_db}
            
            with st.form("form_horas", clear_on_submit=True):
                nombre = st.text_input("Nombre del Especialista")
                
                proyecto_sel = st.selectbox("Proyecto", list(dict_proyectos.keys()))
                
                # Filtrar Entregables según el proyecto seleccionado
                entregables_db = supabase.table("entregables").select("*").eq("proyecto_id", dict_proyectos[proyecto_sel]).execute().data
                dict_entregables = {e['nombre_entregable']: e['id'] for e in entregables_db} if entregables_db else {}
                
                entregable_sel = st.selectbox("Entregable asociado", list(dict_entregables.keys()) if dict_entregables else ["Sin entregables definidos"])
                
                col1, col2 = st.columns(2)
                with col1:
                    fecha = st.date_input("Fecha de trabajo")
                with col2:
                    horas = st.number_input("Horas consumidas", min_value=0.5, max_value=24.0, step=0.5)
                    
                descripcion = st.text_area("Descripción detallada del trabajo realizado")
                
                enviar = st.form_submit_button("Guardar Reporte Diario")
                
                if enviar:
                    if not dict_entregables:
                        st.error("No se puede guardar: El proyecto no tiene entregables asignados.")
                    else:
                        data = {
                            "especialista_nombre": nombre,
                            "proyecto_id": dict_proyectos[proyecto_sel],
                            "entregable_id": dict_entregables[entregable_sel],
                            "fecha": str(fecha),
                            "horas_consumidas": horas,
                            "descripcion": descripcion
                        }
                        supabase.table("registros_horas").insert(data).execute()
                        st.success(f"✅ ¡Registro guardado para {nombre} en el proyecto {proyecto_sel}!")
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

# --- MÓDULO 2: DASHBOARD DEL JEFE ---
elif choice == "Dashboard de Control (Jefe)":
    st.title("📊 Control de Presupuesto y Rendimiento")
    
    # Cargar registros uniendo tablas
    try:
        registros = supabase.table("registros_horas").select("*, proyectos(nombre), entregables(nombre_entregable)").execute().data
        
        if registros:
            df = pd.DataFrame(registros)
            
            # Kpis Principales
            total_horas = df['horas_consumidas'].sum()
            num_especialistas = df['especialista_nombre'].nunique()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Horas Totales Invertidas", f"{total_horas} hrs")
            c2.metric("Especialistas Activos", num_especialistas)
            c3.metric("Proyectos en curso", df['proyecto_id'].nunique())
            
            st.markdown("---")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Rendimiento por Especialista")
                horas_por_persona = df.groupby('especialista_nombre')['horas_consumidas'].sum().reset_index()
                st.bar_chart(horas_por_persona.set_index('especialista_nombre'))
                
            with col_b:
                st.subheader("Historial de Actividades")
                # Limpiar el DataFrame para mostrarlo mejor
                df_display = df.copy()
                df_display['Proyecto'] = df_display['proyectos'].apply(lambda x: x['nombre'])
                df_display['Entregable'] = df_display['entregables'].apply(lambda x: x['nombre_entregable'])
                st.dataframe(df_display[['fecha', 'especialista_nombre', 'Proyecto', 'Entregable', 'horas_consumidas', 'descripcion']].tail(10))
                
        else:
            st.info("Aún no existen registros de horas para mostrar en el Dashboard.")
    except Exception as e:
        st.error(f"Error al procesar el Dashboard: {e}")
