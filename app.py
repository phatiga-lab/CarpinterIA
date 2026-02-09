import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import pandas as pd

# 1. Configuración Básica
st.set_page_config(page_title="CarpinterIA Taller", page_icon="🪚")
st.title("🪚 CarpinterIA: Taller Digital")

# 2. Configuración API (Blindada)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("⚠️ Falta configurar la API Key.")

# 3. Inicializar Memoria (Para que no se borren los datos al editar)
if 'medidas' not in st.session_state:
    st.session_state['medidas'] = {
        "ancho": 900, 
        "alto": 750, 
        "prof": 450, 
        "cajones": 0,
        "nombre": "Mueble Nuevo"
    }

# --- BARRA LATERAL (Insumos) ---
with st.sidebar:
    st.header("⚙️ Configuración Materiales")
    espesor = st.selectbox("Placa Estructura", [18, 15, 25], index=0)
    fondo = st.selectbox("Placa Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)

# --- PASO 1: CARGA Y ANÁLISIS ---
st.header("1. Referencia Visual")
archivo = st.file_uploader("Subí tu diseño aquí", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=300)
    
    # Botón para llamar a la IA
    if st.button("🔍 Analizar Medidas con IA"):
        with st.spinner("Consultando a Gemini 2.0..."):
            try:
                # Usamos el modelo que sabemos que funciona
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                prompt = """
                Analiza este mueble para despiece.
                Estima Ancho, Alto, Profundidad en milimetros.
                Cuenta los cajones.
                Devuelve SOLO JSON: {"ancho": 0, "alto": 0, "prof": 0, "cajones": 0, "nombre": "texto"}
                """
                
                response = model.generate_content([prompt, img])
                texto_limpio = response.text.replace("```json", "").replace("```", "")
                datos = json.loads(texto_limpio)
                
                # Guardamos en memoria
                st.session_state['medidas'].update(datos)
                st.success("¡Medidas detectadas! Podés corregirlas abajo.")
                st.rerun() # Recarga la página para mostrar los números nuevos
                
            except Exception as e:
                st.error(f"Error analizando: {e}")

st.markdown("---")

# --- PASO 2: EDICIÓN MANUAL (Siempre visible) ---
st.header("2. Definición de Medidas (Editable)")
st.info("Acá podés corregir lo que la IA calculó mal. Estos son los números REALES para el corte.")

# Usamos columnas solo para los inputs numéricos para que quede ordenado
c1, c2 = st.columns(2)

with c1:
    ancho_final = st.number_input("Ancho Final (mm)", value=int(st.session_state['medidas']['ancho']))
    alto_final = st.number_input("Alto Final (mm)", value=int(st.session_state['medidas']['alto']))

with c2:
    prof_final = st.number_input("Profundidad (mm)", value=int(st.session_state['medidas']['prof']))
    cant_cajones = st.number_input("Cant. Cajones", value=int(st.session_state['medidas']['cajones']))

st.markdown("---")

# --- PASO 3: BOTÓN DE ACCIÓN (Fuera de columnas, siempre visible) ---
st.header("3. Resultado")

# Este botón está en la raíz del código, IMPOSIBLE que no aparezca
if st.button("🚀 CALCULAR DESPIECE FINAL", type="primary", use_container_width=True):
    
    st.write(f"### 📋 Listado de Corte: {st.session_state['medidas']['nombre']}")
    
    # Lógica Matemática
    alto_lateral = alto_final # Lateral va hasta el piso
    ancho_techopiso = ancho_final - (espesor * 2) # Descuento de espesores
    
    # Armado de la lista
    piezas = []
    
    # 1. Laterales
    piezas.append({
        "Pieza": "Lateral", 
        "Cantidad": 2, 
        "Largo (veta)": alto_lateral, 
        "Ancho": prof_final, 
        "Material": f"Melamina {espesor}mm"
    })
    
    # 2. Piso y Techo
    piezas.append({
        "Pieza": "Techo/Piso", 
        "Cantidad": 2, 
        "Largo": ancho_techopiso, 
        "Ancho": prof_final, 
        "Material": f"Melamina {espesor}mm"
    })
    
    # 3. Fondo
    piezas.append({
        "Pieza": "Fondo", 
        "Cantidad": 1, 
        "Largo": alto_final - 15, 
        "Ancho": ancho_final - 15, 
        "Material": f"Fibro {fondo}mm"
    })
    
    # 4. Cajones (Si corresponde)
    if cant_cajones > 0:
        alto_frente = (alto_final - zocalo - 30) / cant_cajones
        piezas.append({
            "Pieza": "Frente Cajón", 
            "Cantidad": cant_cajones, 
            "Largo": ancho_final - 4, 
            "Ancho": int(alto_frente), 
            "Material": f"Melamina {espesor}mm"
        })
        st.info(f"💡 Se calcularon {cant_cajones} cajones con frentes de {int(alto_frente)}mm de alto.")

    # Mostrar Tabla
    df = pd.DataFrame(piezas)
    st.dataframe(df, use_container_width=True)
    
    st.success("✅ ¡Cálculo completado! Copiá esta tabla para el aserradero.")
