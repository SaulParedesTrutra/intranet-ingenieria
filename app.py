import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONEXIÓN SEGURA
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Vital ERP - Acceso", layout="wide")

# --- UX: ESTILOS PERSONALIZADOS (Letras blancas y fondo oscuro) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2c1e12; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: white !important; }
    .stButton>button { border-radius: 10px; background-color: #4b3621; color: white; width: 100%; }
    h1, h2, h3 { color: #4b3621; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

def login():
    st.sidebar.title("VITAL ERP")
    with st.sidebar.container():
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            # Credenciales de Administrador solicitadas
            if usuario == "administrador" and clave == "1234":
                st.session_state['autenticado'] = True
                st.session_state['rol'] = "Administrador"
                st.session_state['nombre'] = "Administrador"
                st.rerun()
            # Validación contra base de datos para otros usuarios
            else:
                user_db = supabase.table("usuarios").select("*").eq("nombre", usuario).execute().data
                if user_db: # Aquí podrías añadir un campo 'clave' en la tabla usuarios para validar
                    st.session_state['autenticado'] = True
                    st.session_state['rol'] = user_db[0]['rol']
                    st.session_state['nombre'] = user_db[0]['nombre']
                    st.rerun()
                else:
                    st.sidebar.error("Usuario o contraseña incorrectos")

if not st.session_state['autenticado']:
    login()
    st.info("Por favor, ingrese sus credenciales en el panel izquierdo para continuar.")
    st.stop()

# --- SI ESTÁ AUTENTICADO, MOSTRAR EL CONTENIDO ---
st.sidebar.write(f"Bienvenido, **{st.session_state['nombre']}**")
rol_usuario = st.session_state['rol']

if st.sidebar.button("Cerrar Sesión"):
    st.session_state['autenticado'] = False
    st.rerun()

# --- LÓGICA DE PERFILES ---

if rol_usuario == "Administrador":
    st.title("🛡️ Panel de Administración")
    tab1, tab2, tab3 = st.tabs(["Gestionar Usuarios", "Gestionar Proyectos", "Editar/Borrar"])
    
    with tab1:
        st.subheader("Usuarios del Sistema")
        # Formulario para Crear/Editar
        with st.form("form_user"):
            u_nom = st.text_input("Nombre Completo")
            u_rol = st.selectbox("Rol", ["Especialista", "Jefe de Proyecto", "Administrador"])
            if st.form_submit_button("Guardar Usuario"):
                supabase.table("usuarios").insert({"nombre": u_nom, "rol": u_rol}).execute()
                st.success("Usuario registrado")
                st.rerun()
        
        # Tabla con opción de eliminar
        usuarios_list = supabase.table("usuarios").select("*").execute().data
        if usuarios_list:
            df_u = pd.DataFrame(usuarios_list)
            st.dataframe(df_u[["id", "nombre", "rol"]], use_container_width=True)
            id_borrar = st.number_input("ID de usuario a eliminar", min_value=1, step=1)
            if st.button("🗑️ Eliminar Usuario Seleccionado"):
                supabase.table("usuarios").delete().eq("id", id_borrar).execute()
                st.success(f"ID {id_borrar} eliminado")
                st.rerun()

elif rol_usuario == "Jefe de Proyecto":
    st.title("📊 Reportes de Ingeniería")
    # Lógica de Dashboards aquí...

elif rol_usuario == "Especialista":
    st.title(f"👷 Registro de Horas - {st.session_state['nombre']}")
    # Lógica de carga de horas aquí...
