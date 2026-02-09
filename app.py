import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="CarpinterIA", page_icon="🪚")

st.title("🪚 CarpinterIA: Inteligencia Artificial")

# 1. Configuración de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Falta configurar la API Key en los Secrets de Streamlit.")

# --- SIDEBAR: PARÁMETROS ---
st.sidebar.header("Reglas de Taller")
espesor = st.sidebar.selectbox("Espesor Placa", [18, 15, 12, 5.5], index=0)
zocalo = st.sidebar.number_input("Zócalo (mm)", value=70)

# --- FUNCIÓN DE ANÁLISIS ROBUSTA ---
def analizar_imagen(imagen_usuario):
    # Lista de intentos ordenados por velocidad vs. estabilidad
    modelos_a_probar = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision']
    
    progreso = st.empty() # Barra de estado vacía
    
    for modelo_nombre in modelos_a_probar:
        try:
            progreso.info(f"Intentando conectar con cerebro: {modelo_nombre}...")
            model = genai.GenerativeModel(modelo_nombre)
            
            prompt = """
            Actúa como un carpintero experto. Analiza esta imagen técnica o croquis.
            1. Identifica qué tipo de mueble es.
            2. Estima el Ancho, Alto y Profundidad (si no hay medidas, usa proporciones asumiendo ancho estándar de 900mm).
            3. Cuenta cantidad de cajones y puertas.
            Responde en formato limpio y directo.
            """
            
            # Generamos contenido
            response = model.generate_content([prompt, imagen_usuario])
            progreso.empty() # Limpiamos mensaje de carga
            return response.text, modelo_nombre
            
        except Exception as e:
            print(f"Fallo con {modelo_nombre}: {e}")
            continue # Si falla, pasa al siguiente modelo de la lista
            
    progreso.error("Todos los intentos fallaron. Verificá tu API Key o Región.")
    return None, None

# --- INTERFAZ PRINCIPAL ---
st.write("### 1. Subir Croquis")
archivo = st.file_uploader("Subí foto o dibujo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Referencia visual", width=300)
    
    if st.button("🔨 Analizar Mueble"):
        with st.spinner("La IA está midiendo y calculando..."):
            resultado, modelo_usado = analizar_imagen(img)
            
            if resultado:
                st.success(f"¡Análisis completado usando {modelo_usado}!")
                st.write("### 🧠 Interpretación:")
                st.info(resultado)
                
                st.write("---")
                st.write("### 2. Ajuste Fino")
                st.write("Usá estos datos para generar tu listado de corte.")
