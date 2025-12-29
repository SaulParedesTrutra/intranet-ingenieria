import streamlit as st
import pandas as pd
from supabase import create_client
import os

# 1. Configuración de página y CSS
st.set_page_config(page_title="Vital.pe - Intranet", layout="wide", page_icon="🏗️")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# 2. Conexión Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None})

# --- LÓGICA DE LOGIN (Si no está autenticado) ---
if not st.session_state['autenticado']:
    # (Aquí va tu código de login que ya funciona bien...)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/6195/6195699.png' width='80'></div>", unsafe_allow_html=True)
        st.title("Vital.pe")
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("Acceder"):
            if u == "administrador" and p == "1234":
                st.session_state.update({'autenticado': True, 'user_data': {'nombre': 'Admin', 'rol': 'Administrador'}})
                st.rerun()
            else:
                res = supabase.table("usuarios").select("*").eq("nombre", u).eq("clave", p).execute().data
                if res:
                    st.session_state.update({'autenticado': True, 'user_data': res[0]})
                    st.rerun()
    st.stop()

# --- SI ESTÁ AUTENTICADO ---
user = st.session_state['user_data']

# BARRA LATERAL CON OPCIONES DE ADMIN
st.sidebar.title("Vital.pe")
if user['rol'] == "Administrador":
    menu = st.sidebar.radio("Menú Principal", ["🏠 Inicio", "⚙️ Configuración", "📂 Proyectos", "👥 Empleados", "🏢 Clientes"])
else:
    menu = st.sidebar.radio("Menú Principal", ["🏠 Inicio", "📂 Proyectos"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.update({'autenticado': False, 'user_data': None})
    st.rerun()

# --- VENTANA: EMPLEADOS ---
if menu == "👥 Empleados":
    st.markdown("<h1>👥 Gestión de Empleados</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>Administración del equipo y permisos</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["Empleados", "Permisos", "Historial"])
    
    with t1:
        c_bus, c_btn = st.columns([4, 1])
        with c_btn:
            st.button("+ Nuevo Empleado")
        
        st.write("### Lista de Empleados")
        usuarios_db = supabase.table("usuarios").select("*").execute().data
        
        if usuarios_db:
            cols = st.columns(3)
            for i, emp in enumerate(usuarios_db):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="employee-card">
                        <span class="status-badge">activo</span>
                        <div class="emp-name">{emp['nombre']}</div>
                        <div class="emp-detail">✉️ {emp['correo']}</div>
                        <div class="emp-detail">👤 {emp['rol']}</div>
                        <div class="emp-detail">📅 Ingreso: 2024</div>
                    </div>
                    """, unsafe_allow_html=True)
                    # Botones de acción
                    ca1, ca2, ca3 = st.columns([1,1,2])
                    ca1.button("📝", key=f"ed_{emp['id']}")
                    if ca2.button("🗑️", key=f"dl_{emp['id']}"):
                        supabase.table("usuarios").delete().eq("id", emp['id']).execute()
                        st.rerun()
        else:
            st.info("No hay empleados registrados.")

elif menu == "🏠 Inicio":
    st.title(f"Bienvenido, {user['nombre']}")
    st.write("Seleccione una opción en el menú lateral.")

# Agrega aquí los elif para "Configuración", "Proyectos" y "Clientes"
