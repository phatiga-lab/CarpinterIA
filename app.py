import streamlit as st
import pandas as pd

# Configuración visual
st.set_page_config(page_title="CarpinterIA: Pro", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Calculadora Profesional")

# --- 1. CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración Taller")
    espesor = st.selectbox("Espesor Placa (mm)", [18, 15, 25], index=0)
    fondo = st.selectbox("Espesor Fondo (mm)", [3, 5.5, 18], index=1)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)
    
    st.divider()
    st.info("💡 Tip: Para frentes continuos, cortá la tira completa primero.")

# --- 2. ZONA DE TRABAJO ---
st.subheader("📐 Definición del Mueble")

c1, c2, c3 = st.columns(3)
with c1:
    ancho = st.number_input("Ancho Final (mm)", value=1130, step=10)
    alto = st.number_input("Alto Final (mm)", value=800, step=10)
with c2:
    prof = st.number_input("Profundidad (mm)", value=550, step=10)
    cajones = st.number_input("Cant. Cajones", value=3, step=1)
with c3:
    cant_estantes = st.number_input("Cant. Estantes", value=0, step=1)
    tipo_herraje = st.selectbox("Guías", ["Telescópicas", "Push", "Z"], index=0)

st.markdown("---")

# --- 3. MOTOR DE CÁLCULO ---
if st.button("🚀 GENERAR PLANILLA DE TALLER", type="primary", use_container_width=True):
    
    # --- A. LÓGICA DE DESPIECE ---
    alto_lateral = alto # Laterales al piso
    ancho_piso = ancho - (espesor * 2) # Descuento estándar
    
    piezas = []
    
    # 1. ESTRUCTURA
    piezas.append({
        "Pieza": "Lateral", "Cant": 2, 
        "Largo (Veta)": alto_lateral, "Ancho": prof, 
        "Veta": "↕️ Vertical", "Material": f"Melamina {espesor}"
    })
    
    piezas.append({
        "Pieza": "Techo/Piso", "Cant": 2, 
        "Largo (Veta)": ancho_piso, "Ancho": prof, 
        "Veta": "↔️ Horizontal", "Material": f"Melamina {espesor}"
    })
    
    # 2. FONDO
    piezas.append({
        "Pieza": "Fondo", "Cant": 1, 
        "Largo (Veta)": alto-15, "Ancho": ancho-15, 
        "Veta": "Indistinto", "Material": f"Fibro {fondo}"
    })

    # 3. CAJONES
    if cajones > 0:
        # Frente: Descuento de luz (4mm total)
        alto_frente = (alto - zocalo - 30) / cajones 
        piezas.append({
            "Pieza": "Frente Cajón", "Cant": cajones, 
            "Largo (Veta)": ancho-4, "Ancho": int(alto_frente), 
            "Veta": "↔️ Horizontal (Continuo)", "Material": f"Melamina {espesor}"
        })
        
        # Estructura interna cajón
        piezas.append({
            "Pieza": "Lat. Cajón", "Cant": cajones*2, 
            "Largo (Veta)": 500, "Ancho": 150, 
            "Veta": "↔️ Horizontal", "Material": "Blanca 18mm"
        })
        piezas.append({
            "Pieza": "Contra-Frente", "Cant": cajones*2, 
            "Largo (Veta)": ancho_piso - 90, "Ancho": 150, # 90mm descuento guías+laterales
            "Veta": "↔️ Horizontal", "Material": "Blanca 18mm"
        })

    # --- B. RESULTADOS ---
    col_izq, col_der = st.columns([2, 1])
    
    with col_izq:
        st.write("### 📋 Listado de Corte")
        df = pd.DataFrame(piezas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("Nota: 'Largo (Veta)' indica la dirección del dibujo de la madera.")

    with col_der:
        st.write("### 🔩 Insumos Estimados")
        
        # Cálculo de tornillos (Estimación x Pieza)
        tornillos_4x50 = (len(piezas) * 4) + (cajones * 8)
        tornillos_3x16 = (cajones * 12) # 6 por guía
        
        # Cálculo de Tapacanto (Perímetro aproximado)
        metros_canto = ((ancho + alto) * 2 / 1000) * 1.5 # 50% desperdicio/error
        
        st.info(f"**Tornillos 4x50mm:** {int(tornillos_4x50)} u. (Estructura)")
        if fondo == 18:
            st.info(f"**Tornillos 4x40mm:** {int(tornillos_4x50/2)} u. (Fondos)")
        else:
            st.info(f"**Clavos/Grapas:** {int(tornillos_4x50)} u.")
            
        st.success(f"**Tornillos 3.5x16:** {int(tornillos_3x16)} u. (Guías)")
        st.warning(f"**Tapacanto:** {metros_canto:.1f} metros aprox.")
