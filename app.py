import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

st.set_page_config(page_title="CarpinterIA: V17 X-Ray", page_icon="🪚", layout="wide")

# ==============================================================================
# 1. BARRA LATERAL
# ==============================================================================
with st.sidebar:
    st.title("🪚 CarpinterIA V17")
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
    tipo_corredera = st.selectbox("Correderas", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
    es_push = "Push" in tipo_corredera
    
    if "Telescópicas" in tipo_corredera or "Push" in tipo_corredera:
        descuento_guia = 26 
        costo_guia_ref = 6500
    else:
        descuento_guia = 25 
        costo_guia_ref = 2500

    tipo_bisagra = st.selectbox("Bisagras", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)", "Push"])
    
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
# 2. LAYOUT
# ==============================================================================
contenedor_grafico = st.container()
st.divider()
contenedor_controles = st.container()
st.divider()
contenedor_boton = st.container()

# ==============================================================================
# 3. CONTROLES DE DISEÑO
# ==============================================================================
configuracion_columnas = []

with contenedor_controles:
    col_medidas, col_distribucion = st.columns([1, 2])
    
    # --- Medidas Generales ---
    with col_medidas:
        st.subheader("1. Casco General")
        ancho = st.number_input("Ancho Total (mm)", value=1200, step=10)
        alto = st.number_input("Alto Total (mm)", value=2000, step=10)
        prof = st.number_input("Profundidad (mm)", value=550, step=10)
        st.markdown("---")
        cant_columnas = st.number_input("Cantidad de Columnas", min_value=1, max_value=5, value=2, step=1)

    # --- Configuración por Columna ---
    with col_distribucion:
        st.subheader("2. Diseño Interno")
        tabs = st.tabs([f"Col {i+1}" for i in range(cant_columnas)])
        
        for i, tab in enumerate(tabs):
            with tab:
                modo_col = st.radio(f"Estructura C{i+1}", 
                                   ["Dividida", "Entera"], 
                                   horizontal=True, label_visibility="collapsed", key=f"mode_{i}")
                
                detalles_inf = {}
                detalles_sup = {}
                tipo_inf = "Vacío"
                tipo_sup = "Vacío"

                # Helper para interior
                def config_interior(suffix):
                    st.caption("Interior (Detrás de puerta)")
                    t_int = st.selectbox("Distribución", ["Vacío", "Estantes", "Cubos"], key=f"int_{suffix}")
                    d_int = {}
                    if t_int == "Estantes":
                        cant = st.number_input("Cant.", 1, 10, 3, key=f"int_est_{suffix}")
                        d_int = {"tipo": "Estantes", "cant": cant}
                    elif t_int == "Cubos":
                        c1, c2 = st.columns(2)
                        cols = c1.number_input("Cols", 1, 5, 2, key=f"ic_{suffix}")
                        rows = c2.number_input("Filas", 1, 10, 3, key=f"ir_{suffix}")
                        d_int = {"tipo": "Cubos", "cols": cols, "rows": rows}
                    return d_int

                # MODO ENTERO
                if "Entera" in modo_col:
                    tipo_inf = st.selectbox("Componente Único", ["Vacío", "Cajonera", "Puerta Entera", "Estantes", "Barral"], key=f"ent_{i}")
                    h_util = alto - zocalo
                    
                    if tipo_inf == "Cajonera":
                        cant_caj = st.number_input("Cant. Cajones", 6, step=1, key=f"qty_ent_{i}")
                        detalles_inf = {"alto": h_util, "cant": cant_caj}
                    elif tipo_inf == "Puerta Entera":
                        doble = st.checkbox("Doble Hoja", False, key=f"d_ent_{i}")
                        d_int = config_interior(f"ent_{i}")
                        detalles_inf = {"alto": h_util, "doble": doble, "interior": d_int}
                    elif tipo_inf == "Estantes": # Hack visual
                        cant_est = st.number_input("Cant.", 5, step=1, key=f"e_ent_{i}")
                        detalles_sup = {"cant": cant_est}
                        tipo_sup = "Estantes"
                        tipo_inf = "Vacío"
                    elif tipo_inf == "Barral": # Hack visual
                        tipo_sup = "Barral"
                        tipo_inf = "Vacío"

                # MODO DIVIDIDO
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("🔽 **Abajo**")
                        tipo_inf = st.selectbox("Tipo", ["Vacío", "Cajonera", "Puerta Baja"], key=f"inf_{i}")
                        h_mod = st.number_input("Alto (mm)", value=720, step=10, key=f"h_inf_{i}")
                        
                        if tipo_inf == "Cajonera":
                            cant_caj = st.number_input("Cant.", 3, step=1, key=f"q_inf_{i}")
                            detalles_inf = {"alto": h_mod, "cant": cant_caj}
                        elif tipo_inf == "Puerta Baja":
                            doble = st.checkbox("Doble", False, key=f"d_inf_{i}")
                            d_int = config_interior(f"inf_{i}")
                            detalles_inf = {"alto": h_mod, "doble": doble, "interior": d_int}
                        else:
                            detalles_inf = {"alto": h_mod}

                    with c2:
                        st.markdown("🔼 **Arriba**")
                        h_rest = alto - zocalo - h_mod
                        st.caption(f"Libre: {h_rest}mm")
                        
                        if h_rest > 0:
                            tipo_sup = st.selectbox("Tipo", ["Vacío", "Estantes", "Barral", "Puerta Alta", "Cajonera"], key=f"sup_{i}")
                            if tipo_sup == "Estantes":
                                cant = st.number_input("Cant.", 3, step=1, key=f"q_sup_{i}")
                                detalles_sup = {"cant": cant}
                            elif tipo_sup == "Puerta Alta":
                                doble = st.checkbox("Doble", False, key=f"d_sup_{i}")
                                d_int = config_interior(f"sup_{i}")
                                detalles_sup = {"doble": doble, "interior": d_int}
                            elif tipo_sup == "Cajonera":
                                cant = st.number_input("Cant.", 2, step=1, key=f"qc_sup_{i}")
                                detalles_sup = {"cant": cant}

                configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup})

