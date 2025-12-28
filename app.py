# Cambia la línea del menú lateral:
menu = ["Carga de Horas (Especialistas)", "Dashboard de Control (Jefe)", "⚙️ Administración"]

# ... (mantén el código anterior y al final añade esto) ...

elif choice == "⚙️ Administración":
    st.title("⚙️ Panel de Administración")
    
    tab1, tab2 = st.tabs(["Crear Proyectos", "Asignar Entregables"])
    
    with tab1:
        st.subheader("Registrar Nuevo Proyecto")
        with st.form("nuevo_proyecto"):
            n_proy = st.text_input("Nombre del Proyecto")
            presu = st.number_input("Presupuesto Inicial ($)", min_value=0)
            if st.form_submit_button("Crear Proyecto"):
                supabase.table("proyectos").insert({"nombre": n_proy, "presupuesto_total": presu}).execute()
                st.success(f"Proyecto {n_proy} creado.")

    with tab2:
        st.subheader("Añadir Entregable a Proyecto")
        proyectos_db = supabase.table("proyectos").select("*").execute().data
        if proyectos_db:
            dict_p = {p['nombre']: p['id'] for p in proyectos_db}
            p_sel = st.selectbox("Seleccione Proyecto", list(dict_p.keys()), key="admin_p")
            n_entre = st.text_input("Nombre del Entregable (ej: Planos Eléctricos)")
            h_est = st.number_input("Horas Estimadas", min_value=1)
            
            if st.button("Asignar Entregable"):
                supabase.table("entregables").insert({
                    "proyecto_id": dict_p[p_sel], 
                    "nombre_entregable": n_entre, 
                    "horas_estimadas": h_est
                }).execute()
                st.success("Entregable asignado correctamente.")
