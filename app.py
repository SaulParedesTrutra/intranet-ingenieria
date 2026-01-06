import streamlit as st
from supabase import create_client
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Vital.pe - Intranet", layout="wide")

# Conexión Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None, 'view': 'Inicio'})

# --- LOGIN ---
if not st.session_state['autenticado']:
    st.title("🔐 Acceso Vital.pe")
    with st.form("login"):
        u_email = st.text_input("Correo")
        u_pass = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            # Usamos 'clave' porque así se llama en tu BD
            res = supabase.table("usuarios").select("*").eq("correo", u_email).eq("clave", u_pass).execute()
            if res.data:
                st.session_state.update({'autenticado': True, 'user_data': res.data[0]})
                st.rerun()
            else:
                st.error("Datos incorrectos")

# --- APP PRINCIPAL ---
else:
    user = st.session_state['user_data']
    
    # BARRA LATERAL
    with st.sidebar:
        st.header(f"Hola, {user['nombre']}")
        # Agregamos "Mi Perfil" para cambiar la clave
        menu = st.radio("Navegación", ["🏠 Inicio", "👥 Empleados", "⚙️ Mi Perfil"])
        
        if st.button("Cerrar Sesión"):
            st.session_state.clear()
            st.rerun()

    # SECCIÓN: MI PERFIL (CAMBIO DE CONTRASEÑA)
    if menu == "⚙️ Mi Perfil":
        st.subheader("Configuración de Seguridad")
        st.info("Desde aquí puedes actualizar tu contraseña de acceso.")
        
        with st.form("form_cambio_pass"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("Actualizar Clave"):
                if nueva_pass == confirmar and len(nueva_pass) > 5:
                    # Actualizamos en Supabase
                    supabase.table("usuarios").update({
                        "clave": nueva_pass,
                        "primer_ingres": False  # Marcamos que ya no es su primer ingreso
                    }).eq("id", user['id']).execute()
                    
                    st.success("✅ Contraseña actualizada correctamente")
                else:
                    st.error("Las contraseñas no coinciden o son muy cortas")

    # SECCIÓN: EMPLEADOS (Tu código actual)
    elif menu == "👥 Empleados":
        st.title("Gestión de Personal")
        usuarios_db = supabase.table("usuarios").select("*").order("nombre").execute().data
        
        if usuarios_db:
            cols = st.columns(3)
            for i, emp in enumerate(usuarios_db):
                is_active = emp.get('activo', True)
                with cols[i % 3]:
                    st.markdown(f"""
                        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
                            <strong>{emp['nombre'].upper()}</strong><br>
                            <small>{emp['correo']}</small><br>
                            Status: {'🟢 Activo' if is_active else '🔴 Inactivo'}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # El botón OFF cambia el estado 'activo'
                    if st.button("🚫 Off" if is_active else "✅ On", key=f"btn_{emp['id']}"):
                        supabase.table("usuarios").update({"activo": not is_active}).eq("id", emp['id']).execute()
                        st.rerun()
    
    else:
        st.title("Bienvenido a la Intranet")
        st.write("Selecciona una opción del menú para comenzar.")
