# --- INTERFAZ DE LOGIN ---
if not st.session_state['autenticado']:
    # Centrado vertical inicial
    st.write("##")
    
    # Todo dentro de una columna central para forzar la tarjeta
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo (Usa la URL de la imagen que te guste)
        st.markdown("<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/6195/6195699.png' width='80'></div>", unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>Vital.pe</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>Propuesta de Software - Intranet</p>", unsafe_allow_html=True)
        st.write("---") # Línea divisoria sutil
        
        # Inputs y Botón
        usuario = st.text_input("Usuario o Correo")
        clave = st.text_input("Código de Acceso", type="password")
        
        if st.button("Acceder"):
            # (Tu lógica de validación se mantiene igual aquí)
            if usuario == "administrador" and clave == "1234":
                st.session_state.update({'autenticado': True, 'user_data': {'nombre': 'Admin', 'rol': 'Administrador'}})
                st.rerun()
            else:
                # Búsqueda en Supabase...
                res = supabase.table("usuarios").select("*").eq("nombre", usuario).eq("clave", clave).execute().data
                if res:
                    st.session_state.update({'autenticado': True, 'user_data': res[0]})
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    st.stop()
