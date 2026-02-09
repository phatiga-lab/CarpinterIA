import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración limpia
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Usamos el nombre más básico posible
model = genai.GenerativeModel('gemini-pro-vision') 
# Si el anterior falla, probá con 'gemini-1.5-flash' (sin el models/)
st.title("🪚 CarpinterIA: Prototipo V0.20")

# 2. Selector de archivo (Foto del mueble o croquis)
archivo = st.file_uploader("Subí tu croquis o foto de referencia", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Imagen cargada correctamente", width=300)
    
    # 3. Botón para activar el análisis
    if st.button("Analizar con CarpinterIA"):
        with st.spinner("Interpretando..."):
            # Le pedimos a la IA que extraiga los datos básicos
            prompt = "Analiza este mueble. Indicame Ancho, Alto y cantidad de cajones. Si no hay medidas, estimá proporciones."
            response = model.generate_content([prompt, img])
            
            st.write("### 🧠 Resultados del análisis:")
            st.write(response.text)

st.write("---")
st.info("Una vez que la IA analice la foto, usaremos los datos para el despiece técnico.")
