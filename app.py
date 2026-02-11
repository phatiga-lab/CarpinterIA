import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# Configuración de página
st.set_page_config(page_title="CarpinterIA: V14 Precisión", page_icon="🪚", layout="wide")

# ==============================================================================
# 1. BARRA LATERAL: CONFIGURACIÓN
# ==============================================================================
with st.sidebar:
    st.title("🪚 CarpinterIA V14")
    st.markdown("### ⚙️ Configuración")
    
    # Materiales
    st.write("**1. Tableros**")
    espesor = st.selectbox("Espesor Melamina", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70, step=5)
    veta_frentes = st.radio("Veta Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    st.divider()
    
    # Herrajes
    st.write("**2. Herrajes**")
    tipo_corredera = st.selectbox("Correderas", ["Telescópicas (Bolillas)", "Comunes (Z)"])
    if "Telescópicas" in tipo_corredera:
        descuento_guia = 26 
        costo_guia_ref = 6500
    else:
        descuento_guia = 25 
        costo_guia_ref = 2500

    tipo_bisagra = st.selectbox("Bisagras", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)"])
    
    st.divider()
    
    # Costos
    with st.expander("💲 Precios (Opcional)"):
        precio_placa = st.number_input("Precio Placa ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Precio Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input("Precio Canto ($)", value=800, step=50)
        costo_bisagra = st.number_input("Costo Bisagra ($)", value=2500, step=100)
        costo_guia = st.number_input("Costo Guías ($)", value=costo_guia_ref, step=500)
        margen = st.number_input("Margen Ganancia", value=2.5, step=0.1)

# ==============================================================================
# 2. LAYOUT (Estructura Visual)
# ==============================================================================
contenedor_grafico = st.container()
st.divider()
contenedor_controles = st.container()
st.divider()
contenedor_boton = st.container()

# ==============================================================================
# 3. CONTROLES DE DISEÑO (INPUTS MANUALES)
# ==============================================================================
configuracion_columnas = []

with contenedor_controles:
    col_medidas, col_distribucion = st.columns([1, 2])
    
    # --- Medidas Generales ---
    with col_medidas:
        st.subheader("1. Medidas del Mueble")
        ancho = st.number_input("Ancho Total (mm)", value=1200, step=10)
        alto = st.number_input("Alto Total (mm)", value=2000, step=10)
        prof = st.number_input("Profundidad (mm)", value=550, step=10)
        st.markdown("---")
        cant_columnas = st.number_input("Cantidad de Columnas", min_value=1, max_value=5, value=2, step=1)

    # --- Configuración por Columna ---
    with col_distribucion:
        st.subheader("2. Diseño Interno")
        tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
        
        for i, tab in enumerate(tabs):
            with tab:
                c1, c2 = st.columns(2)
                
                # SECTOR INFERIOR
                with c1:
                    st.markdown("##### 🔽 Abajo")
                    tipo_inf = st.selectbox("Componente", ["Vacío", "Cajonera", "Puerta Baja", "Puerta Entera"], key=f"inf_{i}")
                    
                    detalles_inf = {}
                    
                    if tipo_inf == "Cajonera":
                        h_mod = st.number_input("Altura Módulo (mm)", value=720, step=10, key=f"h_caj_{i}")
                        cant_caj = st.number_input("Cant. Cajones", value=3, step=1, min_value=1, key=f"qty_caj_{i}")
                        detalles_inf = {"alto": h_mod, "cant": cant_caj}
                        
                        # Validación visual
                        alto_frente = (h_mod - espesor) / cant_caj
                        st.caption(f"Frentes aprox: {alto_frente:.1f}mm")
                    
                    elif tipo_inf == "Puerta Baja":
                        h_p = st.number_input("Altura Puerta (mm)", value=720, step=10, key=f"h_p_inf_{i}")
                        doble = st.checkbox("¿Doble Hoja?", value=False, key=f"doble_inf_{i}")
                        detalles_inf = {"alto": h_p, "doble": doble}
                        
                    elif tipo_inf == "Puerta Entera":
                        doble = st.checkbox("¿Doble Hoja?", value=False, key=f"doble_ent_{i}")
                        detalles_inf = {"doble": doble}

                # SECTOR SUPERIOR
                with c2:
                    st.markdown("##### 🔼 Arriba")
                    if tipo_inf == "Puerta Entera":
                        st.info("Ocupado por puerta entera.")
                        tipo_sup = "Nada"
                        detalles_sup = {}
                    else:
                        tipo_sup = st.selectbox("Componente", ["Vacío", "Estantes", "Barral", "Puerta Alta"], key=f"sup_{i}")
                        
                        detalles_sup = {}
                        if tipo_sup == "Estantes":
                            cant_est = st.number_input("Cant. Estantes", value=3, step=1, min_value=1, key=f"qty_est_{i}")
                            detalles_sup = {"cant": cant_est}
                        
                        elif tipo_sup == "Puerta Alta":
                             doble_sup = st.checkbox("¿Doble Hoja?", value=False, key=f"doble_sup_{i}")
                             detalles_sup = {"doble": doble_sup}

                configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup})

