import streamlit as st

# Configuración inicial de la página principal
st.set_page_config(
    page_title="CarpinterIA - Hub", 
    page_icon="🪵", 
    layout="centered"
)

# ==============================================================================
# BARRA LATERAL (NAVEGACIÓN PERSONALIZADA)
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <style>
        /* Ocultar el menú lateral por defecto de Streamlit */
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Tipografía personalizada para nuestros links de navegación */
        .stPageLink a {
            font-family: 'Trebuchet MS', 'Lucida Sans Unicode', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.15rem !important;
            color: #2C3E50 !important;
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .stPageLink a:hover {
            color: #E67E22 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("CarpinterIA")
    
    st.markdown("### 📍 Navegación")
    st.page_link("app.py", label="Menú Principal", icon="🏠")
    st.page_link("pages/1_placares.py", label="Módulo Placares", icon="🗄️")
    st.page_link("pages/2_escritorios.py", label="Módulo Escritorios", icon="🪑")

# ==============================================================================
# PANTALLA CENTRAL (HUB)
# ==============================================================================
st.title("CarpinterIA Hub")
st.subheader("Plataforma de Diseño y Despiece CAM")
st.markdown("---")

st.markdown("### ¿Qué vamos a fabricar hoy?")
st.markdown("Seleccioná un módulo desde el menú lateral izquierdo (👈) para comenzar a diseñar.")

st.write("") # Espacio en blanco

# Tarjetas informativas
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 🗄️ Cajas y Roperos")
        st.write("Diseño paramétrico de estructuras cerradas.")
        st.caption("✔️ Placares y Vestidores\n\n✔️ Alacenas\n\n✔️ Bajomesadas")

with col2:
    with st.container(border=True):
        st.markdown("### 🪑 Superficies y Mesas")
        st.write("Diseño estructural con cálculo de apoyos.")
        st.caption("✔️ Escritorios Gerenciales\n\n✔️ Mesas de Trabajo\n\n✔️ Barras")

st.markdown("---")
st.info("💡 **Próximamente:** Guardado de proyectos en la nube, optimizador visual de corte en placa y registro de usuarios.")
