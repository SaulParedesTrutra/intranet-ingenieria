import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# CONEXIÓN
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Vital Ingenieros - ERP", layout="wide")

# --- UX: ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2c1e12; color: white; }
    .stButton>button { border-radius: 20px; text-transform: uppercase; font-weight: bold; }
    .status-card { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #4b3621; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE AUTENTICACIÓN SIMPLE (Simulado para UX) ---
st.sidebar.title("🏗️ Vital ERP")
rol_usuario = st.sidebar.selectbox("Perfil de Acceso (Simulación)", ["Administrador", "Jefe de Proyecto", "Especialista"])
usuario_activo = st.sidebar.text_input("Su Nombre/ID", "Esteban")

# --- FUNCIONES DE AYUDA (CRUD) ---
def obtener_datos(tabla):
    return supabase.table(tabla).select("*").execute().data

# --- PERFIL 1: ADMINISTRADOR (GESTIÓN TOTAL) ---
if rol_usuario == "Administrador":
    st.title("⚙️ Gestión Global del Sistema")
    menu_admin = st.tabs(["👥 Usuarios", "🏗️ Proyectos", "📋 Entregables"])

    with menu_admin[0]:
        st.subheader("Control de Personal")
        col_form, col_list = st.columns([1, 2])
        
        with col_form:
            with st.container():
                st.markdown("**Nuevo/Editar Usuario**")
                id_u = st.text_input("ID (dejar vacío para nuevo)")
                nom_u = st.text_input("Nombre")
                rol_u = st.selectbox("Rol", ["Especialista", "Jefe de Proyecto", "Administrador"])
                c1, c2 = st.columns(2)
                if c1.button("💾 Guardar"):
                    payload = {"nombre": nom_u, "rol": rol_u}
                    if id_u:
                        supabase.table("usuarios").update(payload).eq("id", id_u).execute()
                    else:
                        supabase.table("usuarios").insert(payload).execute()
                    st.success("Cambio aplicado")
                    st.rerun()

        with col_list:
            usuarios = pd.DataFrame(obtener_datos("usuarios"))
            if not usuarios.empty:
                st.write("Usuarios Actuales")
                for i, row in usuarios.iterrows():
                    c_n, c_r, c_b = st.columns([3, 2, 1])
                    c_n.text(row['nombre'])
                    c_r.caption(row['rol'])
                    if c_b.button("🗑️", key=f"del_u_{row['id']}"):
                        supabase.table("usuarios").delete().eq("id", row['id']).execute()
                        st.rerun()

    with menu_admin[1]:
        st.subheader("Gestión de Proyectos")
        proy_data = pd.DataFrame(obtener_datos("proyectos"))
        st.dataframe(proy_data, use_container_width=True)
        # Aquí se repetiría la lógica de edición/borrado similar a usuarios

# --- PERFIL 2: JEFE DE PROYECTO (REPORTES) ---
elif rol_usuario == "Jefe de Proyecto":
    st.title("📊 Dashboard de Supervisión")
    
    # KPIs con diseño UX
    registros = pd.DataFrame(obtener_datos("registros_horas"))
    if not registros.empty:
        total_h = registros['horas_consumidas'].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Horas Totales", f"{total_h} h")
        col2.metric("Presupuesto Consumido", f"${total_h * 50}") # Ejemplo de cálculo
        
        st.markdown("---")
        st.subheader("Análisis de Rendimiento")
        st.bar_chart(registros.groupby('especialista_nombre')['horas_consumidas'].sum())
        st.write("Detalle de Registros Diarios")
        st.table(registros.tail(20))

# --- PERFIL 3: ESPECIALISTA (REGISTRO Y CONSULTA) ---
elif rol_usuario == "Especialista":
    st.title(f"👷 Panel de Especialista: {usuario_activo}")
    tab_reg, tab_hist = st.tabs(["➕ Registrar Horas", "📂 Mi Historial"])
    
    with tab_reg:
        proyectos = obtener_datos("proyectos")
        if proyectos:
            dict_p = {p['nombre']: p['id'] for p in proyectos}
            p_sel = st.selectbox("Proyecto", list(dict_p.keys()))
            
            # Filtro dinámico de entregables
            entregables = supabase.table("entregables").select("*").eq("proyecto_id", dict_p[p_sel]).execute().data
            dict_e = {e['nombre_entregable']: e['id'] for e in entregables}
            
            with st.form("registro_h"):
                e_sel = st.selectbox("Entregable", list(dict_e.keys()))
                h_c = st.number_input("Horas", min_value=0.5, step=0.5)
                desc = st.text_area("¿Qué hiciste hoy?")
                if st.form_submit_button("Enviar Reporte"):
                    supabase.table("registros_horas").insert({
                        "especialista_nombre": usuario_activo,
                        "proyecto_id": dict_p[p_sel],
                        "entregable_id": dict_e[e_sel],
                        "horas_consumidas": h_c,
                        "descripcion": desc
                    }).execute()
                    st.success("Horas registradas")
    
    with tab_hist:
        mis_registros = supabase.table("registros_horas").select("*").eq("especialista_nombre", usuario_activo).execute().data
        if mis_registros:
            st.dataframe(pd.DataFrame(mis_registros))
        else:
            st.info("No tienes registros previos.")
