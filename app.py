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

import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd

# Configuración de página
st.set_page_config(page_title="CarpinterIA Studio", layout="wide")
st.title("🪚 CarpinterIA: Studio")

# 1. Configuración de API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Falta API Key")

# --- SIDEBAR: PARÁMETROS DE TALLER ---
with st.sidebar:
    st.header("📐 Configuración de Taller")
    espesor = st.selectbox("Espesor Placa (mm)", [18, 15], index=0)
    fondo = st.selectbox("Espesor Fondo (mm)", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)

# --- CEREBRO: VISIÓN A DATOS ---
def analizar_imagen_json(imagen):
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prompt de Ingeniería Inversa
    prompt = """
    Eres un software de despiece de muebles. Analiza la imagen.
    Devuelve SOLO un objeto JSON con esta estructura exacta, sin texto extra:
    {
        "mueble": "Nombre del mueble",
        "ancho_total_mm": 0,
        "alto_total_mm": 0,
        "profundidad_mm": 0,
        "cant_cajones": 0,
        "cant_puertas": 0,
        "descripcion": "Breve nota técnica"
    }
    Si no hay medidas explícitas, estima basándote en estándares (ej: alto mesa 750mm).
    """
    try:
        response = model.generate_content([prompt, imagen])
        # Limpieza por si la IA agrega comillas de código
        texto_limpio = response.text.replace("```json", "").replace("```", "")
        return json.loads(texto_limpio)
    except Exception as e:
        return None

# --- INTERFAZ PRINCIPAL ---
col1, col2 = st.columns([1, 2])

with col1:
    st.info("1. Carga tu diseño")
    archivo = st.file_uploader("Subir foto/croquis", type=['jpg', 'png'])
    if archivo:
        img = Image.open(archivo)
        st.image(img, use_column_width=True)

with col2:
    st.info("2. Definición Técnica")
    
    if archivo and st.button("🔨 Procesar Imagen"):
        with st.spinner("Calculando estructura..."):
            datos_ia = analizar_imagen_json(img)
            
            if datos_ia:
                # Guardamos en sesión para que no se borre al editar
                st.session_state['datos_mueble'] = datos_ia
                st.success("¡Estructura detectada!")
            else:
                st.error("No se pudo interpretar la imagen. Intenta de nuevo.")

    # Si ya tenemos datos, mostramos el editor
    if 'datos_mueble' in st.session_state:
        datos = st.session_state['datos_mueble']
        
        # TABLA EDITABLE: El usuario tiene la última palabra
        df_medidas = pd.DataFrame({
            "Parámetro": ["Ancho", "Alto", "Profundidad", "Cajones"],
            "Valor": [datos['ancho_total_mm'], datos['alto_total_mm'], datos['profundidad_mm'], datos['cant_cajones']]
        })
        
        st.write(f"**Detectado:** {datos['mueble']}")
        df_editado = st.data_editor(df_medidas, num_rows="dynamic")
        
        # --- BOTÓN DE DESPIECE FINAL ---
        if st.button("🚀 Generar Listado de Corte"):
            st.write("---")
            st.subheader("📋 Listado de Corte Optimizado")
            
            # Recuperamos valores editados por el usuario
            ancho_final = df_editado.iloc[0, 1]
            alto_final = df_editado.iloc[1, 1]
            prof_final = df_editado.iloc[2, 1]
            
            # LÓGICA DE CARPINTERÍA (Tu fórmula)
            lista_corte = [
                {"Pieza": "Lateral", "Cant": 2, "Largo": alto_final, "Ancho": prof_final, "Material": f"Melamina {espesor}mm", "Veta": "Vertical"},
                {"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_final - (espesor*2), "Ancho": prof_final, "Material": f"Melamina {espesor}mm", "Veta": "Horizontal"},
                {"Pieza": "Fondo", "Cant": 1, "Largo": alto_final-10, "Ancho": ancho_final-10, "Material": f"Fibro {fondo}mm", "Nota": "Clavado"}
            ]
            
            st.table(pd.DataFrame(lista_corte))
            st.balloons()
