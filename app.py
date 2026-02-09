import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarpinterIA: V5 Full", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Calculadora Completa")

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
            min_value=70, max_value=400, step=10, value=150
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

# Feedback
cajones_por_columna = cant_cajones_total / columnas
if cajones_por_columna % 1 != 0:
    st.warning(f"⚠️ {cant_cajones_total} cajones no se reparten igual en {columnas} columnas.")

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO ---
if st.button("🚀 CALCULAR TODO (Despiece + Compras)", type="primary", use_container_width=True):
    
    piezas = []
    alertas = []
    
    # --- A. CÁLCULO ESTRUCTURAL ---
    alto_lateral = alto
    ancho_interno_total = ancho - (espesor * 2)
    alto_util_modulo = alto - zocalo - (espesor * 2)
    
    piezas.append({"Pieza": "Lateral Ext.", "Cant": 2, "Largo": alto_lateral, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_interno_total, "Ancho": prof, "Veta": "↔️ Horizontal", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Indistinto", "Mat": f"Fibro {fondo_esp}"})
    
    if columnas > 1:
        piezas.append({"Pieza": "Divisor Vert.", "Cant": columnas - 1, "Largo": alto_util_modulo, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})

    # --- B. LÓGICA DE CAJONES ---
    if cant_cajones_total > 0 and cajones_por_columna % 1 == 0:
        cajones_por_col = int(cajones_por_columna)
        descuento_parantes = (columnas - 1) * espesor
        ancho_hueco = (ancho_interno_total - descuento_parantes) / columnas
        luz_entre_cajones = 3 
        alto_frente = (alto_util_modulo - ((cajones_por_col - 1) * luz_entre_cajones)) / cajones_por_col
        
        # Validación de Altura
        margen_seguridad = 25 
        max_lateral_posible = int(alto_frente - margen_seguridad)
        lateral_final = 0
        
        if max_lateral_posible < 70:
            st.error(f"❌ Los cajones son muy bajos ({int(alto_frente)}mm). No entran laterales.")
        else:
            if modo_lateral == "Automático (Máximo Posible)":
                lateral_final = (max_lateral_posible // 10) * 10
                alertas.append(f"ℹ️ Lateral calculado: {lateral_final}mm")
            else: 
                if lateral_manual <= max_lateral_posible:
                    lateral_final = lateral_manual
                else:
                    lateral_final = (max_lateral_posible // 10) * 10
                    alertas.append(f"⚠️ Se redujo el lateral a {lateral_final}mm para que entre.")

        # Piezas Cajón
        if lateral_final >= 70:
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant_cajones_total, "Largo": ancho_hueco-4, "Ancho": alto_frente, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            piezas.append({"Pieza": "Lat. Cajón", "Cant": cant_cajones_total * 2, "Largo": 500, "Ancho": lateral_final, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
            piezas.append({"Pieza": "Contra-Frente", "Cant": cant_cajones_total, "Largo": ancho_hueco-90, "Ancho": lateral_final, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
            piezas.append({"Pieza": "Fondo Cajón", "Cant": cant_cajones_total, "Largo": 500, "Ancho": ancho_hueco-90, "Veta": "Indistinto", "Mat": "Fibro 3mm"})

    # --- C. CÁLCULO DE INSUMOS (RECUPERADO) ---
    tornillos_4x50 = (len(piezas) * 4) + (cant_cajones_total * 8) # Estructura + Armado Cajones
    tornillos_3x16 = cant_cajones_total * 12 # 6 por guía
    correderas = cant_cajones_total
    
    metros_canto = 0
    for p in piezas:
        if "Melamina" in p["Mat"]: 
            # Perímetro x Cantidad / 1000 para pasar a metros
            metros_canto += ((p["Largo"] + p["Ancho"]) * 2 * p["Cant"]) / 1000
    
    canto_pvc = metros_canto * 1.2 # 20% desperdicio

    # --- D. MOSTRAR RESULTADOS ---
    col_izq, col_der = st.columns([2, 1])
    
    with col_izq:
        st.write("### 📋 Listado de Corte")
        for a in alertas: st.info(a)
            
        df = pd.DataFrame(piezas)
        st.dataframe(df.style.format({"Largo": "{:.1f}", "Ancho": "{:.1f}"}), use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV", csv, "despiece_completo.csv", "text/csv")

    with col_der:
        st.write("### 🛒 Lista de Compras")
        st.success(f"**Tornillos 4x50mm:** {int(tornillos_4x50)} u.")
        if fondo_esp == 18:
            st.success(f"**Tornillos 4x40mm:** {int(tornillos_4x50/2)} u.")
        else:
            st.info(f"**Clavos/Grapas:** {int(tornillos_4x50)} u.")
            
        st.warning(f"**Tornillos 3.5x16:** {int(tornillos_3x16)} u.")
        st.warning(f"**Correderas 500mm:** {correderas} pares")
        st.error(f"**Canto PVC:** {canto_pvc:.1f} m (incluye 20% desp.)")
        
        if cant_cajones_total > 0:
            st.markdown("---")
            st.write("**Datos Técnicos:**")
            st.caption(f"Alto Frente: {alto_frente:.1f}mm")
            st.caption(f"Lateral Usado: {lateral_final}mm")
