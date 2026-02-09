import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarpinterIA: Distribución", page_icon="📐", layout="wide")
st.title("📐 CarpinterIA: Distribución Inteligente")

# --- 1. CONFIGURACIÓN GLOBAL ---
with st.sidebar:
    st.header("⚙️ Materiales")
    espesor = st.selectbox("Espesor Estructura", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Zócalo (mm)", value=70, help="Poné 0 si es mueble colgante")
    
    st.divider()
    st.header("🎨 Diseño de Cajones")
    veta_frentes = st.radio("Veta en Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)
    
    st.divider()
    st.header("🛠️ Forzar Medidas")
    # AQUÍ ESTÁ LA SOLUCIÓN: VOS DECIDÍS LA ALTURA
    altura_lateral_forzada = st.selectbox(
        "Altura Lateral de Cajón", 
        ["Automático", "100 mm", "120 mm", "150 mm", "180 mm", "200 mm"],
        index=0,
        help="Si ponés Automático, el sistema decide según el espacio."
    )

# --- 2. DEFINICIÓN DEL MUEBLE ---
st.subheader("1. Dimensiones y Distribución")

c1, c2, c3 = st.columns(3)
with c1:
    ancho = st.number_input("Ancho Total (mm)", value=1300)
    alto = st.number_input("Alto Total (mm)", value=600)
with c2:
    prof = st.number_input("Profundidad (mm)", value=550)
    cant_cajones_total = st.number_input("Total de Cajones", value=9)
with c3:
    columnas = st.number_input("Cantidad de Columnas", value=3, min_value=1)

# Feedback visual inmediato
cajones_por_columna = cant_cajones_total / columnas
if cajones_por_columna % 1 == 0:
    st.info(f"💡 Estructura: **{columnas} columnas** de **{int(cajones_por_columna)} cajones** cada una.")
else:
    st.warning(f"⚠️ {cant_cajones_total} cajones no se reparten igual en {columnas} columnas.")

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO ---
if st.button("🚀 CALCULAR DESPIECE DETALLADO", type="primary", use_container_width=True):
    
    piezas = []
    
    # --- A. CÁLCULOS ESTRUCTURALES ---
    alto_lateral = alto
    ancho_interno_total = ancho - (espesor * 2)
    
    # 1. Estructura Básica
    piezas.append({"Pieza": "Lateral Externo", "Cant": 2, "Largo": alto_lateral, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_interno_total, "Ancho": prof, "Veta": "↔️ Horizontal", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Indistinto", "Mat": f"Fibro {fondo_esp}"})

    # 2. Divisores (Parantes)
    alto_util_modulo = alto - zocalo - (espesor * 2)
    if columnas > 1:
        piezas.append({"Pieza": "Divisor Vertical", "Cant": columnas - 1, "Largo": alto_util_modulo, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})

    # --- B. CÁLCULO DE CAJONES ---
    if cant_cajones_total > 0 and cajones_por_columna % 1 == 0:
        cajones_por_col = int(cajones_por_columna)
        
        # Ancho de Frente
        descuento_parantes = (columnas - 1) * espesor
        ancho_libre_total = ancho_interno_total - descuento_parantes
        ancho_hueco = ancho_libre_total / columnas
        ancho_frente_real = ancho_hueco - 4 # 2mm luz por lado
        
        # Alto de Frente
        luz_entre_cajones = 3 
        alto_frente = (alto_util_modulo - ((cajones_por_col - 1) * luz_entre_cajones)) / cajones_por_col
        
        # --- LÓGICA DE ALTURA LATERAL (CORREGIDA) ---
        altura_final_lat = 0
        
        if altura_lateral_forzada != "Automático":
            # Si el usuario mandó una medida, usamos esa
            altura_final_lat = int(altura_lateral_forzada.split(" ")[0])
        else:
            # Lógica Automática (Más permisiva ahora)
            # Si el frente mide 160, entra un lateral de 150 (sobran 10mm)
            if alto_frente >= 155:
                altura_final_lat = 150
            elif alto_frente >= 125:
                altura_final_lat = 120
            elif alto_frente >= 105:
                altura_final_lat = 100
            else:
                altura_final_lat = int(alto_frente - 15)

        # Agregar piezas de cajón
        piezas.append({
            "Pieza": "Frente Cajón", "Cant": cant_cajones_total, 
            "Largo": ancho_frente_real, "Ancho": alto_frente, 
            "Veta": veta_frentes, "Mat": f"Melamina {espesor}"
        })
        
        piezas.append({
            "Pieza": "Lat. Cajón", "Cant": cant_cajones_total * 2, 
            "Largo": 500, "Ancho": altura_final_lat, 
            "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"
        })
        
        ancho_contrafrente = ancho_hueco - 90 
        piezas.append({
            "Pieza": "Contra-Frente", "Cant": cant_cajones_total, 
            "Largo": ancho_contrafrente, "Ancho": altura_final_lat, 
            "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"
        })
        
        piezas.append({
            "Pieza": "Fondo Cajón", "Cant": cant_cajones_total, 
            "Largo": 500, "Ancho": ancho_contrafrente, 
            "Veta": "Indistinto", "Mat": "Fibro 3mm"
        })
        
        st.success(f"✅ Cálculo Base: Frente de **{alto_frente:.1f} mm** -> Lateral seleccionado de **{altura_final_lat} mm**.")

    # --- MOSTRAR ---
    st.write("### 📋 Listado de Corte Final")
    df = pd.DataFrame(piezas)
    st.dataframe(df.style.format({"Largo": "{:.1f}", "Ancho": "{:.1f}"}), use_container_width=True)
