import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONEXIÓN SEGURA
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Error de configuración: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Intranet Vital Ingenieros", layout="wide", page_icon="🏗️")

# ESTILO VISUAL
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #4b3621; color: white; border-radius: 5px; width: 100%; }
    h1, h2, h3 { color: #4b3621; }
    .stTab { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# BARRA LATERAL
st.sidebar.title("🛠️ Panel de Control")
menu = ["Carga de Horas", "Dashboard Jefe", "⚙️ Administración del Sistema"]
choice = st.sidebar.selectbox("Seleccione una opción", menu)

# --- MÓDULO 1: CARGA DE HORAS (ESPECIALISTAS) ---
if choice == "Carga de Horas":
    st.title("📝 Registro Diario de Actividades")
    
    try:
        # Cargar datos necesarios para el formulario
        proyectos_db = supabase.table("proyectos").select("*").eq("estado", "Activo").execute().data
        especialistas_db = supabase.table("usuarios").select("*").eq("rol", "Especialista").execute().data
        
        if not proyectos_db or not especialistas_db:
            st.warning("⚠️ Configuración incompleta: El administrador debe crear Proyectos y Usuarios en la pestaña de Administración.")
        else:
            dict_proyectos = {p['nombre']: p['id'] for p in proyectos_db}
            lista_especialistas = [u['nombre'] for u in especialistas_db]
            
            with st.form("form_horas", clear_on_submit=True):
                col_u, col_p = st.columns(2)
                with col_u:
                    nombre_sel = st.selectbox("Especialista", lista_especialistas)
                with col_p:
                    proyecto_sel = st.selectbox("Proyecto", list(dict_proyectos.keys()))
                
                # Filtrar Entregables por Proyecto
                entregables_db = supabase.table("entregables").select("*").eq("proyecto_id", dict_proyectos[proyecto_sel]).execute().data
                dict_entregables = {e['nombre_entregable']: e['id'] for e in entregables_db} if entregables_db else {}
                
                entregable_sel = st.selectbox("Entregable asociado", list(dict_entregables.keys()) if dict_entregables else ["Sin entregables"])
                
                col1, col2 = st.columns(2)
                with col1:
                    fecha = st.date_input("Fecha")
                with col2:
                    horas = st.number_input("Horas consumidas", min_value=0.5, max_value=24.0, step=0.5)
                
                descripcion = st.text_area("Descripción del trabajo")
                
                if st.form_submit_button("Guardar Reporte"):
                    if not dict_entregables:
                        st.error("Error: Este proyecto no tiene entregables asignados.")
                    else:
                        data = {
                            "especialista_nombre": nombre_sel,
                            "proyecto_id": dict_proyectos[proyecto_sel],
                            "entregable_id": dict_entregables[entregable_sel],
                            "fecha": str(fecha),
                            "horas_consumidas": horas,
                            "descripcion": descripcion
                        }
                        supabase.table("registros_horas").insert(data).execute()
                        st.success("✅ Registro guardado correctamente.")
    except Exception as e:
        st.error(f"Error en el sistema: {e}")

# --- MÓDULO 2: DASHBOARD DEL JEFE ---
elif choice == "Dashboard Jefe":
    st.title("📊 Control de Gestión y Gastos")
    
    registros = supabase.table("registros_horas").select("*, proyectos(nombre, presupuesto_total)").execute().data
    if registros:
        df = pd.DataFrame(registros)
        st.metric("Total Horas Acumuladas", f"{df['horas_consumidas'].sum()} hrs")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Horas por Especialista")
            st.bar_chart(df.groupby('especialista_nombre')['horas_consumidas'].sum())
        with c2:
            st.subheader("Últimos Registros")
            st.dataframe(df[['fecha', 'especialista_nombre', 'horas_consumidas', 'descripcion']].tail(10))
    else:
        st.info("No hay datos para mostrar.")

# --- MÓDULO 3: ADMINISTRACIÓN (GESTIÓN WEB) ---
elif choice == "⚙️ Administración del Sistema":
    st.title("⚙️ Gestión Integral de Sistema")
    t1, t2, t3 = st.tabs(["👥 Usuarios", "🏗️ Proyectos", "📋 Entregables"])
    
    with t1:
        st.subheader("Gestión de Especialistas")
        with st.form("nuevo_usuario"):
            u_nombre = st.text_input("Nombre Completo")
            u_rol = st.selectbox("Rol", ["Especialista", "Jefe de Proyecto"])
            if st.form_submit_button("Registrar Usuario"):
                supabase.table("usuarios").insert({"nombre": u_nombre, "rol": u_rol}).execute()
                st.success(f"Usuario {u_nombre} creado.")
        
        # Listado de usuarios existentes
        u_list = supabase.table("usuarios").select("*").execute().data
        if u_list: st.table(pd.DataFrame(u_list)[['nombre', 'rol']])

    with t2:
        st.subheader("Gestión de Proyectos")
        with st.form("admin_proy"):
            p_nom = st.text_input("Nombre del Proyecto")
            p_pre = st.number_input("Presupuesto ($)", min_value=0)
            if st.form_submit_button("Crear Proyecto"):
                supabase.table("proyectos").insert({"nombre": p_nom, "presupuesto_total": p_pre, "estado": "Activo"}).execute()
                st.success("Proyecto activo creado.")

    with t3:
        st.subheader("Asignación de Entregables")
        proy_admin = supabase.table("proyectos").select("*").execute().data
        if proy_admin:
            dict_pa = {p['nombre']: p['id'] for p in proy_admin}
            pa_sel = st.selectbox("Seleccione Proyecto", list(dict_pa.keys()))
            en_nom = st.text_input("Nombre de la Entrega (ej: Supervisión Civil)")
            en_hrs = st.number_input("Horas Estimadas", min_value=1)
            if st.button("Asignar"):
                supabase.table("entregables").insert({"proyecto_id": dict_pa[pa_sel], "nombre_entregable": en_nom, "horas_estimadas": en_hrs}).execute()
                st.success("Entregable vinculado.")
