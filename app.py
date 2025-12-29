elif menu == "👥 Empleados":
        st.markdown("<h2 style='margin-bottom:0;'>👥 Gestión de Empleados</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:gray;'>Administración del equipo y permisos</p>", unsafe_allow_html=True)
        
        # Fila de acciones superiores
        col_busqueda, col_nuevo = st.columns([3, 1])
        with col_nuevo:
            if st.button("+ Nuevo Empleado"):
                # Aquí podrías abrir un modal o formulario de registro
                st.info("Formulario de registro en desarrollo")

        st.write("---")

        # Obtener empleados de Supabase
        usuarios = supabase.table("usuarios").select("*").execute().data

        if usuarios:
            # Crear una cuadrícula de 3 columnas
            cols = st.columns(3)
            
            for i, u in enumerate(usuarios):
                # Seleccionar la columna correspondiente (0, 1 o 2)
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="employee-card">
                        <span class="status-badge">activo</span>
                        <div class="employee-name">{u['nombre']}</div>
                        <div class="employee-info">✉️ {u['correo']}</div>
                        <div class="employee-info">👤 {u['rol']}</div>
                        <div class="employee-info">📅 Ingreso: 2024</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botones de acción debajo de cada tarjeta HTML
                    c_edit, c_del, c_empty = st.columns([1, 1, 2])
                    with c_edit:
                        st.button("📝", key=f"edit_{u['id']}")
                    with c_del:
                        if st.button("🗑️", key=f"del_{u['id']}"):
                            # Lógica para eliminar de Supabase
                            supabase.table("usuarios").delete().eq("id", u['id']).execute()
                            st.rerun()
        else:
            st.info("No hay empleados registrados aún.")
