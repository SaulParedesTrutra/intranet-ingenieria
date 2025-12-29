import streamlit as st
import pandas as pd
from supabase import create_client
import os

# ... (Mantener configuración de página y carga de CSS igual) ...

# --- SI ESTÁ AUTENTICADO ---
if st.session_state['autenticado']:
    user = st.session_state['user_data']
    
    # BARRA LATERAL (SIDEBAR)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/6195/6195699.png", width=100)
    st.sidebar.title(f"Bienvenido, {user['nombre']}")
    st.sidebar.markdown(f"**Rol:** {user['rol']}")
    st.sidebar.write("---")

    # Definir opciones según el Rol
    if user['rol'] == "Administrador":
        opciones = ["🏠 Inicio", "⚙️ Configuración", "📂 Gestión de Proyectos", "👥 Empleados", "🏢 Clientes"]
    else:
        # Opciones limitadas para especialistas o jefes de proyecto
        opciones = ["🏠 Inicio", "📂 Gestión de Proyectos"]

    menu = st.sidebar.radio("Navegación", opciones)

    # BOTÓN DE CIERRE DE SESIÓN AL FINAL
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.update({'autenticado': False, 'user_data': None})
        st.rerun()

    # --- LÓGICA DE LAS VENTANAS ---
    if menu == "🏠 Inicio":
        st.title("Panel Principal")
        st.write("Seleccione una opción en el menú de la izquierda para comenzar.")
        
    elif menu == "⚙️ Configuración":
        st.title("⚙️ Configuración del Sistema")
        st.info("Opciones de personalización y ajustes generales.")

    elif menu == "📂 Gestión de Proyectos":
        st.title("📂 Gestión de Proyectos")
        # Aquí va tu código actual de visualización de proyectos

    elif menu == "👥 Empleados":
        st.title("👥 Gestión de Empleados")
        # Aquí va tu código de "Gestión Usuarios" que teníamos antes

    elif menu == "🏢 Clientes":
        st.title("🏢 Base de Datos de Clientes")
        st.write("Listado y registro de clientes de Vital.pe")
