import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd
import time

# 1. Configuración de página
st.set_page_config(page_title="CarpinterIA Taller", page_icon="🪚")
st.title("🪚 CarpinterIA: Taller Digital")

# 2. Configuración API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Falta configurar la API Key.")

# 3. Inicializar Memoria
if 'medidas' not in st.session_state:
    st.session_state['medidas'] = {
        "ancho": 900, "alto": 750, "prof": 450, "cajones": 0, "nombre": "Mueble Nuevo"
    }

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Materiales")
    espesor = st.selectbox("Placa Estructura", [18, 15, 25], index=0)
    fondo = st.selectbox("Placa Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)

# --- FUNCIÓN: FUERZA BRUTA INTELIGENTE ---
def intentar_analisis_robusto(imagen):
    # Lista de todos los nombres posibles para cuentas gratuitas
    # El código probará uno por uno hasta que uno funcione
    modelos_posibles = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-pro-vision" # El clásico, si todo lo nuevo falla
    ]
    
    prompt = """
    Analiza este mueble. Estima Ancho, Alto, Profundidad en mm y cuenta cajones.
    Devuelve SOLO JSON: {"ancho": 0, "alto": 0, "prof": 0, "cajones": 0, "nombre": "texto"}
    """
    
    barra = st.progress(0)
    estado = st.empty()
    
    for i, nombre_modelo in enumerate(modelos_posibles):
        try:
            estado.text(f"Intentando con motor: {nombre_modelo}...")
            barra.progress((i + 1) / len(modelos_posibles))
            
            # Configuramos el modelo actual del bucle
            model = genai.GenerativeModel(nombre_modelo)
            
            # Intentamos generar
            response = model.generate_content([prompt, imagen])
            
            # Si llegamos acá, funcionó! Limpiamos y devolvemos
            texto_limpio = response.text.replace("```json", "").replace("```", "")
            estado.empty()
            barra.empty()
            st.success(f"✅ Conectado con éxito usando: {nombre_modelo}")
            return json.loads(texto_limpio)
            
        except Exception as e:
            # Si falla, seguimos al siguiente sin molestar al usuario
            time.sleep(0.5)
            continue
            
    estado.error("❌ Todos los modelos fallaron. Revisá tu API Key o intentá más tarde.")
    return None

# --- INTERFAZ ---
st.header("1. Referencia Visual")
archivo = st.file_uploader("Subí tu diseño aquí", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=300)
    
    if st.button("🔍 Analizar Medidas"):
        with st.spinner("Buscando el mejor modelo disponible..."):
            datos = intentar_analisis_robusto(img)
            
            if datos:
                st.session_state['medidas'].update(datos)
                st.rerun()

st.markdown("---")

# --- EDICIÓN Y CÁLCULO ---
st.header("2. Definición (Editable)")
c1, c2 = st.columns(2)
with c1:
    ancho_f = st.number_input("Ancho (mm)", value=int(st.session_state['medidas']['ancho']))
    alto_f = st.number_input("Alto (mm)", value=int(st.session_state['medidas']['alto']))
with c2:
    prof_f = st.number_input("Prof. (mm)", value=int(st.session_state['medidas']['prof']))
    cajones = st.number_input("Cajones", value=int(st.session_state['medidas']['cajones']))

if st.button("🚀 CALCULAR DESPIECE FINAL", type="primary"):
    st.write(f"### 📋 Corte para: {st.session_state['medidas']['nombre']}")
    
    # Lógica simple de corte
    piezas = [
        {"Pieza": "Lateral", "Cant": 2, "Largo": alto_f, "Ancho": prof_f, "Mat": f"Melamina {espesor}"},
        {"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_f - (espesor*2), "Ancho": prof_f, "Mat": f"Melamina {espesor}"},
        {"Pieza": "Fondo", "Cant": 1, "Largo": alto_f-15, "Ancho": ancho_f-15, "Mat": f"Fibro {fondo}"}
    ]
    if cajones > 0:
        alto_frente = (alto_f - zocalo - 30) / cajones
        piezas.append({"Pieza": "Frente Cajón", "Cant": cajones, "Largo": ancho_f-4, "Ancho": int(alto_frente), "Mat": f"Melamina {espesor}"})
        
    st.dataframe(pd.DataFrame(piezas), use_container_width=True)
