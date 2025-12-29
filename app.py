import streamlit as st
import pandas as pd
from supabase import create_client
import os
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Vital.pe - Intranet", layout="wide", page_icon="🏗️")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# --- CONEXIÓN SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None})

# --- FUNCIÓN ENVÍO CORREO ---
def enviar_email_real(destinatario, nombre_usuario, clave_temp):
    remitente = st.secrets["EMAIL_SENDER"]
    password = st.secrets["EMAIL_PASSWORD"]
    try:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "Bienvenida - Vital.pe ERP"
        cuerpo = f"Hola {nombre_usuario},\n\nTu clave de acceso es: {clave_temp}"
        msg.attach(MIMEText(cuerpo, 'plain'))
        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except:
        return False

# --- INTERFAZ DE LOGIN ---
if not st.session_state['autenticado']:
    st.write("##")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/6195/6195699.png' width='80'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Vital.pe</h1>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario")
        clave = st.text_input("Código de Acceso", type="password")
        if st.button("Acceder", use_container_width=True):
            if usuario == "administrador" and clave == "1234":
                st.session_state.update({'autenticado': True, 'user_data': {'nombre': 'Admin', 'rol': 'Administrador'}})
                st.rerun()
            else:
                res = supabase.table("usuarios").select("*").eq("nombre", usuario).eq("clave", clave).execute().data
                if res:
                    if res[0].get('activo', True):
                        st.session_state.update({'autenticado': True, 'user_data': res[0]})
                        st.rerun()
                    else:
                        st.error("Esta cuenta ha sido desactivada.")
                else:
                    st.error("Credenciales incorrectas")
    st.stop()

# --- PANEL DE CONTROL ---
user = st.session_state['user_data']
st.sidebar.title("Vital.pe")

if user['rol'] == "Administrador":
    menu = st.sidebar.radio("Navegación", ["🏠 Inicio", "⚙️ Configuración", "📂 Proyectos", "👥 Empleados", "🏢 Clientes"])
else:
    menu = st.sidebar.radio("Navegación", ["🏠 Inicio", "📂 Proyectos"])

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.update({'autenticado': False, 'user_data': None})
    st.rerun()

# --- VENTANA EMPLEADOS ---
if menu == "👥 Empleados":
    st.title("👥 Gestión de Empleados")
    tab1, tab2 = st.tabs(["Lista de Personal", "Registrar Nuevo"])

    with tab1:
        usuarios_db = supabase.table("usuarios").select("*").order("nombre").execute().data
        if usuarios_db:
            cols = st.columns(3)
            for i, emp in enumerate(usuarios_db):
                is_active = emp.get('activo', True)
                status_label = "ACTIVO" if is_active else "INACTIVO"
                status_class = "status-activo" if is_active else "status-inactivo"
                card_class = "employee-card" if is_active else "employee-card disabled-user"
                
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="{card_class}">
                        <span class="status-badge {status_class}">{status_label}</span>
                        <div class="emp-name">{emp['nombre']}</div>
                        <div class="emp-detail">✉️ {emp['correo']}</div>
                        <div class="emp-detail">👤 {emp['rol']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("📝 Editar", key=f"ed_{emp['id']}"):
                        st.session_state[f"edit_mode_{emp['id']}"] = True
                    
                    btn_label = "🚫 Desactivar" if is_active else "✅ Activar"
                    if c2.button(btn_label, key=f"sw_{emp['id']}"):
                        supabase.table("usuarios").update({"activo": not is_active}).eq("id", emp['id']).execute()
                        st.rerun()
                    
                    if c3.button("🗑️ Borrar", key=f"rm_{emp['id']}"):
                        supabase.table("usuarios").delete().eq("id", emp['id']).execute()
                        st.rerun()

                    # Formulario de Edición
                    if st.session_state.get(f"edit_mode_{emp['id']}", False):
                        with st.form(f"form_{emp['id']}"):
                            new_name = st.text_input("Nombre", value=emp['nombre'])
                            new_rol = st.selectbox("Rol", ["Administrador", "Especialista", "Jefe de Proyecto"], index=0)
                            if st.form_submit_button("Guardar"):
                                supabase.table("usuarios").update({"nombre": new_name, "rol": new_rol}).eq("id", emp['id']).execute()
                                st.session_state[f"edit_mode_{emp['id']}"] = False
                                st.rerun()

    with tab2:
        with st.form("nuevo_emp"):
            st.write("### Datos del Empleado")
            nom = st.text_input("Nombre Completo")
            eml = st.text_input("Correo")
            rol = st.selectbox("Rol", ["Especialista", "Jefe de Proyecto", "Administrador"])
            if st.form_submit_button("Registrar"):
                clv = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
                supabase.table("usuarios").insert({"nombre": nom, "correo": eml, "rol": rol, "clave": clv, "activo": True}).execute()
                enviar_email_real(eml, nom, clv)
                st.success("Empleado registrado y correo enviado.")
                st.rerun()

elif menu == "🏠 Inicio":
    st.title("Bienvenido al Sistema")
    st.write("Use el menú lateral para navegar.")
