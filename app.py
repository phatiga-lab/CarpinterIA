import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarpinterIA: V4 Range", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Calculadora con Validación de Alturas")

# --- 1. CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración Taller")
    espesor = st.selectbox("Espesor Estructura", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Zócalo (mm)", value=70, help="0 si es flotante")
    
    st.divider()
    st.header("🎨 Diseño de Cajones")
    veta_frentes = st.radio("Veta en Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)
    
    st.divider()
    st.header("🛠️ Estrategia de Laterales")
    modo_lateral = st.radio(
        "¿Cómo definimos la altura del lateral?",
        ["Automático (Máximo Posible)", "Manual (Forzar Medida)"]
    )
    
    lateral_manual = 0
    if modo_lateral == "Manual (Forzar Medida)":
        lateral_manual = st.number_input(
            "Altura deseada (mm)", 
            min_value=70, 
            max_value=400, 
            step=10, 
            value=150,
            help="El sistema validará si esta medida entra. Si no entra, la bajará automáticamente."
        )

# --- 2. DEFINICIÓN DEL MUEBLE ---
st.subheader("1. Definición de Medidas")
c1, c2, c3 = st.columns(3)
with c1:
    ancho = st.number_input("Ancho Total (mm)", value=900)
    alto = st.number_input("Alto Total (mm)", value=720)
with c2:
    prof = st.number_input("Profundidad (mm)", value=500)
    cant_cajones_total = st.number_input("Total Cajones", value=4)
with c3:
    columnas = st.number_input("Columnas", value=1, min_value=1)

# Feedback visual de distribución
cajones_por_columna = cant_cajones_total / columnas
if cajones_por_columna % 1 != 0:
    st.warning(f"⚠️ {cant_cajones_total} cajones no se pueden repartir igual en {columnas} columnas.")
else:
    st.info(f"✅ Distribución: {int(cajones_por_columna)} cajones por columna.")

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO INTELIGENTE ---
if st.button("🚀 CALCULAR Y VALIDAR RANGOS", type="primary", use_container_width=True):
    
    piezas = []
    alertas = []
    
    # --- A. CÁLCULO ESTRUCTURAL BÁSICO ---
    alto_lateral = alto
    ancho_interno_total = ancho - (espesor * 2)
    alto_util_modulo = alto - zocalo - (espesor * 2) # Espacio real vacío vertical
    
    # Piezas Estructurales
    piezas.append({"Pieza": "Lateral Ext.", "Cant": 2, "Largo": alto_lateral, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_interno_total, "Ancho": prof, "Veta": "↔️ Horizontal", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Indistinto", "Mat": f"Fibro {fondo_esp}"})
    
    if columnas > 1:
        piezas.append({"Pieza": "Divisor Vert.", "Cant": columnas - 1, "Largo": alto_util_modulo, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})

    # --- B. LÓGICA DE CAJONES AVANZADA ---
    if cant_cajones_total > 0 and cajones_por_columna % 1 == 0:
        cajones_por_col = int(cajones_por_columna)
        
        # 1. Calcular dimensiones del hueco
        descuento_parantes = (columnas - 1) * espesor
        ancho_hueco = (ancho_interno_total - descuento_parantes) / columnas
        
        # 2. Calcular Alto de Frente Exacto
        luz_entre_cajones = 3 
        alto_frente = (alto_util_modulo - ((cajones_por_col - 1) * luz_entre_cajones)) / cajones_por_col
        
        # 3. --- VALIDACIÓN DE RANGO DE LATERAL ---
        # Margen técnico: Necesitamos espacio para que el cajón entre y para la corredera abajo.
        # Usualmente: 15mm abajo + 10mm arriba libres = 25mm de descuento mínimo.
        margen_seguridad = 25 
        max_lateral_posible = int(alto_frente - margen_seguridad)
        
        # Definimos el lateral final
        lateral_final = 0
        
        if max_lateral_posible < 70:
            st.error(f"❌ Error Crítico: Los cajones son demasiado bajos ({int(alto_frente)}mm). El espacio útil interno es menor a 70mm. No entra ningún lateral.")
            lateral_final = 0 # Anula el cálculo
        else:
            if modo_lateral == "Automático (Máximo Posible)":
                # Buscamos el estándar más cercano hacia abajo (saltos de 10mm)
                # Ejemplo: Si max es 178, usamos 170.
                lateral_final = (max_lateral_posible // 10) * 10
                alertas.append(f"ℹ️ Modo Auto: Se calculó el lateral máximo posible ({lateral_final}mm) para aprovechar la profundidad.")
            
            else: # Modo Manual
                if lateral_manual <= max_lateral_posible:
                    lateral_final = lateral_manual
                    alertas.append(f"✅ Tu medida manual ({lateral_manual}mm) entra perfectamente.")
                else:
                    # CLAMPING: Si pidió 200 pero entra 150, forzamos 150.
                    lateral_final = (max_lateral_posible // 10) * 10
                    alertas.append(f"⚠️ **Aviso de Corrección:** Pediste {lateral_manual}mm, pero el frente es de solo {int(alto_frente)}mm. Se redujo el lateral a **{lateral_final}mm** (el máximo posible) para que entre.")

        # 4. Generar Piezas de Cajón (Solo si es válido)
        if lateral_final >= 70:
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant_cajones_total, "Largo": ancho_hueco-4, "Ancho": alto_frente, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            piezas.append({"Pieza": "Lat. Cajón", "Cant": cant_cajones_total * 2, "Largo": 500, "Ancho": lateral_final, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
            piezas.append({"Pieza": "Contra-Frente", "Cant": cant_cajones_total, "Largo": ancho_hueco-90, "Ancho": lateral_final, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
            piezas.append({"Pieza": "Fondo Cajón", "Cant": cant_cajones_total, "Largo": 500, "Ancho": ancho_hueco-90, "Veta": "Indistinto", "Mat": "Fibro 3mm"})

    # --- C. MOSTRAR RESULTADOS ---
    col_izq, col_der = st.columns([2, 1])
    
    with col_izq:
        st.write("### 📋 Listado de Corte Optimizado")
        
        # Mostrar las alertas de validación antes de la tabla
        for alerta in alertas:
            if "Error" in alerta: st.error(alerta)
            elif "Aviso" in alerta: st.warning(alerta)
            else: st.success(alerta)

        if lateral_final >= 70 or cant_cajones_total == 0:
            df = pd.DataFrame(piezas)
            st.dataframe(
                df.style.format({"Largo": "{:.1f}", "Ancho": "{:.1f}"}), 
                use_container_width=True, hide_index=True
            )
            
            # Botón CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Bajar CSV", csv, "corte_validado.csv", "text/csv")

    with col_der:
        st.write("### 📊 Análisis Técnico")
        if cant_cajones_total > 0:
            st.metric("Alto de Frente Real", f"{alto_frente:.1f} mm")
            st.metric("Espacio Útil Interno", f"{max_lateral_posible + 25} mm")
            st.metric("Lateral Seleccionado", f"{lateral_final} mm")
            
            progreso = min(lateral_final / (alto_frente if alto_frente > 0 else 1), 1.0)
            st.progress(progreso, text="Ocupación vertical del cajón")