# ==============================================================================
# 4. GRÁFICO DINÁMICO (PLOTLY)
# ==============================================================================
def dibujar_mueble(ancho, alto, zocalo, columnas, configs, espesor_mat):
    fig = go.Figure()
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0), 
        height=400,
        xaxis=dict(visible=False, range=[-50, ancho+50]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]),
        plot_bgcolor="white",
        title=f"Vista Previa: {ancho}x{alto} mm"
    )

    # Casco
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2C3E50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4))

    ancho_col = ancho / columnas
    
    for i, conf in enumerate(configs):
        x_s = i * ancho_col
        x_e = (i + 1) * ancho_col
        y_c = zocalo 
        
        if i < columnas: 
             fig.add_shape(type="line", x0=x_e, y0=zocalo, x1=x_e, y1=alto, line=dict(color="#5D4037", width=2))

        # --- DIBUJO INFERIOR ---
        if conf["inf_tipo"] == "Cajonera":
            h_total = conf["inf_data"]["alto"]
            cant = conf["inf_data"]["cant"]
            
            # Tapa
            y_tapa = y_c + h_total
            fig.add_shape(type="rect", x0=x_s, y0=y_tapa-espesor_mat, x1=x_e, y1=y_tapa, fillcolor="#8B4513", line=dict(width=0))
            
            h_util = h_total - espesor_mat
            h_unit = h_util / cant
            
            for c in range(cant):
                y_pos = y_c + (c * h_unit)
                fig.add_shape(type="rect", x0=x_s+3, y0=y_pos+2, x1=x_e-3, y1=y_pos+h_unit-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                fig.add_shape(type="line", x0=x_s+20, y0=y_pos+(h_unit/2), x1=x_e-20, y1=y_pos+(h_unit/2), line=dict(color="#154360", width=2))
            y_c += h_total

        elif conf["inf_tipo"] == "Puerta Baja":
            h = conf["inf_data"]["alto"]
            doble = conf["inf_data"]["doble"]
            
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=y_c+h-2, fillcolor="#ABEBC6", line=dict(color="#196F3D"))
            
            if doble:
                # Línea divisoria
                mid = x_s + (ancho_col/2)
                fig.add_shape(type="line", x0=mid, y0=y_c+2, x1=mid, y1=y_c+h-2, line=dict(color="#145A32", width=1))
                # 2 Manijas
                fig.add_shape(type="circle", x0=mid-15, y0=y_c+h-50, x1=mid-5, y1=y_c+h-40, fillcolor="black")
                fig.add_shape(type="circle", x0=mid+5, y0=y_c+h-50, x1=mid+15, y1=y_c+h-40, fillcolor="black")
            else:
                # 1 Manija
                px = x_e - 20 if i % 2 == 0 else x_s + 20
                fig.add_shape(type="circle", x0=px-5, y0=y_c+h-50, x1=px+5, y1=y_c+h-40, fillcolor="black")
                
            y_c += h

        elif conf["inf_tipo"] == "Puerta Entera":
            doble = conf["inf_data"]["doble"]
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="#D2B4DE", line=dict(color="#6C3483"))
            
            if doble:
                mid = x_s + (ancho_col/2)
                fig.add_shape(type="line", x0=mid, y0=y_c+2, x1=mid, y1=alto-2, line=dict(color="#4A235A", width=1))
                fig.add_shape(type="circle", x0=mid-15, y0=zocalo+900, x1=mid-5, y1=zocalo+910, fillcolor="black")
                fig.add_shape(type="circle", x0=mid+5, y0=zocalo+900, x1=mid+15, y1=zocalo+910, fillcolor="black")
            else:
                px = x_e - 20 if i % 2 == 0 else x_s + 20
                fig.add_shape(type="circle", x0=px-5, y0=zocalo+900, x1=px+5, y1=zocalo+910, fillcolor="black")
            y_c = alto

        # --- DIBUJO SUPERIOR ---
        restante = alto - y_c
        if restante > 0:
            if conf["sup_tipo"] == "Estantes":
                cant = conf["sup_data"]["cant"]
                paso = restante / (cant + 1)
                for e in range(cant):
                    y_est = y_c + (paso * (e+1))
                    fig.add_shape(type="line", x0=x_s+2, y0=y_est, x1=x_e-2, y1=y_est, line=dict(color="#6E2C00", width=3))
            
            elif conf["sup_tipo"] == "Barral":
                y_b = alto - 100
                fig.add_shape(type="line", x0=x_s+10, y0=y_b, x1=x_e-10, y1=y_b, line=dict(color="gray", width=5))
                fig.add_annotation(x=x_s+(ancho_col/2), y=y_b-30, text="👕", showarrow=False)
            
            elif conf["sup_tipo"] == "Puerta Alta":
                 doble = conf["sup_data"]["doble"]
                 fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="#F9E79F", line=dict(color="#D4AC0D"))
                 if doble:
                     mid = x_s + (ancho_col/2)
                     fig.add_shape(type="line", x0=mid, y0=y_c+2, x1=mid, y1=alto-2, line=dict(color="#9A7D0A", width=1))
                     fig.add_shape(type="circle", x0=mid-15, y0=y_c+50, x1=mid-5, y1=y_c+60, fillcolor="black")
                     fig.add_shape(type="circle", x0=mid+5, y0=y_c+50, x1=mid+15, y1=y_c+60, fillcolor="black")
                 else:
                     px = x_e - 20 if i % 2 == 0 else x_s + 20
                     fig.add_shape(type="circle", x0=px-5, y0=y_c+50, x1=px+5, y1=y_c+60, fillcolor="black")

    return fig

