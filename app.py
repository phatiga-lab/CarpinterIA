import streamlit as st
import pandas as pd
from PIL import Image
import google.generativeai as genai

# Configuración visual
st.set_page_config(page_title="CarpinterIA: Calculadora", page_icon="🪚")
st.title("🪚 CarpinterIA: Calculadora de Corte")

# --- 1. CONFIGURACIÓN LATERAL (SIEMPRE VISIBLE) ---
with st.sidebar:
    st.header("⚙️ Materiales")
    espesor = st.selectbox("Espesor Placa (mm)", [18, 15, 25], index=0)
    fondo = st.selectbox("Espesor Fondo (mm)", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)
    
    st.divider()
    st.caption("Estado del Sistema:")
    # Intento silencioso de conexión (no rompe la app si falla)
    api_status = "🔴 Desconectado"
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_status = "🟢 API Key Detectada"
    except:
        api_status = "🔴 Falta API Key"
    st.text(api_status)

# --- 2. ZONA DE IA (OPCIONAL Y COLAPSABLE) ---
with st.expander("📸 Cargar Croquis / Foto (Opcional)"):
    archivo = st.file_uploader("Subí una imagen para intentar leer medidas", type=['jpg', 'png'])
    if archivo:
        img = Image.open(archivo)
        st.image(img, width=200)
        
        if st.button("Tratar de leer medidas con IA"):
            try:
                # Intento con el modelo más básico y estable
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(["Dime solo el ancho y alto estimado de este mueble en mm. Formato: Ancho: X, Alto: Y", img])
                st.info(f"🤖 La IA sugiere: {response.text}")
            except Exception as e:
                st.warning(f"La IA no pudo leer la foto (Error de Google), pero podés cargar los datos abajo manualmente.\nDetalle: {e}")

# --- 3. ZONA DE TRABAJO (LO IMPORTANTE) ---
st.subheader("📐 Definición de Medidas")
st.write("Ingresá las medidas finales del mueble para generar el corte.")

col1, col2 = st.columns(2)

with col1:
    # Usamos session_state para que no se borren los números
    ancho = st.number_input("Ancho Final (mm)", value=900, step=10)
    alto = st.number_input("Alto Final (mm)", value=750, step=10)

with col2:
    prof = st.number_input("Profundidad (mm)", value=450, step=10)
    cajones = st.number_input("Cantidad de Cajones", value=0, step=1)

st.markdown("---")

# --- 4. BOTÓN DE CÁLCULO (GARANTIZADO) ---
if st.button("🚀 CALCULAR DESPIECE AHORA", type="primary", use_container_width=True):
    
    # Lógica de Carpintería
    alto_lateral = alto
    ancho_piso = ancho - (espesor * 2)
    
    # Lista de Piezas
    piezas = [
        {"Pieza": "Lateral", "Cant": 2, "Medidas": f"{alto_lateral} x {prof} mm", "Material": f"Melamina {espesor}"},
        {"Pieza": "Techo/Piso", "Cant": 2, "Medidas": f"{ancho_piso} x {prof} mm", "Material": f"Melamina {espesor}"},
        {"Pieza": "Fondo", "Cant": 1, "Medidas": f"{alto-15} x {ancho-15} mm", "Material": f"Fibro {fondo}"}
    ]
    
    # Lógica de Cajones
    if cajones > 0:
        alto_frente = (alto - zocalo - 30) / cajones
        piezas.append({"Pieza": "Frente Cajón", "Cant": cajones, "Medidas": f"{int(alto_frente)} x {ancho-4} mm", "Material": f"Melamina {espesor}"})
        # Laterales de cajón (estándar)
        piezas.append({"Pieza": "Lat. Cajón", "Cant": cajones*2, "Medidas": f"500 x 150 mm", "Material": "Melamina Blanca"})

    # Mostrar Resultados
    st.success("✅ Despiece Generado Exitosamente")
    df = pd.DataFrame(piezas)
    st.dataframe(df, use_container_width=True)
    
    st.caption("Nota: Las medidas de cajones son sugeridas. Verificar luz de correderas.")
