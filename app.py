import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

st.set_page_config(page_title="CarpinterIA: Ultimate", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Sistema Integral (V11)")

# --- 1. BARRA LATERAL: CONFIGURACIÓN Y COSTOS ---
with st.sidebar:
    st.header("1. Materiales y Estructura")
    espesor = st.selectbox("Espesor Melamina", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)
    veta_frentes = st.radio("Veta Visual", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    st.divider()
    st.header("2. Selección de Herrajes")
    
    # TIPOS DE CORREDERAS (Afecta medidas y precio)
    tipo_corredera = st.selectbox("Tipo de Correderas", ["Telescópicas (Bolillas)", "Comunes (Z)"])
    if "Telescópicas" in tipo_corredera:
        descuento_guia = 26 # 13mm por lado
        precio_guia_default = 6500
    else:
        descuento_guia = 25 # 12.5mm por lado
        precio_guia_default = 2500

    # TIPOS DE BISAGRAS
    tipo_bisagra = st.selectbox("Tipo de Bisagra", ["Codo 0 (Cobertura Total)", "Codo 9 (Media)", "Codo 18 (Interior)"])
    
    st.divider()
    st.header("3. Costos (Lista de Precios)")
    precio_placa = st.number_input("Precio Placa Melamina ($)", value=85000, step=1000)
    precio_fondo = st.number_input("Precio Placa Fondo ($)", value=25000, step=1000)
    precio_canto = st.number_input("Precio Metro Canto ($)", value=800, step=50)
    costo_bisagra = st.number_input("Costo x Bisagra ($)", value=2500, step=100)
    costo_guia = st.number_input("Costo x Par Correderas ($)", value=precio_guia_default, step=500)
    margen = st.slider("Margen de Ganancia", 1.5, 4.0, 2.5, help="Multiplicador sobre el costo")

# --- 2. DISEÑO DEL MUEBLE ---
col_dims, col_config = st.columns([1, 2])

with col_dims:
    st.subheader("Medidas Generales")
    ancho = st.number_input("Ancho Total (mm)", 500, 3000, 1200, step=50)
    alto = st.number_input("Alto Total (mm)", 600, 2600, 2000, step=50)
    prof = st.number_input("Profundidad (mm)", 300, 900, 550, step=50)
    
    st.subheader("Distribución")
    cant_columnas = st.slider("Cantidad de Columnas", 1, 4, 2)
    
    st.info(f"💡 Herraje seleccionado: **{tipo_corredera}** (Descuento {descuento_guia}mm).")

# --- 3. CONFIGURACIÓN DETALLADA POR COLUMNA ---
configuracion_columnas = []

with col_config:
    st.subheader("Configuración por Columna")
    tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
    
    for i, tab in enumerate(tabs):
        with tab:
            c1, c2 = st.columns(2)
            
            # --- SECTOR INFERIOR ---
            with c1:
                st.write("🔽 **Componente Inferior**")
                tipo_inf = st.selectbox(f"Tipo (Col {i+1} Inf)", 
                                       ["Vacío", "Cajonera", "Puerta Baja", "Puerta Entera"], 
                                       key=f"inf_{i}")
                
                detalles_inf = {}
                if tipo_inf == "Cajonera":
                    h_mod = st.slider(f"Altura Módulo (mm)", 300, 1200, 720, key=f"h_caj_{i}")
                    cant_caj = st.slider(f"Cant. Cajones", 2, 8, 3, key=f"qty_caj_{i}")
                    
                    # Cálculo previo para validar altura
                    alto_frente = (h_mod / cant_caj)
                    if alto_frente < 130:
                        st.warning(f"⚠️ Cajones muy bajos ({alto_frente:.0f}mm).")
                    
                    detalles_inf = {"alto": h_mod, "cant": cant_caj}
                
                elif tipo_inf == "Puerta Baja":
                    h_p = st.slider(f"Altura Puerta (mm)", 300, 1200, 720, key=f"h_p_inf_{i}")
                    detalles_inf = {"alto": h_p}

            # --- SECTOR SUPERIOR ---
            with c2:
                st.write("🔼 **Componente Superior**")
                if tipo_inf == "Puerta Entera":
                    st.info("Ocupado por puerta entera.")
                    tipo_sup = "Nada"
                    detalles_sup = {}
                else:
                    tipo_sup = st.selectbox(f"Tipo (Col {i+1} Sup)", 
                                           ["Estantes", "Barral", "Espacio Libre", "Puerta Alta"], 
                                           key=f"sup_{i}")
                    
                    detalles_sup = {}
                    if tipo_sup == "Estantes":
                        cant_est = st.slider(f"Cant. Estantes", 1, 8, 3, key=f"qty_est_{i}")
                        detalles_sup = {"cant": cant_est}

            configuracion_columnas.append({
                "inf_tipo": tipo_inf, "inf_data": detalles_inf,
                "sup_tipo": tipo_sup, "sup_data": detalles_sup
            })

# --- 4. MOTOR GRÁFICO (VISUALIZADOR) ---
def dibujar_mueble(ancho, alto, zocalo, columnas, configs):
    fig = go.Figure()
    fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=350,
        xaxis=dict(visible=False, range=[-50, ancho+50]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]),
        plot_bgcolor="white")

    # Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2C3E50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4))

    ancho_col = ancho / columnas
    
    for i, conf in enumerate(configs):
        x_s = i * ancho_col
        x_e = (i + 1) * ancho_col
        y_c = zocalo
        
        if i < columnas: # Divisor
             fig.add_shape(type="line", x0=x_e, y0=zocalo, x1=x_e, y1=alto, line=dict(color="#5D4037", width=2))

        # Inferior
        if conf["inf_tipo"] == "Cajonera":
            h = conf["inf_data"]["alto"]
            cant = conf["inf_data"]["cant"]
            h_unit = h / cant
            for c in range(cant):
                y_pos = y_c + (c * h_unit)
                fig.add_shape(type="rect", x0=x_s+3, y0=y_pos+2, x1=x_e-3, y1=y_pos+h_unit-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                fig.add_shape(type="line", x0=x_s+20, y0=y_pos+(h_unit/2), x1=x_e-20, y1=y_pos+(h_unit/2), line=dict(color="#154360", width=2))
            y_c += h
        elif conf["inf_tipo"] == "Puerta Baja":
            h = conf["inf_data"]["alto"]
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=y_c+h-2, fillcolor="#ABEBC6", line=dict(color="#196F3D"))
            y_c += h
        elif conf["inf_tipo"] == "Puerta Entera":
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="#D2B4DE", line=dict(color="#6C3483"))
            y_c = alto

        # Superior
        rest = alto - y_c
        if rest > 0:
            if conf["sup_tipo"] == "Estantes":
                cant = conf["sup_data"]["cant"]
                paso = rest / (cant + 1)
                for e in range(cant):
                    y_est = y_c + (paso * (e+1))
                    fig.add_shape(type="line", x0=x_s+2, y0=y_est, x1=x_e-2, y1=y_est, line=dict(color="#6E2C00", width=3))
            elif conf["sup_tipo"] == "Barral":
                y_b = alto - 100
                fig.add_shape(type="line", x0=x_s+10, y0=y_b, x1=x_e-10, y1=y_b, line=dict(color="gray", width=5))
                fig.add_annotation(x=x_s+(ancho_col/2), y=y_b-30, text="👕", showarrow=False)
            elif conf["sup_tipo"] == "Puerta Alta":
                 fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="#F9E79F", line=dict(color="#D4AC0D"))

    return fig

