import streamlit as st
import pandas as pd
from supabase import create_client
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Vital.pe - Intranet", layout="wide")

# --- 2. ESTILO CSS ---
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# --- 3. CONEXIÓN SUPABASE ---
# Asegúrate de tener SUPABASE_URL y SUPABASE_KEY en tus secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- 4. ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.update({
        'autenticado': False, 
        'user_data': None,
        'cambio_obligatorio': False
    })

# --- 5. LÓGICA DE LOGIN ---
if not st.session_state['autenticado']:
    st.title("🔐 Vital.pe - Acceso")
    with st.form("login_form"):
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")
        
        if submit:
            # CORRECCIÓN: Usamos 'clave' en lugar de 'password' según tu imagen
            res = supabase.table("usuarios").select("*").eq("correo", email).eq("clave", password).execute()
            
            if res.data:
                user = res.data[0]
                st.session_state['autenticado'] = True
                st.session_state['user_data'] = user
                
                # Verificar si debe cambiar clave (columna 'primer_ingres')
                if user.get('primer_ingres') == True:
                    st.session_state['cambio_obligatorio'] = True
                
                st.rerun()
            else:
                st.error("Credenciales incorrectas o usuario no encontrado.")

# --- 6. INTERFAZ PARA USUARIOS AUTENTICADOS ---
else:
    user = st.session_state['user_data']

    # CASO: CAMBIO DE CLAVE OBLIGATORIO
    if st.session_state['cambio_obligatorio']:
        st.warning("⚠️ Primer Ingreso Detectado: Por seguridad, debe cambiar su clave.")
        with st.form("change_password_form"):
            nueva_clave = st.text_input("Nueva Contraseña", type="password")
            confirmar_clave = st.text_input("Confirmar Nueva Contraseña", type="password")
            btn_cambiar = st.form_submit_button("Actualizar y Entrar")

            if btn_cambiar:
                if nueva_clave == confirmar_clave and len(nueva_clave) >= 6:
                    # Actualizamos en la DB: nueva clave y ponemos primer_ingres en false
                    supabase.table("usuarios").update({
                        "clave": nueva_clave,
                        "primer_ingres": False
                    }).eq("id", user['id']).execute()
                    
                    st.success("Clave actualizada correctamente.")
                    st.session_state['cambio_obligatorio'] = False
                    # Actualizamos datos locales para reflejar el cambio
                    st.session_state['user_data']['primer_ingres'] = False
                    st.rerun()
                else:
                    st.error("Las claves no coinciden o son muy cortas (mínimo 6 caracteres).")

    # CASO: PANEL PRINCIPAL (Solo si ya cambió su clave)
    else:
        # Barra lateral
        with st.sidebar:
            st.title("Vital.pe")
            st.write(f"Bienvenido, **{user['nombre']}**")
            menu = st.radio("Menú", ["🏠 Inicio", "👥 Empleados", "📂 Proyectos"])
            st.divider()
            if st.button("Cerrar Sesión"):
                st.session_state.clear()
                st.rerun()

        # CONTENIDO DE LAS SECCIONES
        if menu == "👥 Empleados":
            st.markdown("<h1 style='color: #1e293b;'>👥 Gestión de Empleados</h1>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Lista de Personal", "Registrar Nuevo"])

            with tab1:
                usuarios_db = supabase.table("usuarios").select("*").order("nombre").execute().data
                if usuarios_db:
                    cols = st.columns(3)
                    for i, emp in enumerate(usuarios_db):
                        is_active = emp.get('activo', True)
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div style="border:1px solid #ddd; padding:15px; border-radius:10px; margin-bottom:10px;">
                                <small style="color:{'green' if is_active else 'red'}">{'● Activo' if is_active else '○ Inactivo'}</small>
                                <div style="font-weight:bold; font-size:1.1em;">{emp['nombre'].upper()}</div>
                                <div>✉️ {emp['correo']}</div>
                                <div>👤 {emp['rol']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Botones rápidos
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("🚫 Off" if is_active else "✅ On", key=f"s_{emp['id']}"):
                                    supabase.table("usuarios").update({"activo": not is_active}).eq("id", emp['id']).execute()
                                    st.rerun()
                            with b2:
                                if st.button("🗑️ Del", key=f"d_{emp['id']}"):
                                    supabase.table("usuarios").delete().eq("id", emp['id']).execute()
                                    st.rerun()
                else:
                    st.info("No hay empleados registrados.")

        elif menu == "🏠 Inicio":
            st.header(f"Panel de Control - {user['rol']}")
            st.write("Bienvenido a la intranet de Vital.pe.")
