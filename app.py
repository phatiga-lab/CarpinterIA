import streamlit as st
import pandas as pd

st.set_page_config(page_title="CarpinterIA: Universal", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Diseño Universal (V6)")

# --- 1. CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Materiales y Herrajes")
    espesor = st.selectbox("Espesor Estructura", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Zócalo (mm)", value=70)
    
    st.divider()
    st.header("🎨 Vetas y Terminación")
    veta_frentes = st.radio("Veta (Frentes/Puertas)", ["↔️ Horizontal", "↕️ Vertical"], index=1)
    
    st.divider()
    st.info("ℹ️ Los estantes se calculan con 20mm de retiro frontal para que cierre la puerta.")

# --- 2. DEFINICIÓN DEL MUEBLE ---
st.subheader("1. Dimensiones del Casco")
c1, c2, c3 = st.columns(3)
with c1:
    ancho = st.number_input("Ancho Total (mm)", value=900)
    alto = st.number_input("Alto Total (mm)", value=1800)
with c2:
    prof = st.number_input("Profundidad (mm)", value=550)
    columnas = st.number_input("Columnas Verticales", value=1, min_value=1)
with c3:
    # CONFIGURACIÓN INTERNA
    st.write("Componentes:")
    cant_cajones = st.number_input("Cant. Cajones", value=0)
    cant_puertas = st.number_input("Cant. Puertas", value=2)
    cant_estantes = st.number_input("Cant. Estantes Móviles", value=3)

# Lógica de Altura de Puerta (Si hay puertas)
alto_puerta = 0
if cant_puertas > 0:
    st.markdown("---")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.write("📏 **Configuración de Puertas**")
        tipo_cobertura = st.radio("Altura de Puertas:", ["Cubren todo el frente", "Definir altura manual"], index=0)
    with c_p2:
        if tipo_cobertura == "Definir altura manual":
            alto_puerta = st.number_input("Alto de la Puerta (mm)", value=int(alto-zocalo))
        else:
            alto_puerta = alto - zocalo # Por defecto cubre todo menos zocalo
            st.info(f"Altura calculada: {alto_puerta}mm")

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO ---
if st.button("🚀 CALCULAR PROYECTO COMPLETO", type="primary", use_container_width=True):
    
    piezas = []
    compras = [] # Nueva lista para el detalle de herrajes
    
    # --- A. ESTRUCTURA (CASCO) ---
    ancho_interno_total = ancho - (espesor * 2)
    alto_util = alto - zocalo - (espesor * 2)
    
    piezas.append({"Pieza": "Lateral Ext.", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_interno_total, "Ancho": prof, "Veta": "↔️ Horizontal", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Indistinto", "Mat": f"Fibro {fondo_esp}"})
    
    # Divisores
    if columnas > 1:
        piezas.append({"Pieza": "Divisor Vert.", "Cant": columnas - 1, "Largo": alto_util, "Ancho": prof, "Veta": "↕️ Vertical", "Mat": f"Melamina {espesor}"})
        
        # Recalcular ancho hueco para componentes
        descuento_parantes = (columnas - 1) * espesor
        ancho_hueco = (ancho_interno_total - descuento_parantes) / columnas
    else:
        ancho_hueco = ancho_interno_total

    # --- B. ESTANTES ---
    if cant_estantes > 0:
        piezas.append({
            "Pieza": "Estante Móvil", 
            "Cant": cant_estantes, 
            "Largo": ancho_hueco - 2, # 2mm de luz para que entre fácil
            "Ancho": prof - 20, # Retiro para que no choque la puerta
            "Veta": "↔️ Horizontal", 
            "Mat": f"Melamina {espesor}"
        })
        # Herrajes Estantes
        compras.append({"Item": "Soportes Estante", "Cant": cant_estantes * 4, "Unidad": "u.", "Uso": "4 por cada estante"})

    # --- C. PUERTAS ---
    if cant_puertas > 0:
        # Cálculo de ancho de puerta
        ancho_puerta = 0
        if cant_puertas == 1:
            ancho_puerta = ancho - 4 # 2mm luz x lado
        elif cant_puertas >= 2:
            # Asumimos puertas pares cubriendo el ancho total
            # (Ancho - 2mm izq - 2mm der - 2mm centro) / 2
            ancho_puerta = (ancho - 6) / cant_puertas
            
        piezas.append({
            "Pieza": "Puerta", 
            "Cant": cant_puertas, 
            "Largo": alto_puerta, 
            "Ancho": ancho_puerta, 
            "Veta": veta_frentes, 
            "Mat": f"Melamina {espesor}"
        })
        
        # Cálculo de Bisagras (Regla de carpintero)
        bisagras_por_puerta = 2
        if alto_puerta > 900: bisagras_por_puerta = 3
        if alto_puerta > 1600: bisagras_por_puerta = 4
        if alto_puerta > 2100: bisagras_por_puerta = 5
        
        compras.append({
            "Item": "Bisagras Cazoleta 35mm", 
            "Cant": cant_puertas * bisagras_por_puerta, 
            "Unidad": "u.", 
            "Uso": f"{bisagras_por_puerta} por puerta (Codo 0 si es lateral ext)"
        })

    # --- D. CAJONES ---
    if cant_cajones > 0:
        # Asumimos que los cajones van en UNA columna o se reparten. 
        # Para simplificar V6: Calculamos material para X cajones del ancho del hueco.
        # Altura: Asumimos 180mm por defecto si no hay restricción, o calculamos.
        alto_frente_cajon = 180 # Estándar
        lateral_cajon = 150 # Estándar
        
        piezas.append({"Pieza": "Frente Cajón", "Cant": cant_cajones, "Largo": ancho_hueco-4, "Ancho": alto_frente_cajon, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
        piezas.append({"Pieza": "Lat. Cajón", "Cant": cant_cajones*2, "Largo": 500, "Ancho": lateral_cajon, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
        piezas.append({"Pieza": "Contra-Frente", "Cant": cant_cajones, "Largo": ancho_hueco-90, "Ancho": lateral_cajon, "Veta": "↔️ Horizontal", "Mat": "Blanca 18mm"})
        piezas.append({"Pieza": "Fondo Cajón", "Cant": cant_cajones, "Largo": 500, "Ancho": ancho_hueco-90, "Veta": "Indistinto", "Mat": "Fibro 3mm"})
        
        compras.append({"Item": "Correderas Z/Telescópicas", "Cant": cant_cajones, "Unidad": "pares", "Uso": "1 par por cajón (500mm)"})
        compras.append({"Item": "Tornillos 3.5x16mm", "Cant": cant_cajones * 12, "Unidad": "u.", "Uso": "Fijación correderas"})

    # --- E. TORNILLERÍA GRUESA ---
    # Estructura básica
    tornillos_estruc = (len(piezas) * 4) 
    compras.insert(0, {"Item": "Tornillos 4x50mm", "Cant": int(tornillos_estruc), "Unidad": "u.", "Uso": "Armado estructural del casco"})
    
    if fondo_esp == 18:
        compras.append({"Item": "Tornillos 4x40mm", "Cant": 20, "Unidad": "u.", "Uso": "Fijación de Fondo 18mm"})
    else:
        compras.append({"Item": "Clavos / Grapas", "Cant": 50, "Unidad": "u.", "Uso": "Fijación Fondo Fibro"})

    # --- VISUALIZACIÓN ---
    col_izq, col_der = st.columns([1.5, 1])
    
    with col_izq:
        st.write("### 📋 Listado de Corte")
        df_piezas = pd.DataFrame(piezas)
        st.dataframe(df_piezas.style.format({"Largo": "{:.1f}", "Ancho": "{:.1f}"}), use_container_width=True, hide_index=True)
        
        # Botón CSV
        csv = df_piezas.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Planilla Corte", csv, "corte_v6.csv", "text/csv")

    with col_der:
        st.write("### 🛒 Lista de Compras (Con Referencia)")
        df_compras = pd.DataFrame(compras)
        st.dataframe(
            df_compras, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Item": st.column_config.TextColumn("Herraje", width="medium"),
                "Uso": st.column_config.TextColumn("¿Para qué sirve?", width="large"),
            }
        )
        
        # Cálculo de Tapacantos
        metros = sum([((p["Largo"]+p["Ancho"])*2*p["Cant"])/1000 for p in piezas if "Melamina" in p["Mat"]])
        st.warning(f"**Tapacanto PVC:** Comprar aprox {metros*1.2:.1f} metros.")
