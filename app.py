import streamlit as st
import pandas as pd
from supabase import create_client
import secrets
import string
from datetime import datetime

# 1. CONEXIÓN SEGURA
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Error de configuración: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

st.set_page_config(page_title="Vital Ingenieros ERP", layout="wide", page_icon="🏗️")

# --- ESTILOS UX ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #2c1e12; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: white !important; }
    .stButton>button { border-radius: 10px; background-color: #4b3621; color: white; width: 100%; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #4b3621; }
    .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE SEGURIDAD ---
def generar_clave_unica():
    caracteres = string.ascii_letters + string.digits
    while True:
        clave = ''.join(secrets.choice(caracteres) for _ in range(12))
        if (any(c.isdigit() for c in clave) and any(c.isupper() for c in clave) and any(c.islower() for c in clave)):
            return clave

def plantilla_correo(nombre, clave, asunto="Bienvenida"):
    return f"""
    Asunto: {asunto} - Vital Ingenieros ERP
    
    Hola {nombre},
    Tus credenciales de acceso han sido actualizadas/creadas:
    
    - Usuario: {nombre}
    - Clave Temporal: {clave}
    
    Nota: El sistema solicitará el cambio de esta clave en el próximo ingreso.
    """

# --- LÓGICA DE AUTENTICACIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.update({'autenticado': False, 'user_data': None, 'cambio_pwd_obligatorio': False})

if not st.session_state['autenticado']:
    st.sidebar.title("VITAL ERP")
    u_input = st.sidebar.text_input("Usuario")
    p_input = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("INGRESAR"):
        if u_input == "administrador" and p_input == "1234":
            st.session_state.update({'autenticado': True, 'user_data': {'id': 0, 'nombre': 'Admin', 'rol': 'Administrador'}})
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
                st.sidebar.error("Usuario o contraseña incorrectos")
    st.stop()

# --- CAMBIO DE CONTRASEÑA ---
if st.session_state['cambio_pwd_obligatorio']:
    st.title("🔐 Seguridad: Cambio de Contraseña")
    with st.form("pwd_form"):
        n_pwd = st.text_input("Nueva Contraseña", type="password")
        c_pwd = st.text_input("Confirmar Contraseña", type="password")
        if st.form_submit_button("Actualizar"):
            if n_pwd == c_pwd and len(n_pwd) >= 6:
                supabase.table("usuarios").update({"clave": n_pwd, "primer_ingreso": False}).eq("id", st.session_state['user_data']['id']).execute()
                st.session_state['cambio_pwd_obligatorio'] = False
                st.success("Contraseña actualizada.")
                st.rerun()
            else:
                st.error("Error en las contraseñas.")
    st.stop()

# --- DASHBOARD PRINCIPAL ---
st.sidebar.write(f"Sesión: **{st.session_state['user_data']['nombre']}**")
rol = st.session_state['user_data']['rol']

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.update({'autenticado': False, 'user_data': None})
    st.rerun()

# ---------------- ADMINISTRADOR ----------------
if rol == "Administrador":
    opcion = st.sidebar.radio("Menú", ["👥 Gestión de Usuarios", "🏗️ Gestión de Proyectos"])

    if opcion == "👥 Gestión de Usuarios":
        st.title("Administración de Personal")
        tab_list, tab_reset = st.tabs(["Lista de Usuarios", "Restablecer Claves"])
        
        with tab_list:
            with st.expander("➕ Crear Nuevo Usuario"):
                with st.form("crear_u", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    n_u = c1.text_input("Nombre")
                    m_u = c2.text_input("Correo")
                    r_u = st.selectbox("Rol", ["Especialista", "Jefe de Proyecto"])
                    if st.form_submit_button("Registrar"):
                        clave_t = generar_clave_unica()
                        supabase.table("usuarios").insert({"nombre": n_u, "correo": m_u, "rol": r_u, "clave": clave_t, "primer_ingreso": True}).execute()
                        st.info("Copia los datos de acceso:")
                        st.code(plantilla_correo(n_u, clave_t))

            u_db = pd.DataFrame(supabase.table("usuarios").select("*").execute().data)
            if not u_db.empty:
                st.dataframe(u_db[['id', 'nombre', 'correo', 'rol']], use_container_width=True)
        
        with tab_reset:
            st.subheader("Reset de Seguridad")
            user_to_reset = st.selectbox("Seleccione Usuario", u_db['nombre'].tolist() if not u_db.empty else [])
            if st.button("Generar Nueva Clave Temporal"):
                nueva_t = generar_clave_unica()
                supabase.table("usuarios").update({"clave": nueva_t, "primer_ingreso": True}).eq("nombre", user_to_reset).execute()
                st.warning(f"Clave reseteada para {user_to_reset}")
                st.code(plantilla_correo(user_to_reset, nueva_t, asunto="Reset de Contraseña"))

    elif opcion == "🏗️ Gestión de Proyectos":
        st.title("Control de Proyectos")
        with st.form("proy_form"):
            nom_p = st.text_input("Nombre Proyecto")
            cli_p = st.text_input("Cliente")
            mon_p = st.number_input("Monto ($)", min_value=0.0)
            if st.form_submit_button("Guardar Proyecto"):
                supabase.table("proyectos").insert({"nombre": nom_p, "cliente": cli_p, "presupuesto_total": mon_p, "estado": "Activo"}).execute()
                st.rerun()
        p_data = pd.DataFrame(supabase.table("proyectos").select("*").execute().data)
        st.dataframe(p_data, use_container_width=True)

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
                hrs = st.number_input("Horas invertidas", min_value=0.5, step=0.5)
                det = st.text_area("Descripción de la actividad")
                if st.form_submit_button("Enviar Registro"):
                    supabase.table("registros_horas").insert({
                        "proyecto_id": lista_p[p_sel],
                        "especialista_nombre": st.session_state['user_data']['nombre'],
                        "horas_consumidas": hrs,
                        "descripcion": det,
                        "fecha_registro": str(datetime.now().date())
                    }).execute()
                    st.success("Horas registradas con éxito.")
        else:
            st.warning("No hay proyectos activos.")

    with t2:
        st.subheader("Mis Actividades Recientes")
        mis_h = supabase.table("registros_horas").select("*").eq("especialista_nombre", st.session_state['user_data']['nombre']).order("fecha_registro", desc=True).execute().data
        if mis_h:
            df_hist = pd.DataFrame(mis_h)
            st.dataframe(df_hist[['fecha_registro', 'horas_consumidas', 'descripcion']], use_container_width=True)
            st.metric("Total Acumulado", f"{df_hist['horas_consumidas'].sum()} hrs")
        else:
            st.info("Aún no tienes registros.")

# ---------------- JEFE DE PROYECTO ----------------
elif rol == "Jefe de Proyecto":
    st.title("📊 Reportes de Gestión")
    # El Jefe de Proyecto ve todo pero no edita
    all_h = pd.DataFrame(supabase.table("registros_horas").select("*").execute().data)
    if not all_h.empty:
        st.write("Resumen de Carga por Especialista")
        st.bar_chart(all_h.groupby('especialista_nombre')['horas_consumidas'].sum())
        st.dataframe(all_h, use_container_width=True)