with contenedor_grafico:
    st.plotly_chart(dibujar_mueble(ancho, alto, zocalo, cant_columnas, configuracion_columnas, espesor), use_container_width=True)

# ==============================================================================
# 5. BOTÓN DE ACCIÓN
# ==============================================================================
with contenedor_boton:
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        procesar = st.button("🚀 PROCESAR PROYECTO COMPLETO", type="primary", use_container_width=True)

# ==============================================================================
# 6. LÓGICA DE CÁLCULO
# ==============================================================================
if procesar:
    piezas = []
    compras = []
    
    # A. Estructura
    alto_int = alto - zocalo - (espesor * 2) 
    ancho_int_total = ancho - (espesor * 2)
    
    piezas.append({"Pieza": "Lat. Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_int_total, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
    
    if cant_columnas > 1:
        piezas.append({"Pieza": "Divisor Vert", "Cant": cant_columnas-1, "Largo": alto_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

    descuento_parantes = (cant_columnas - 1) * espesor
    ancho_hueco = (ancho_int_total - descuento_parantes) / cant_columnas

    # B. Procesar Columnas
    for i, conf in enumerate(configuracion_columnas):
        
        # --- CAJONES ---
        if conf["inf_tipo"] == "Cajonera":
            cant = conf["inf_data"]["cant"]
            h_modulo_total = conf["inf_data"]["alto"]
            
            # Tapa Cajonera
            piezas.append({
                "Pieza": f"Tapa Cajonera (Col {i+1})", "Cant": 1, 
                "Largo": ancho_hueco, "Ancho": prof, "Veta": "↔️ Horiz", 
                "Mat": f"Melamina {espesor}", "Nota": "Estructural"
            })
            
            h_disponible_frentes = h_modulo_total - espesor
            luz = 3
            alto_frente_real = (h_disponible_frentes - ((cant - 1) * luz)) / cant
            
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant, "Largo": ancho_hueco-4, "Ancho": alto_frente_real, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
            # Lateral Cajón
            espacio_caja = alto_frente_real - 30 
            lat_h = 0
            if espacio_caja >= 190: lat_h = 180
            elif espacio_caja >= 160: lat_h = 150
            elif espacio_caja >= 110: lat_h = 100
            
            if lat_h > 0:
                ancho_caja = ancho_hueco - (descuento_guia * 2) - 36
                piezas.append({"Pieza": "Lat. Cajón", "Cant": cant*2, "Largo": 500, "Ancho": lat_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
                piezas.append({"Pieza": "Contra-Frente", "Cant": cant, "Largo": ancho_caja, "Ancho": lat_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
                piezas.append({"Pieza": "Fondo Cajón", "Cant": cant, "Largo": 500, "Ancho": ancho_caja, "Veta": "---", "Mat": "Fibro 3mm"})
                compras.append({"Item": f"Guías {tipo_corredera} 500mm", "Cant": cant, "Unidad": "par", "Costo": costo_guia})
                compras.append({"Item": "Tornillos 3.5x16", "Cant": cant*12, "Unidad": "u.", "Costo": 0})
            else:
                st.error(f"❌ Error Col {i+1}: Cajones muy bajos.")

        # --- PUERTAS (LOGICA DE DOBLE HOJA) ---
        def procesar_puerta(tipo, h_total, es_doble):
            cant_hojas = 2 if es_doble else 1
            if es_doble:
                # Ancho: Hueco - 2 luz izq - 2 luz der - 2 luz centro = Hueco - 6
                ancho_hoja = (ancho_hueco - 6) / 2
                nombre_pieza = f"{tipo} (x2 Hojas)"
            else:
                # Ancho: Hueco - 4
                ancho_hoja = ancho_hueco - 4
                nombre_pieza = tipo

            piezas.append({
                "Pieza": nombre_pieza, "Cant": cant_hojas, 
                "Largo": h_total-4, "Ancho": ancho_hoja, 
                "Veta": veta_frentes, "Mat": f"Melamina {espesor}"
            })
            
            # Bisagras
            bisagras_por_hoja = 2 if h_total < 900 else (3 if h_total < 1600 else (4 if h_total < 2100 else 5))
            compras.append({
                "Item": f"Bisagras {tipo_bisagra}", 
                "Cant": bisagras_por_hoja * cant_hojas, 
                "Unidad": "u.", "Costo": costo_bisagra
            })

        if "Puerta" in conf["inf_tipo"]:
            h = conf["inf_data"]["alto"] if conf["inf_tipo"] == "Puerta Baja" else (alto - zocalo)
            doble = conf["inf_data"].get("doble", False)
            procesar_puerta(conf["inf_tipo"], h, doble)

        if conf["sup_tipo"] == "Puerta Alta":
             h_usada = conf["inf_data"].get("alto", 0)
             h_rest = alto - zocalo - h_usada
             doble = conf["sup_data"].get("doble", False)
             procesar_puerta("Puerta Alta", h_rest, doble)

        # --- OTROS ---
        if conf["sup_tipo"] == "Estantes":
            cant = conf["sup_data"]["cant"]
            piezas.append({"Pieza": "Estante Móvil", "Cant": cant, "Largo": ancho_hueco-2, "Ancho": prof-20, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
            compras.append({"Item": "Soportes Estante", "Cant": cant*4, "Unidad": "u.", "Costo": 50})

        if conf["sup_tipo"] == "Barral":
            compras.append({"Item": "Barral Oval", "Cant": 1, "Unidad": "tira", "Nota": f"Cortar a {ancho_hueco-5:.0f}mm", "Costo": 3000})
            compras.append({"Item": "Soportes Barral", "Cant": 2, "Unidad": "u.", "Costo": 500})

    # C. Cierre
    compras.insert(0, {"Item": "Tornillos 4x50", "Cant": len(piezas)*4, "Unidad": "u.", "Costo": 10})
    mts_canto = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1000
    compras.append({"Item": "Tapacanto PVC", "Cant": int(mts_canto*1.2), "Unidad": "m", "Costo": precio_canto})

    # Visual
    t1, t2, t3 = st.tabs(["📋 Despiece", "🔩 Herrajes", "💰 Costos"])
    with t1:
        df = pd.DataFrame(piezas)
        st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
        st.download_button("📥 Bajar CSV", df.to_csv(index=False).encode(), "corte.csv")
    with t2:
        df_c = pd.DataFrame(compras)
        st.dataframe(df_c.groupby(["Item", "Unidad", "Nota"], as_index=False).sum(), use_container_width=True, hide_index=True)
    with t3:
        # Costo aprox
        placas = math.ceil((sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1e6 * 1.3) / 4.75)
        costo_final = (placas * precio_placa) + sum([c.get("Costo",0) * c["Cant"] for c in compras])
        st.metric("Costo Total", f"$ {costo_final:,.0f}")