# ==============================================================================
# 4. GRÁFICO (RAYOS X)
# ==============================================================================
def dibujar_mueble(ancho, alto, zocalo, columnas, configs, espesor_mat, es_push):
    fig = go.Figure()
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0), height=450,
        xaxis=dict(visible=False, range=[-50, ancho+50]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]),
        plot_bgcolor="white", title=f"Vista Previa {ancho}x{alto}mm"
    )

    # Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2C3E50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4))

    ancho_col = ancho / columnas
    
    # FUNCIONES DE DIBUJO
    def dibujar_manija(cx, cy):
        if not es_push:
            fig.add_shape(type="line", x0=cx, y0=cy-15, x1=cx, y1=cy+15, line=dict(color="#154360", width=4))

    def dibujar_interior(x_start, x_end, y_start, h_total, data_int):
        if not data_int: return
        tipo = data_int.get("tipo")
        
        # Color más oscuro para el interior
        color_int = "#A04000" 
        
        if tipo == "Estantes":
            cant = data_int["cant"]
            paso = h_total / (cant + 1)
            for e in range(cant):
                y = y_start + (paso * (e+1))
                fig.add_shape(type="line", x0=x_start+5, y0=y, x1=x_end-5, y1=y, line=dict(color=color_int, width=2, dash="dot"))
        
        elif tipo == "Cubos":
            cols = data_int["cols"]
            rows = data_int["rows"]
            # Horizontales
            paso_h = h_total / rows
            for r in range(1, rows):
                y = y_start + (paso_h * r)
                fig.add_shape(type="line", x0=x_start+5, y0=y, x1=x_end-5, y1=y, line=dict(color=color_int, width=2, dash="dot"))
            # Verticales
            ancho_local = x_end - x_start
            paso_w = ancho_local / cols
            for c in range(1, cols):
                x = x_start + (paso_w * c)
                fig.add_shape(type="line", x0=x, y0=y_start+5, x1=x, y1=y_start+h_total-5, line=dict(color=color_int, width=2, dash="dot"))

    for i, conf in enumerate(configs):
        x_s = i * ancho_col
        x_e = (i + 1) * ancho_col
        y_c = zocalo 
        
        if i < columnas: 
             fig.add_shape(type="line", x0=x_e, y0=zocalo, x1=x_e, y1=alto, line=dict(color="#5D4037", width=2))

        # --- SECTOR INFERIOR ---
        tipo = conf["inf_tipo"]
        data = conf["inf_data"]
        
        if tipo == "Cajonera":
            h = data["alto"]
            cant = data["cant"]
            
            # TAPA INTELIGENTE: Solo dibujar si NO llega al techo
            if (y_c + h) < (alto - 5): # Tolerancia 5mm
                fig.add_shape(type="rect", x0=x_s, y0=y_c+h-espesor_mat, x1=x_e, y1=y_c+h, fillcolor="#8B4513", line=dict(width=0))
            
            h_unit = (h - (espesor_mat if (y_c+h)<(alto-5) else 0)) / cant
            for c in range(cant):
                y_pos = y_c + (c * h_unit)
                # Cajon opaco
                fig.add_shape(type="rect", x0=x_s+3, y0=y_pos+2, x1=x_e-3, y1=y_pos+h_unit-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                dibujar_manija(x_s + (ancho_col/2), y_pos + (h_unit/2))
            y_c += h

        elif "Puerta" in tipo:
            h = data["alto"] if tipo == "Puerta Baja" else (alto - zocalo)
            doble = data.get("doble", False)
            
            # 1. DIBUJAR INTERIOR PRIMERO (Para que quede atras)
            dibujar_interior(x_s, x_e, y_c, h, data.get("interior"))
            
            # 2. DIBUJAR PUERTA TRASLUCIDA (RGBA)
            # Verde agua transparente: rgba(171, 235, 198, 0.5)
            # Violeta transparente: rgba(210, 180, 222, 0.5)
            color_fill = "rgba(171, 235, 198, 0.6)" if "Baja" in tipo else "rgba(210, 180, 222, 0.6)"
            color_line = "#196F3D" if "Baja" in tipo else "#6C3483"
            
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=y_c+h-2, fillcolor=color_fill, line=dict(color=color_line))
            
            if doble:
                mid = x_s + (ancho_col/2)
                fig.add_shape(type="line", x0=mid, y0=y_c+2, x1=mid, y1=y_c+h-2, line=dict(color=color_line, width=1))
                dibujar_manija(mid-15, y_c + h/2)
                dibujar_manija(mid+15, y_c + h/2)
            else:
                px = x_e - 20 if i % 2 == 0 else x_s + 20
                dibujar_manija(px, y_c + h/2)
            
            y_c = alto if tipo == "Puerta Entera" else y_c + h
            
        else:
            if "alto" in data: y_c += data["alto"]

        # --- SECTOR SUPERIOR ---
        rest = alto - y_c
        if rest > 0:
            ts = conf["sup_tipo"]
            ds = conf["sup_data"]
            
            if ts == "Estantes":
                dibujar_interior(x_s, x_e, y_c, rest, {"tipo": "Estantes", "cant": ds["cant"]})
            
            elif ts == "Barral":
                y_b = alto - 100
                fig.add_shape(type="line", x0=x_s+10, y0=y_b, x1=x_e-10, y1=y_b, line=dict(color="gray", width=5))
                fig.add_annotation(x=x_s+(ancho_col/2), y=y_b-30, text="👕", showarrow=False)

            elif ts == "Puerta Alta":
                 # Interior
                 dibujar_interior(x_s, x_e, y_c, rest, ds.get("interior"))
                 # Puerta
                 doble = ds.get("doble", False)
                 fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="rgba(249, 231, 159, 0.6)", line=dict(color="#D4AC0D"))
                 if doble:
                     mid = x_s + (ancho_col/2)
                     fig.add_shape(type="line", x0=mid, y0=y_c+2, x1=mid, y1=alto-2, line=dict(color="#D4AC0D", width=1))
                     dibujar_manija(mid-15, y_c + 50)
                     dibujar_manija(mid+15, y_c + 50)
                 else:
                     px = x_e - 20 if i % 2 == 0 else x_s + 20
                     dibujar_manija(px, y_c + 50)

            elif ts == "Cajonera":
                # Piso cajonera
                fig.add_shape(type="rect", x0=x_s, y0=y_c, x1=x_e, y1=y_c+espesor_mat, fillcolor="#8B4513", line=dict(width=0))
                h_util = rest - espesor_mat
                h_unit = h_util / ds["cant"]
                for c in range(ds["cant"]):
                    y_pos = y_c + espesor_mat + (c * h_unit)
                    fig.add_shape(type="rect", x0=x_s+3, y0=y_pos+2, x1=x_e-3, y1=y_pos+h_unit-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                    dibujar_manija(x_s + (ancho_col/2), y_pos + (h_unit/2))

    return fig

with contenedor_grafico:
    st.plotly_chart(dibujar_mueble(ancho, alto, zocalo, cant_columnas, configuracion_columnas, espesor, es_push), use_container_width=True)

# ==============================================================================
# 5. LOGICA PROCESAMIENTO
# ==============================================================================
with contenedor_boton:
    procesar = st.button("🚀 PROCESAR PROYECTO COMPLETO", type="primary", use_container_width=True)

if procesar:
    piezas = []
    compras = []
    errores = []

    # Validaciones Globales
    ancho_int_total = ancho - (espesor * 2)
    descuento_parantes = (cant_columnas - 1) * espesor
    ancho_hueco = (ancho_int_total - descuento_parantes) / cant_columnas
    
    if ancho_hueco < 150:
        st.error(f"⛔ ERROR CRÍTICO: Las columnas son muy angostas ({ancho_hueco:.0f}mm). Mínimo 150mm para que entren los herrajes.")
        st.stop()

    # Estructura
    alto_int = alto - zocalo - (espesor * 2) 
    piezas.append({"Pieza": "Lat. Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_int_total, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
    if cant_columnas > 1:
        piezas.append({"Pieza": "Divisor Vert", "Cant": cant_columnas-1, "Largo": alto_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

    # Procesar Columnas
    for i, conf in enumerate(configuracion_columnas):
        
        # CAJONES
        def procesar_cajones(pos, cant, h_total, es_superior=False):
            # Tapa/Piso Inteligente
            # Si es INFERIOR y NO toca el techo (modulo dividido) -> Lleva TAPA
            # Si es SUPERIOR -> Lleva PISO
            # Si es ENTERA -> NO lleva nada (usa techo mueble)
            
            h_disponible = h_total
            
            if es_superior:
                piezas.append({"Pieza": f"Piso Cajonera Sup (C{i+1})", "Cant": 1, "Largo": ancho_hueco, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
                h_disponible -= espesor
            elif pos == "Entera":
                pass # Usa techo mueble
            else: # Inferior comun
                piezas.append({"Pieza": f"Tapa Cajonera Inf (C{i+1})", "Cant": 1, "Largo": ancho_hueco, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
                h_disponible -= espesor

            luz = 3
            alto_frente = (h_disponible - ((cant - 1) * luz)) / cant
            
            # Validación Altura Cajon
            if alto_frente < 70:
                errores.append(f"Col {i+1}: Cajones de {alto_frente:.0f}mm son imposibles de fabricar (Mín 70mm).")
                return

            piezas.append({"Pieza": f"Frente {pos}", "Cant": cant, "Largo": ancho_hueco-4, "Ancho": alto_frente, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
            lat_h = 0
            espacio = alto_frente - 30
            if espacio >= 190: lat_h = 180
            elif espacio >= 160: lat_h = 150
            elif espacio >= 110: lat_h = 100
            
            if lat_h > 0:
                ancho_caja = ancho_hueco - (descuento_guia * 2) - 36
                piezas.append({"Pieza": "Lat. Cajón", "Cant": cant*2, "Largo": 500, "Ancho": lat_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
                piezas.append({"Pieza": "Contra-Frente", "Cant": cant, "Largo": ancho_caja, "Ancho": lat_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
                piezas.append({"Pieza": "Fondo Cajón", "Cant": cant, "Largo": 500, "Ancho": ancho_caja, "Veta": "---", "Mat": "Fibro 3mm"})
                compras.append({"Item": f"Guías {tipo_corredera} 500mm", "Cant": cant, "Unidad": "par", "Costo": costo_guia})
            else:
                errores.append(f"Col {i+1}: Cajón muy bajo para lateral estándar.")

        # PUERTAS E INTERIOR
        def procesar_puerta(tipo, h, es_doble, data_int):
            cant_hojas = 2 if es_doble else 1
            ancho_hoja = (ancho_hueco - 6)/2 if es_doble else (ancho_hueco - 4)
            piezas.append({"Pieza": f"{tipo} {'(Doble)' if es_doble else ''}", "Cant": cant_hojas, "Largo": h-4, "Ancho": ancho_hoja, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
            bisagras = 2 if h < 900 else (3 if h < 1600 else (4 if h < 2100 else 5))
            compras.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": bisagras * cant_hojas, "Unidad": "u.", "Costo": costo_bisagra})

            # Interior Detras de Puerta
            if data_int:
                prof_int = prof - 20 # Descuento prof
                if data_int["tipo"] == "Estantes":
                    cant = data_int["cant"]
                    piezas.append({"Pieza": "Estante Int.", "Cant": cant, "Largo": ancho_hueco-2, "Ancho": prof_int, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
                elif data_int["tipo"] == "Cubos":
                    cols = data_int["cols"]
                    rows = data_int["rows"]
                    # Divisores Vert
                    if cols > 1:
                        # Descuento espesores de divisores para calcular luz
                        luz_cubo_w = (ancho_hueco - ((cols-1)*espesor)) / cols
                        piezas.append({"Pieza": "Divisor Cubo Vert", "Cant": cols-1, "Largo": h-2, "Ancho": prof_int, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
                    # Divisores Horiz (Estantes fijos completos)
                    if rows > 1:
                        piezas.append({"Pieza": "Estante Cubo Horiz", "Cant": rows-1, "Largo": ancho_hueco-2, "Ancho": prof_int, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})

        # Ejecución
        if conf["inf_tipo"] == "Cajonera":
            # Si es entera, no descontamos tapa (pasa False)
            procesar_cajones("Inf", conf["inf_data"]["cant"], conf["inf_data"]["alto"], False)
        elif "Puerta" in conf["inf_tipo"]:
            h = conf["inf_data"]["alto"] if conf["inf_tipo"] == "Puerta Baja" else (alto - zocalo)
            procesar_puerta(conf["inf_tipo"], h, conf["inf_data"].get("doble"), conf["inf_data"].get("interior"))
        
        # Superior
        if conf["sup_tipo"] == "Cajonera":
            h_inf = conf["inf_data"].get("alto", 0)
            procesar_cajones("Sup", conf["sup_data"]["cant"], alto-zocalo-h_inf, True)
        elif conf["sup_tipo"] == "Puerta Alta":
            h_inf = conf["inf_data"].get("alto", 0)
            procesar_puerta("Alta", alto-zocalo-h_inf, conf["sup_data"].get("doble"), conf["sup_data"].get("interior"))
        elif conf["sup_tipo"] == "Estantes":
             piezas.append({"Pieza": "Estante Móvil", "Cant": conf["sup_data"]["cant"], "Largo": ancho_hueco-2, "Ancho": prof-20, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
        elif conf["sup_tipo"] == "Barral":
             compras.append({"Item": "Barral", "Cant": 1, "Unidad": "u.", "Costo": 3000})

    # VISUALIZAR
    if errores:
        for e in errores: st.error(e)
    else:
        # Finalizar compras
        compras.insert(0, {"Item": "Tornillos 4x50", "Cant": len(piezas)*4, "Unidad": "u.", "Costo": 10})
        mts = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1000
        compras.append({"Item": "Tapacanto PVC", "Cant": int(mts*1.2), "Unidad": "m", "Costo": precio_canto})

        t1, t2, t3 = st.tabs(["📋 Despiece", "🔩 Herrajes", "💰 Costos"])
        with t1:
            df = pd.DataFrame(piezas)
            st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True)
            st.download_button("📥 CSV", df.to_csv(index=False).encode(), "corte.csv")
        with t2:
            st.dataframe(pd.DataFrame(compras).groupby(["Item", "Unidad"], as_index=False).sum(), use_container_width=True)
        with t3:
            placas = math.ceil((sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1e6 * 1.3) / 4.75)
            st.metric("Costo Total Estimado", f"$ {(placas * precio_placa) + sum([c.get('Costo',0)*c['Cant'] for c in compras]):,.0f}")
