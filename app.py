import streamlit as st

# Configuración inicial de la página principal
st.set_page_config(
    page_title="CarpinterIA - Hub", 
    page_icon="🪵", 
    layout="centered"
)

# Encabezado
st.image("https://cdn-icons-png.flaticon.com/512/3063/3063080.png", width=80)
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
