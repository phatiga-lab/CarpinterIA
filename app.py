import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="CarpinterIA", page_icon="🪚")
st.title("🪚 CarpinterIA: Versión 2.0")

# 1. Configuración de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Falta configurar la API Key en los Secrets.")

# --- SIDEBAR ---
st.sidebar.header("Reglas de Taller")
espesor = st.sidebar.selectbox("Espesor Placa", [18, 15, 12, 5.5], index=0)
zocalo = st.sidebar.number_input("Zócalo (mm)", value=70)

# --- FUNCIÓN DE ANÁLISIS ---
def analizar_imagen(imagen_usuario):
    # ACTUALIZADO: Usamos los modelos que vimos en tu diagnóstico
    modelos_a_probar = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.0-flash-lite']
    
    progreso = st.empty()
    
    for modelo_nombre in modelos_a_probar:
        try:
            progreso.info(f"Intentando conectar con: {modelo_nombre}...")
            model = genai.GenerativeModel(modelo_nombre)
            
            prompt = """
            Actúa como un carpintero experto. Analiza esta imagen técnica o croquis.
            1. Identifica qué tipo de mueble es.
            2. Estima el Ancho, Alto y Profundidad (si no hay medidas, usa proporciones).
            3. Lista los herrajes necesarios (cantidad de bisagras, correderas, etc).
            Responde en formato lista simple.
            """
            
            response = model.generate_content([prompt, imagen_usuario])
            progreso.empty()
            return response.text, modelo_nombre
            
        except Exception as e:
            # Si falla, probamos el siguiente de la lista
            continue 
            
    progreso.error("Error de conexión con todos los modelos. Verificá tu API Key.")
    return None, None

# --- INTERFAZ ---
st.write("### 1. Subir Croquis")
archivo = st.file_uploader("Subí foto o dibujo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Referencia visual", width=300)
    
    if st.button("🔨 Analizar Mueble"):
        with st.spinner("La IA está midiendo..."):
            resultado, modelo_usado = analizar_imagen(img)
            
            if resultado:
                st.success(f"¡Análisis completado usando {modelo_usado}!")
                st.info(resultado)
                st.write("---")
                st.warning("⚠️ Recordá verificar las medidas en obra antes de cortar.")
