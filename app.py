import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarpinterIA: Distribución", page_icon="📐", layout="wide")
st.title("📐 CarpinterIA: Distribución Inteligente")

# --- 1. CONFIGURACIÓN GLOBAL ---
with st.sidebar:
    st.header("⚙️ Materiales")
    espesor = st.selectbox("Espesor Estructura", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Zócalo (mm)", value=70)
    
    st.divider()
    st.header("🎨 Diseño")
    veta_frentes = st.radio("Veta en Frentes de Cajón", ["↔️ Horizontal", "↕️ Vertical"], index=0)

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
    # AQUÍ ESTÁ LA SOLUCIÓN: Columnas
    columnas = st.number_input("Cantidad de Columnas", value=3, min_value=1, help="Si ponés 1, apila todo. Si ponés 3, divide el ancho en 3 módulos.")
    
# Lógica de distribución visual para el usuario
cajones_por_columna = cant_cajones_total / columnas

if cajones_por_columna % 1 != 0:
    st.warning(f"⚠️ Atención: {cant_cajones_total} cajones no se pueden dividir exactamente en {columnas} columnas.")
else:
    st.info(f"💡 Interpretación: El mueble tendrá **{columnas} columnas** con **{int(cajones_por_columna)} cajones** cada una.")

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO ---
if st.button("🚀 CALCULAR DESPIECE DETALLADO", type="primary", use_container_width=True):
    
    piezas = []
    alertas = []

    # --- A. CÁLCULOS ESTRUCTURALES ---
    
    # 1. Laterales Externos (Siempre van hasta el piso en este modelo)
    alto_lateral = alto
    piezas.append({"Pieza": "Lateral Externo", "Cant": 2, "Largo": alto_lateral, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
    
    # 2. Piso y Techo (Van entre laterales externos)
    # Descuento: Ancho total - 2 espesores laterales
    ancho_interno_total = ancho - (espesor * 2)
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_interno_total, "Ancho": prof, "Veta": "↔️ Horizontal", "Mat": f"Melamina {espesor}"})
    
    # 3. Parantes / Divisores Verticales (Si hay más de 1 columna)
    # Van entre piso y techo.
    espacio_vertical_interno = alto - (espesor * 2) - zocalo # Asumiendo zócalo independiente o integrado
    # Ajuste: Si el lateral baja al piso, el espacio interior es Alto - Zocalo (si hay) - Techo - Piso?
    # Simplificación estándar: Laterales al piso. Piso elevado a nivel de zocalo. Techo arriba.
    # Espacio útil vertical = Alto - Zocalo - Espesor(Techo) - Espesor(Piso)
    alto_util_modulo = alto - zocalo - (espesor * 2)
    
    if columnas > 1:
        cant_parantes = columnas - 1
        piezas.append({"Pieza": "Divisor Vertical", "Cant": cant_parantes, "Largo": alto_util_modulo, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
        
    # 4. Fondo
    piezas.append({"Pieza": "Fondo", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Indistinto", "Mat": f"Fibro {fondo_esp}"})

    # --- B. CÁLCULO DE CAJONES ---
    
    if cant_cajones_total > 0:
        # 1. Calcular Ancho de cada Módulo (Hueco)
        # Ancho interno total - (espesor de parantes)
        descuento_parantes = (columnas - 1) * espesor
        ancho_libre_total = ancho_interno_total - descuento_parantes
        ancho_hueco = ancho_libre_total / columnas
        
        # 2. Calcular Alto de cada Frente
        # Alto útil / cantidad de cajones por columna - (luces)
        luz_entre_cajones = 3 # mm
        alto_frente = (alto_util_modulo - (cajones_por_columna * luz_entre_cajones)) / cajones_por_columna
        
        # 3. Validar si entra un lateral de 150mm
        # El espacio útil del cajón suele ser Frente - 30mm (margen)
        espacio_interno_cajon = alto_frente - 15 
        
        altura_lateral_sugerida = 0
        if espacio_interno_cajon >= 160:
            altura_lateral_sugerida = 150 # Estándar
        elif espacio_interno_cajon >= 110:
            altura_lateral_sugerida = 100 # Bajo
        else:
            altura_lateral_sugerida = int(espacio_interno_cajon - 10)
            alertas.append(f"⚠️ **Cuidado:** Los cajones son muy bajos ({int(alto_frente)}mm de frente). No entra un lateral estándar de 150mm. Se sugiere cortar laterales a {altura_lateral_sugerida}mm.")

        # AGREGAR PIEZAS DE CAJÓN
        
        # Frentes
        # Ancho frente = Ancho hueco - luz lateral (ej 2mm por lado = 4mm)
        ancho_frente_real = ancho_hueco - 4 
        # Si es cajón superpuesto (tapa los laterales), el cálculo cambia, pero asumimos sistema encajonado estándar o ajustado.
        # Para simplificar en esta etapa: Frente cubre hueco - luces.
        
        piezas.append({
            "Pieza": "Frente Cajón", 
            "Cant": cant_cajones_total, 
            "Largo": ancho_frente_real, 
            "Ancho": alto_frente, 
            "Veta": veta_frentes, 
            "Mat": f"Melamina {espesor}"
        })
        
        # Laterales de Cajón
        piezas.append({
            "Pieza": "Lat. Cajón", 
            "Cant": cant_cajones_total * 2, 
            "Largo": 500, # Profundidad estándar de corredera
            "Ancho": altura_lateral_sugerida, 
            "Veta": "↔️ Horizontal", 
            "Mat": "Blanca 18mm"
        })
        
        # Contra-frente y Fondo de cajón
        ancho_contrafrente = ancho_hueco - 90 # 18+18 laterales + 13+13 correderas + margen = aprox 90
        piezas.append({
            "Pieza": "Contra-Frente", 
            "Cant": cant_cajones_total, 
            "Largo": ancho_contrafrente, 
            "Ancho": altura_lateral_sugerida, 
            "Veta": "↔️ Horizontal", 
            "Mat": "Blanca 18mm"
        })
        
        piezas.append({
            "Pieza": "Fondo Cajón", 
            "Cant": cant_cajones_total, 
            "Largo": 500, 
            "Ancho": ancho_contrafrente, 
            "Veta": "Indistinto", 
            "Mat": "Fibro 3mm"
        })

    # --- MOSTRAR RESULTADOS ---
    st.write("### 📋 Listado de Corte Optimizado")
    
    if alertas:
        for a in alertas:
            st.error(a)
            
    df = pd.DataFrame(piezas)
    # Formatear números para que no muestren decimales feos
    st.dataframe(df.style.format({"Largo": "{:.1f}", "Ancho": "{:.1f}"}), use_container_width=True)
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.success(f"**Ancho libre por columna:** {ancho_hueco:.1f} mm")
    with col_info2:
        if cant_cajones_total > 0:
            st.success(f"**Alto de Frente calculado:** {alto_frente:.1f} mm")
