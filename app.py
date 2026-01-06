import streamlit as st
import pandas as pd
from supabase import create_client
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Vital.pe - Intranet", layout="wide", page_icon="👥")

# --- 2. ESTILO CSS ---
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # Fallback por si el archivo no existe
        st.markdown("""
            <style>
            .employee-card {
                background-color: #f8fafc;
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
                margin-bottom: 10px;
            }
            .status-activo { color: green; font-weight: bold; }
            .status-inactivo { color: red; font-weight: bold; }
            .emp-name { font-size: 1.2rem; font-weight: bold; color: #1e293b; }
            </style>
        """, unsafe_allow_html=True)

load_css("style.css")

# --- 3. CONEXIÓN SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- 4. GESTIÓN DE ESTADO (SESSION STATE) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- 5. LÓGICA DE NAVEGACIÓN ---

# CASO A: USUARIO NO LOGUEADO
if not st.session_state.autenticado:
    st.container()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚀 Vital.pe - Intranet")
        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("Entrar")

            if btn_login:
                # Consulta a la tabla usuarios
                try:
                    res = supabase.table("usuarios").select("*").eq("correo", email).eq("password", password).execute()
                    if len(res.data) > 0:
                        st.session_state.autenticado = True
                        st.session_state.user_data = res.data[0]
                        st.success("¡Bienvenido!")
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

# CASO B: USUARIO AUTENTICADO
else:
    user = st.session_state.user_data
    
    # Barra lateral
    with st.sidebar:
        st.image("https://via.placeholder.com/150", width=100) # Opcional: Tu logo
        st.write(f"👤 **{user['nombre']}**")
        st.write(f"🔑 Rol: {user.get('rol', 'Usuario')}")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
        
        st.divider()
        menu = st.radio("Menú", ["🏠 Inicio", "👥 Empleados", "📂 Proyectos"])

    # --- VENTANA: EMPLEADOS ---
    if menu == "👥 Empleados":
        st.markdown("<h1 style='color: #1e293b;'>👥 Gestión de Empleados</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Lista de Personal", "Registrar Nuevo"])

        with tab1:
            try:
                usuarios_db = supabase.table("usuarios").select("*").order("nombre").execute().data
                if usuarios_db:
                    cols = st.columns(3)
                    for i, emp in enumerate(usuarios_db):
                        is_active = emp.get('activo', True)
                        idx = i % 3
                        
                        with cols[idx]:
                            st.markdown(f"""
                            <div class="employee-card">
                                <span class="status-badge {'status-activo' if is_active else 'status-inactivo'}">
                                    {'● Activo' if is_active else '○ Inactivo'}
                                </span>
                                <div class="emp-name">{emp['nombre'].upper()}</div>
                                <div class="emp-detail">✉️ {emp['correo']}</div>
                                <div class="emp-detail">👤 {emp['rol']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            b1, b2, b3 = st.columns(3)
                            with b1:
                                if st.button("📝", key=f"e_{emp['id']}"):
                                    st.info("Función editar en desarrollo")
                            with b2:
                                lbl = "🚫" if is_active else "✅"
                                if st.button(lbl, key=f"s_{emp['id']}"):
                                    supabase.table("usuarios").update({"activo": not is_active}).eq("id", emp['id']).execute()
                                    st.rerun()
                            with b3:
                                if st.button("🗑️", key=f"d_{emp['id']}"):
                                    supabase.table("usuarios").delete().eq("id", emp['id']).execute()
                                    st.rerun()
                else:
                    st.info("No hay empleados registrados.")
            except Exception as e:
                st.error(f"Error al cargar datos: {e}")

    elif menu == "🏠 Inicio":
        st.title(f"Bienvenido al sistema, {user['nombre']}")
        st.write("Selecciona una opción en el menú de la izquierda para comenzar.")
