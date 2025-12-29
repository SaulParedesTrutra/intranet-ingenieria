import streamlit as st
import pandas as pd
from supabase import create_client
import os

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Vital.pe - Intranet", layout="centered", page_icon="🔒")

# CARGA DE DISEÑO (CSS)
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# CONEXIÓN SUPABASE (Asegúrate de tener tus Secrets configurados)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None})

# --- INTERFAZ DE LOGIN (ESTILO TARJETA ÚNICA) ---
if not st.session_state['autenticado']:
    st.write("##") # Espacio superior
    
    # Este bloque genera la tarjeta blanca del login
    with st.container():
        # Logo Superior
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/6195/6195699.png' width='80'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Vital.pe</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Propuesta de Software - Intranet</p>", unsafe_allow_html=True)
        st.write("---")
        
        # Campos de entrada
        usuario = st.text_input("Usuario o Correo")
        clave = st.text_input("Código de Acceso", type="password")
        
        st.write("##") # Espacio para el botón
        if st.button("Acceder"):
            if usuario == "administrador" and clave == "1234":
                st.session_state.update({'autenticado': True, 'user_data': {'nombre': 'Admin', 'rol': 'Administrador'}})
                st.rerun()
            else:
                res = supabase.table("usuarios").select("*").eq("nombre", usuario).eq("clave", clave).execute().data
                if res:
                    st.session_state.update({'autenticado': True, 'user_data': res[0]})
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    st.stop()

# --- SI ESTÁ AUTENTICADO (Contenido del sistema) ---
st.title("Panel Principal")
st.write(f"Bienvenido, {st.session_state['user_data']['nombre']}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.update({'autenticado': False, 'user_data': None})
    st.rerun()
