import streamlit as st
import pandas as pd

# Título de la App
st.title("CarpinterIA - Prototipo V0.1")

# 1. Sidebar de Configuración Global
st.sidebar.header("Parámetros de Taller")
espesor = st.sidebar.selectbox("Espesor de Placa (mm)", [9, 12, 15, 18, 25, 36], index=3)
zocalo_min = st.sidebar.number_input("Zócalo Mínimo (mm)", value=70)

# 2. Carga de Proyecto
uploaded_file = st.file_uploader("Subí tu croquis o foto de referencia", type=['jpg', 'png', 'pdf'])

# 3. Simulación de Tabla de Interpretación (Editable)
st.subheader("Configuración del Mueble")
data = {
    "Variable": ["Ancho Total", "Alto Total", "Profundidad", "Zócalo"],
    "Medida (mm)": [1130, 800, 550, 70]
}
df = st.data_editor(pd.DataFrame(data)) # ¡Aquí podés editar los valores en vivo!

# 4. Lógica de Despiece (El Corazón)
if st.button("Generar Despiece"):
    # Tomamos los valores editados
    ancho = df.iloc[0, 1]
    alto = df.iloc[1, 1]
    
    st.success(f"Calculando despiece para mueble de {ancho}x{alto}mm...")
    
    # Ejemplo de salida
    st.write("### Listado de Corte Sugerido")
    st.table([
        {"Pieza": "Lateral", "Cant": 2, "Largo": alto, "Ancho": 550},
        {"Pieza": "Piso/Techo", "Cant": 2, "Largo": ancho - (espesor*2), "Ancho": 550},
    ])
