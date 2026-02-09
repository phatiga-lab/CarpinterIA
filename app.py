import streamlit as st
import google.generativeai as genai
from PIL import Image

import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Forzar el uso de la versión estable de la API
# Esto evita el error de "v1beta not found"
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 2. Definir el modelo sin prefijos y con un bloque de error detallado
try:
    # Probamos con el nombre más estándar posible
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prueba rápida de texto para validar la llave
    test = model.generate_content("test")
    st.sidebar.success("✅ Conexión Exitosa")
except Exception as e:
    st.sidebar.error(f"❌ Error: {e}")
    # Si falla, intentamos con el modelo Pro como backup automático
    model = genai.GenerativeModel('gemini-1.5-pro')

# OPCIONAL: Si querés ver si la llave funciona, agregá esto:
try:
    # Intento de respuesta simple para verificar conexión
    test_response = model.generate_content("Hola")
    st.sidebar.success("✅ Conexión con Google AI establecida")
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {e}")
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
