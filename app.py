import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CARGAR CSS EXTERNO
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 2. CONFIGURACIÓN Y CONEXIÓN (MANTENER IGUAL)
st.set_page_config(page_title="Vital.pe - Intranet", layout="centered", page_icon="🔒")
local_css("style.css") # Llamada al archivo de diseño

# (Variables de Supabase y funciones de correo se mantienen igual...)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None, 'cambio_pwd': False})

# --- INTERFAZ DE LOGIN (DISEÑO MEJORADO) ---
if not st.session_state['autenticado']:
    # Espaciado superior para centrar verticalmente
    st.write("##")
    
    # Contenedor central
    with st.container():
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/6195/6195699.png' width='80'></div>", unsafe_allow_html=True)
        st.title("Vital.pe")
        st.markdown("<p>Propuesta de Software - Intranet</p>", unsafe_allow_html=True)
        
        usuario = st.text_input("Usuario o Correo")
        clave = st.text_input("Código de Acceso", type="password")
        
        st.write("##") # Espacio antes del botón
        if st.button("Acceder"):
            if usuario == "administrador" and clave == "1234":
                st.session_state.update({'autenticado': True, 'user_data': {'nombre': 'Admin', 'rol': 'Administrador'}})
                st.rerun()
            else:
                # Lógica de búsqueda en Supabase
                res = supabase.table("usuarios").select("*").eq("nombre", usuario).eq("clave", clave).execute().data
                if res:
                    st.session_state.update({'autenticado': True, 'user_data': res[0]})
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    st.stop()

# --- SI ESTÁ AUTENTICADO (Contenido del sistema) ---
# Aquí va el resto de tu código de administración y reportes...
