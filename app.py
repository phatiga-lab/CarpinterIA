import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarpinterIA: Master", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Solución Integral")

# --- 1. CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración Taller")
    espesor = st.selectbox("Espesor Estructura", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Zócalo (mm)", value=70)
    
    st.divider()
    st.header("🎨 Diseño")
    veta_frentes = st.radio("Veta en Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)
    
    st.divider()
    st.header("🛠️ Ajustes Finos")
    altura_lateral_forzada = st.selectbox(
        "Altura Lateral Cajón", 
        ["Automático", "100 mm", "120 mm", "150 mm", "180 mm"],
        index=0
    )

# --- 2. DEFINICIÓN DEL MUEBLE ---
st.subheader("1. Dimensiones y Estructura")
c1, c2, c3 = st.columns(3)
with c1:
    ancho = st.number_input("Ancho Total (mm)", value=1300)
    alto = st.number_input("Alto Total (mm)", value=600)
with c2:
    prof = st.number_input("Profundidad (mm)", value=550)
    cant_cajones_total = st.number_input("Total Cajones", value=9)
with c3:
    columnas = st.number_input("Columnas", value=3, min_value=1)

# Feedback
cajones_por_columna = cant_cajones_total / columnas
if cajones_por_columna % 1 == 0:
    st.info(f"✅ Diseño: {columnas} columnas de {int(cajones_por_columna)} cajones.")
else:
    st.warning(f"⚠️ Atención: {cant_cajones_total} cajones no se dividen exacto en {columnas} col.")

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO FINAL ---
if st.button("🚀 PROCESAR PROYECTO COMPLETO", type="primary", use_container_width=True):
    
    piezas = []
    
    # --- A. CÁLCULO DE PIEZAS ---
    alto_lateral = alto
    ancho_interno_total = ancho - (espesor * 2)
    
    # Estructura
    piezas.append({"Pieza": "Lateral Ext.", "Cant": 2, "Largo": alto_lateral, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_interno_total, "Ancho": prof, "Veta": "↔️ Horizontal", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Indistinto", "Mat": f"Fibro {fondo_esp}"})

    # Divisores
    alto_util_modulo = alto - zocalo - (espesor * 2)
    if columnas > 1:
        piezas.append({"Pieza": "Divisor Vert.", "Cant": columnas - 1, "Largo": alto_util_modulo, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})

    # Cajones
    if cant_cajones_total > 0 and cajones_por_columna % 1 == 0:
        cajones_por_col = int(cajones_por_columna)
        descuento_parantes = (columnas - 1) * espesor
        ancho_hueco = (ancho_interno_total - descuento_parantes) / columnas
        
        # Alto Frente
        luz_entre_cajones = 3 
        alto_frente = (alto_util_modulo - ((cajones_por_col - 1) * luz_entre_cajones)) / cajones_por_col
        
        # Altura Lateral (Lógica Automática V2)
        if altura_lateral_forzada != "Automático":
            lat_h = int(altura_lateral_forzada.split(" ")[0])
        else:
            if alto_frente >= 155: lat_h = 150
            elif alto_frente >= 125: lat_h = 120
            elif alto_frente >= 105: lat_h = 100
            else: lat_h = int(alto_frente - 15)

        # Agregar Cajones
        piezas.append({"Pieza": "Frente Cajón", "Cant": cant_cajones_total, "Largo": ancho_hueco-4, "Ancho": alto_frente, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
        piezas.append({"Pieza": "Lat. Cajón", "Cant": cant_cajones_total * 2, "Largo": 500, "Ancho": lat_h, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
        piezas.append({"Pieza": "Contra-Frente", "Cant": cant_cajones_total, "Largo": ancho_hueco-90, "Ancho": lat_h, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
        piezas.append({"Pieza": "Fondo Cajón", "Cant": cant_cajones_total, "Largo": 500, "Ancho": ancho_hueco-90, "Veta": "Indistinto", "Mat": "Fibro 3mm"})

    # --- B. CÁLCULO DE INSUMOS (FERRETERÍA) ---
    # Tornillos 4x50: 4 por unión estructural aprox.
    uniones_estruc = 4 + (columnas * 2) # Laterales + parantes
    tornillos_4x50 = (uniones_estruc * 4) + (cant_cajones_total * 8) # Armado estructura + armado cajones
    
    # Tornillos 3.5x16: 6 tornillos por corredera (3 cajón + 3 lateral) x 2 lados
    tornillos_3x16 = cant_cajones_total * 12 
    
    # Tapacantos (Estimación de perímetro)
    metros_lineales = 0
    for p in piezas:
        if "Melamina" in p["Mat"]: # Solo canteamos melamina vista
            metros_lineales += ((p["Largo"] + p["Ancho"]) * 2 * p["Cant"]) / 1000
    
    canto_pvc = metros_lineales * 1.2 # 20% desperdicio
    
    # --- VISUALIZACIÓN ---
    col_izq, col_der = st.columns([2, 1])
    
    with col_izq:
        st.write("### 📋 Listado de Corte")
        df = pd.DataFrame(piezas)
        # Formato lindo
        st.dataframe(
            df.style.format({"Largo": "{:.1f}", "Ancho": "{:.1f}"}), 
            use_container_width=True, 
            hide_index=True
        )
        
        # Botón de Descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Planilla CSV", csv, "despiece_carpinteria.csv", "text/csv")

    with col_der:
        st.write("### 🛒 Lista de Compras")
        st.info(f"**Tornillos 4x50mm:** {int(tornillos_4x50)} u.")
        if fondo_esp == 18:
            st.info(f"**Tornillos 4x40mm:** {int(tornillos_4x50/1.5)} u. (Fondo)")
        else:
            st.info(f"**Clavos/Grapas:** {int(tornillos_4x50)} u.")
            
        st.success(f"**Tornillos 3.5x16:** {int(tornillos_3x16)} u.")
        st.warning(f"**Correderas 500mm:** {cant_cajones_total} pares")
        st.error(f"**Canto PVC:** {canto_pvc:.1f} m aprox.")
