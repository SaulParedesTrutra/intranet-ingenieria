import streamlit as st
import pandas as pd
from supabase import create_client
import os
import secrets
import string

# Configuración Inicial
st.set_page_config(page_title="Vital.pe - Intranet", layout="wide")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# Conexión Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- INICIO DE SESIÓN Y MENÚ (Resumido para brevedad) ---
if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None})

# Lógica de Login... (Mantener tu lógica actual)

# --- VENTANA: EMPLEADOS ---
if st.session_state['autenticado']:
    user = st.session_state['user_data']
    
    # Barra lateral de navegación
    menu = st.sidebar.radio("Menú", ["🏠 Inicio", "👥 Empleados", "📂 Proyectos"])
    
    if menu == "👥 Empleados":
        st.markdown("<h1 style='color: #1e293b;'>👥 Gestión de Empleados</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Lista de Personal", "Registrar Nuevo"])

        with tab1:
            usuarios_db = supabase.table("usuarios").select("*").order("nombre").execute().data
            if usuarios_db:
                # Cuadrícula de 3 columnas
                cols = st.columns(3)
                for i, emp in enumerate(usuarios_db):
                    is_active = emp.get('activo', True)
                    idx = i % 3
                    
                    with cols[idx]:
                        # Diseño de la tarjeta
                        st.markdown(f"""
                        <div class="employee-card">
                            <span class="status-badge {'status-activo' if is_active else 'status-inactivo'}">
                                {'Activo' if is_active else 'Inactivo'}
                            </span>
                            <div class="emp-name">{emp['nombre'].upper()}</div>
                            <div class="emp-detail">✉️ {emp['correo']}</div>
                            <div class="emp-detail">👤 {emp['rol']}</div>
                            <div class="emp-detail">📅 Ingreso: 2024</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botones de Acción (Aumentamos el espacio para que no se amontonen)
                        b1, b2, b3 = st.columns([1, 1.2, 1])
                        
                        with b1:
                            if st.button("📝 Ed", key=f"e_{emp['id']}"):
                                st.session_state[f"edit_{emp['id']}"] = True
                        
                        with b2:
                            lbl = "🚫 Off" if is_active else "✅ On"
                            if st.button(lbl, key=f"s_{emp['id']}"):
                                supabase.table("usuarios").update({"activo": not is_active}).eq("id", emp['id']).execute()
                                st.rerun()
                        
                        with b3:
                            if st.button("🗑️ Del", key=f"d_{emp['id']}"):
                                supabase.table("usuarios").delete().eq("id", emp['id']).execute()
                                st.rerun()
            else:
                st.info("No hay empleados registrados.")