st.plotly_chart(dibujar_mueble(ancho, alto, zocalo, cant_columnas, configuracion_columnas), use_container_width=True)

# --- 5. LOGICA MAESTRA DE CÁLCULO ---
if st.button("🚀 PROCESAR PROYECTO COMPLETO", type="primary"):
    
    piezas = []
    compras = []
    
    # A. Estructura General
    alto_int = alto - zocalo - (espesor * 2)
    ancho_int_total = ancho - (espesor * 2)
    
    piezas.append({"Pieza": "Lat. Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_int_total, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
    
    if cant_columnas > 1:
        piezas.append({"Pieza": "Divisor Vert", "Cant": cant_columnas-1, "Largo": alto_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

    # Calculo hueco exacto
    descuento_parantes = (cant_columnas - 1) * espesor
    ancho_hueco = (ancho_int_total - descuento_parantes) / cant_columnas

    # B. Procesar Columnas
    for conf in configuracion_columnas:
        
        # --- CAJONES ---
        if conf["inf_tipo"] == "Cajonera":
            cant = conf["inf_data"]["cant"]
            h_total = conf["inf_data"]["alto"]
            
            # Frentes
            luz = 3
            alto_frente = (h_total / cant) - luz
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant, "Largo": ancho_hueco-4, "Ancho": alto_frente, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
            # VALIDACIÓN INTELIGENTE DE ALTURA LATERAL
            margen_seguridad = 30 # Espacio para que no toque arriba
            espacio_util_cajon = alto_frente - margen_seguridad
            
            lat_h = 150 # Altura estándar preferida
            if espacio_util_cajon < 70: lat_h = 0 # Error
            elif espacio_util_cajon < 110: lat_h = 100
            elif espacio_util_cajon < 160: lat_h = 150
            elif espacio_util_cajon >= 190: lat_h = 180

            if lat_h > 0:
                # Caja del cajón
                # Ancho: Hueco - Descuento de guía seleccionada (25 o 26mm)
                ancho_caja = ancho_hueco - 90 # 18+18 laterales + 13+13 guías + margen aprox
                
                piezas.append({"Pieza": "Lat. Cajón", "Cant": cant*2, "Largo": 500, "Ancho": lat_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
                piezas.append({"Pieza": "Contra-Frente", "Cant": cant, "Largo": ancho_caja, "Ancho": lat_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
                piezas.append({"Pieza": "Fondo Cajón", "Cant": cant, "Largo": 500, "Ancho": ancho_caja, "Veta": "---", "Mat": "Fibro 3mm"})
                
                compras.append({"Item": f"Guías {tipo_corredera} 500mm", "Cant": cant, "Costo": costo_guia, "Nota": "Pares"})
                compras.append({"Item": "Tornillos 3.5x16", "Cant": cant*12, "Costo": 0, "Nota": "Guías"})
        
        # --- PUERTAS (Bisagras) ---
        def get_bisagras(h):
            if h < 900: return 2
            if h < 1600: return 3
            if h < 2100: return 4
            return 5

        if "Puerta" in conf["inf_tipo"]:
            h = conf["inf_data"]["alto"] if conf["inf_tipo"] == "Puerta Baja" else (alto - zocalo)
            piezas.append({"Pieza": conf["inf_tipo"], "Cant": 1, "Largo": h-4, "Ancho": ancho_hueco-4, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            b = get_bisagras(h)
            compras.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": b, "Costo": costo_bisagra, "Nota": ""})
        
        if conf["sup_tipo"] == "Puerta Alta":
             # Calcular altura restante
             h_usada = conf["inf_data"].get("alto", 0)
             h_rest = alto - zocalo - h_usada
             piezas.append({"Pieza": "Puerta Alta", "Cant": 1, "Largo": h_rest-4, "Ancho": ancho_hueco-4, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
             b = get_bisagras(h_rest)
             compras.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": b, "Costo": costo_bisagra, "Nota": ""})

        # --- ESTANTES ---
        if conf["sup_tipo"] == "Estantes":
            cant = conf["sup_data"]["cant"]
            piezas.append({"Pieza": "Estante Móvil", "Cant": cant, "Largo": ancho_hueco-2, "Ancho": prof-20, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
            compras.append({"Item": "Soportes Estante", "Cant": cant*4, "Costo": 50, "Nota": ""})

        # --- BARRAL ---
        if conf["sup_tipo"] == "Barral":
            compras.append({"Item": "Barral Oval", "Cant": 1, "Costo": 3000, "Nota": f"Cortar a {ancho_hueco-5:.0f}mm"})
            compras.append({"Item": "Soportes Barral", "Cant": 2, "Costo": 500, "Nota": ""})

    # C. Insumos Finales
    tornillos = len(piezas) * 4
    compras.insert(0, {"Item": "Tornillos 4x50", "Cant": tornillos, "Costo": 5, "Nota": "Estructura"})
    
    metros_canto = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1000
    compras.append({"Item": "Tapacanto PVC", "Cant": int(metros_canto*1.2), "Costo": precio_canto, "Nota": "Incluye 20% desp."})

    # D. Presupuesto
    area_mela = sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1e6
    placas_mela = math.ceil((area_mela * 1.3) / 4.75) # 4.75m2 placa estandar, 30% desp
    
    area_fondo = sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Fibro" in p["Mat"]]) / 1e6
    placas_fondo = math.ceil((area_fondo * 1.2) / 4.75)

    costo_materia = (placas_mela * precio_placa) + (placas_fondo * precio_fondo)
    costo_herrajes = sum([c["Cant"] * c["Costo"] for c in compras])
    costo_total = costo_materia + costo_herrajes
    precio_venta = costo_total * margen

    # --- MOSTRAR RESULTADOS EN PESTAÑAS ---
    tab1, tab2, tab3 = st.tabs(["📋 Despiece (Corte)", "🛒 Insumos (Herrajes)", "💰 Presupuesto"])
    
    with tab1:
        df_piezas = pd.DataFrame(piezas)
        st.dataframe(df_piezas.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
        st.download_button("📥 CSV Corte", df_piezas.to_csv(index=False).encode(), "despiece.csv")

    with tab2:
        df_compras = pd.DataFrame(compras)
        df_agrup = df_compras.groupby(["Item", "Nota"], as_index=False).agg({"Cant": "sum"})
        st.dataframe(df_agrup, use_container_width=True, hide_index=True)
        st.info(f"Correderas seleccionadas: **{tipo_corredera}**")

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Detalle de Costos**")
            st.write(f"- Melamina ({placas_mela} placas): ${placas_mela * precio_placa:,.0f}")
            st.write(f"- Fondo ({placas_fondo} placas): ${placas_fondo * precio_fondo:,.0f}")
            st.write(f"- Herrajes y Cantos: ${costo_herrajes:,.0f}")
            st.markdown("---")
            st.write(f"**COSTO TOTAL DIRECTO: ${costo_total:,.0f}**")
        with c2:
            st.metric("PRECIO DE VENTA SUGERIDO", f"$ {precio_venta:,.0f}")
            st.caption(f"Margen aplicado: x{margen}")
