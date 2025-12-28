import streamlit as st
import pandas as pd
from supabase import create_client
import secrets
import string
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONEXIÓN SEGURA A SUPABASE
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Error de configuración: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Vital Ingenieros ERP", layout="wide", page_icon="🏗️")

# --- ESTILOS UX (Letras blancas en sidebar, diseño profesional) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2c1e12; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: white !important; }
    .stButton>button { border-radius: 10px; background-color: #4b3621; color: white; width: 100%; font-weight: bold; }
    h1, h2, h3 { color: #4b3621; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SEGURIDAD Y CORREO ---
def generar_clave_unica():
    caracteres = string.ascii_letters + string.digits
    while True:
        clave = ''.join(secrets.choice(caracteres) for _ in range(12))
        if (any(c.isdigit() for c in clave) and any(c.isupper() for c in clave) and any(c.islower() for c in clave)):
            return clave

def enviar_email_real(destinatario, nombre_usuario, clave_temp, asunto_tipo="Bienvenida"):
    remitente = st.secrets["EMAIL_SENDER"]
    password = st.secrets["EMAIL_PASSWORD"]
    servidor_smtp = st.secrets.get("SMTP_SERVER", "smtp.office365.com")
    puerto_smtp = int(st.secrets.get("SMTP_PORT", 587))
    
    msg = MIMEMultipart()
    msg['From'] = f"Vital Ingenieros ERP <{remitente}>"
    msg['To'] = destinatario
    msg['Subject'] = f"{asunto_tipo} - Sistema de Gestión"

    cuerpo = f"""
    Hola {nombre_usuario},
    
    Se han generado tus credenciales para el ERP de Vital Ingenieros:
    
    Usuario: {nombre_usuario}
    Contraseña Temporal: {clave_temp}
    
    Por seguridad, deberás cambiar esta clave en tu primer ingreso.
    """
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        server = smtplib.SMTP(servidor_smtp, puerto_smtp)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error en el envío de correo: {e}")
        return False

# --- LÓGICA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None, 'cambio_pwd_obligatorio': False})

if not st.session_state['autenticado']:
    st.sidebar.title("VITAL ERP")
    u_input = st.sidebar.text_input("Usuario")
    p_input = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("INGRESAR"):
        if u_input == "administrador" and p_input == "1234":
            st.session_state.update({'autenticado': True, 'user_data': {'nombre': 'Admin', 'rol': 'Administrador'}})
            st.rerun()
        else:
            res = supabase.table("usuarios").select("*").eq("nombre", u_input).eq("clave", p_input).execute().data
            if res:
                user = res[0]
                st.session_state.update({'autenticado': True, 'user_data': user})
                if user.get('primer_ingreso'):
                    st.session_state['cambio_pwd_obligatorio'] = True
                st.rerun()
            else:
                st.sidebar.error("Credenciales incorrectas")
    st.stop()

# --- CAMBIO DE CONTRASEÑA OBLIGATORIO ---
if st.session_state['cambio_pwd_obligatorio']:
    st.title("🔐 Seguridad: Cambio de Contraseña")
    with st.form("pwd_form"):
        n_pwd = st.text_input("Nueva Contraseña", type="password")
        c_pwd = st.text_input("Confirmar Contraseña", type="password")
        if st.form_submit_button("Actualizar y Entrar"):
            if n_pwd == c_pwd and len(n_pwd) >= 6:
                supabase.table("usuarios").update({"clave": n_pwd, "primer_ingreso": False}).eq("id", st.session_state['user_data']['id']).execute()
                st.session_state['cambio_pwd_obligatorio'] = False
                st.success("Contraseña actualizada.")
                st.rerun()
            else:
                st.error("Error en las contraseñas (mínimo 6 caracteres).")
    st.stop()

# --- MENÚ LATERAL Y CIERRE DE SESIÓN ---
st.sidebar.write(f"Usuario: **{st.session_state['user_data']['nombre']}**")
rol = st.session_state['user_data']['rol']

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.update({'autenticado': False, 'user_data': None})
    st.rerun()

# ---------------- ADMINISTRADOR ----------------
if rol == "Administrador":
    opcion = st.sidebar.radio("Menú", ["👥 Gestión Usuarios", "🏗️ Gestión Proyectos"])

    if opcion == "👥 Gestión Usuarios":
        st.title("Administración de Personal")
        t_list, t_reset = st.tabs(["Lista y Creación", "Resetear Clave"])
        
        with t_list:
            with st.form("crear_u", clear_on_submit=True):
                c1, c2 = st.columns(2)
                nombre_u = c1.text_input("Nombre Completo")
                email_u = c2.text_input("Correo Electrónico")
                rol_u = st.selectbox("Rol", ["Especialista", "Jefe de Proyecto"])
                if st.form_submit_button("Registrar y Enviar Email"):
                    clave_t = generar_clave_unica()
                    supabase.table("usuarios").insert({"nombre": nombre_u, "correo": email_u, "rol": rol_u, "clave": clave_t, "primer_ingreso": True}).execute()
                    if enviar_email_real(email_u, nombre_u, clave_t):
                        st.success(f"Correo enviado a {email_u}")
                    st.rerun()

            usuarios_db = pd.DataFrame(supabase.table("usuarios").select("*").execute().data)
            if not usuarios_db.empty:
                st.dataframe(usuarios_db[['id', 'nombre', 'correo', 'rol']], use_container_width=True)
                id_borrar = st.number_input("ID para eliminar", min_value=0, step=1)
                if st.button("🗑️ Eliminar Usuario"):
                    supabase.table("usuarios").delete().eq("id", id_borrar).execute()
                    st.rerun()

    elif opcion == "🏗️ Gestión Proyectos":
        st.title("Control de Proyectos")
        with st.form("proy_form"):
            n_p = st.text_input("Nombre del Proyecto")
            c_p = st.text_input("Cliente")
            d_p = st.text_area("Descripción")
            m_p = st.number_input("Monto Económico ($)", min_value=0.0)
            if st.form_submit_button("Crear Proyecto"):
                supabase.table("proyectos").insert({"nombre": n_p, "cliente": c_p, "descripcion": d_p, "presupuesto_total": m_p, "estado": "Activo"}).execute()
                st.rerun()
        
        proyectos_db = pd.DataFrame(supabase.table("proyectos").select("*").execute().data)
        if not proyectos_db.empty:
            st.dataframe(proyectos_db, use_container_width=True)

# ---------------- ESPECIALISTA ----------------
elif rol == "Especialista":
    st.title("👷 Mi Panel de Trabajo")
    t1, t2 = st.tabs(["📝 Registrar Horas", "📂 Mi Historial"])
    
    with t1:
        proyectos = supabase.table("proyectos").select("*").execute().data
        if proyectos:
            lista_p = {p['nombre']: p['id'] for p in proyectos}
            with st.form("reg_h"):
                p_sel = st.selectbox("Proyecto", list(lista_p.keys()))
                hrs = st.number_input("Horas", min_value=0.5, step=0.5)
                det = st.text_area("Descripción de la actividad")
                if st.form_submit_button("Guardar Registro"):
                    supabase.table("registros_horas").insert({
                        "proyecto_id": lista_p[p_sel],
                        "especialista_nombre": st.session_state['user_data']['nombre'],
                        "horas_consumidas": hrs,
                        "descripcion": det,
                        "fecha_registro": str(datetime.now().date())
                    }).execute()
                    st.success("Registro guardado.")
        
    with t2:
        mis_h = pd.DataFrame(supabase.table("registros_horas").select("*").eq("especialista_nombre", st.session_state['user_data']['nombre']).execute().data)
        if not mis_h.empty:
            st.dataframe(mis_h[['fecha_registro', 'horas_consumidas', 'descripcion']], use_container_width=True)
            st.metric("Total de Horas", f"{mis_h['horas_consumidas'].sum()} hrs")

# ---------------- JEFE DE PROYECTO ----------------
elif rol == "Jefe de Proyecto":
    st.title("📊 Reportes de Gestión")
    all_h = pd.DataFrame(supabase.table("registros_horas").select("*").execute().data)
    if not all_h.empty:
        st.bar_chart(all_h.groupby('especialista_nombre')['horas_consumidas'].sum())
        st.dataframe(all_h, use_container_width=True)
