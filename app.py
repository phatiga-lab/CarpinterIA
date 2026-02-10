import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# Configuración de página (SIEMPRE VA PRIMERO)
st.set_page_config(page_title="CarpinterIA: Layout Pro", page_icon="🪚", layout="wide")

# ==============================================================================
# 1. BARRA LATERAL (IZQUIERDA): CONFIGURACIÓN GENERAL
# ==============================================================================
with st.sidebar:
    st.title("🪚 CarpinterIA")
    st.markdown("### ⚙️ Configuración")
    
    # A. Materiales
    st.write("**1. Tableros**")
    espesor = st.selectbox("Espesor Melamina", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)
    veta_frentes = st.radio("Veta Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    st.divider()
    
    # B. Herrajes
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
    
    # C. Costos
    with st.expander("💲 Precios (Opcional)"):
        precio_placa = st.number_input("Precio Placa ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Precio Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input("Precio Canto ($)", value=800, step=50)
        costo_bisagra = st.number_input("Costo Bisagra ($)", value=2500, step=100)
        costo_guia = st.number_input("Costo Guías ($)", value=costo_guia_ref, step=500)
        margen = st.slider("Margen Ganancia", 1.5, 4.0, 2.5)

# ==============================================================================
# 2. DEFINICIÓN DE ESTRUCTURA VISUAL (LAYOUT)
# ==============================================================================
# Definimos los espacios vacíos primero
contenedor_grafico = st.container() # Arriba: Gráfico
st.divider()
contenedor_controles = st.container() # Abajo: Controles
st.divider()
contenedor_boton = st.container() # Final: Botón

# ==============================================================================
# 3. PARTE INFERIOR: CONTROLES DE DISEÑO
# ==============================================================================
configuracion_columnas = []

with contenedor_controles:
    col_medidas, col_distribucion = st.columns([1, 2])
    
    # --- Medidas Generales ---
    with col_medidas:
        st.subheader("1. Medidas del Mueble")
        ancho = st.number_input("Ancho Total (mm)", 500, 3000, 1200, step=50)
        alto = st.number_input("Alto Total (mm)", 600, 2600, 2000, step=50)
        prof = st.number_input("Profundidad (mm)", 300, 900, 550, step=50)
        st.markdown("---")
        cant_columnas = st.slider("Columnas", 1, 4, 2)

    # --- Configuración por Columna ---
    with col_distribucion:
        st.subheader("2. Diseño Interno")
        tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
        
        for i, tab in enumerate(tabs):
            with tab:
                c1, c2 = st.columns(2)
                
                # Sector Inferior
                with c1:
                    st.markdown("##### 🔽 Abajo")
                    tipo_inf = st.selectbox("Componente", ["Vacío", "Cajonera", "Puerta Baja", "Puerta Entera"], key=f"inf_{i}")
                    
                    detalles_inf = {}
                    if tipo_inf == "Cajonera":
                        h_mod = st.slider("Altura Módulo", 300, 1200, 720, key=f"h_caj_{i}")
                        cant_caj = st.slider("Cant. Cajones", 2, 8, 3, key=f"qty_caj_{i}")
                        detalles_inf = {"alto": h_mod, "cant": cant_caj}
                    
                    elif tipo_inf == "Puerta Baja":
                        h_p = st.slider("Altura Puerta", 300, 1200, 720, key=f"h_p_inf_{i}")
                        detalles_inf = {"alto": h_p}

                # Sector Superior
                with c2:
                    st.markdown("##### 🔼 Arriba")
                    if tipo_inf == "Puerta Entera":
                        st.info("Ocupado.")
                        tipo_sup = "Nada"
                        detalles_sup = {}
                    else:
                        tipo_sup = st.selectbox("Componente", ["Estantes", "Barral", "Espacio Libre", "Puerta Alta"], key=f"sup_{i}")
                        
                        detalles_sup = {}
                        if tipo_sup == "Estantes":
                            cant_est = st.slider("Cant. Estantes", 1, 8, 3, key=f"qty_est_{i}")
                            detalles_sup = {"cant": cant_est}

                configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup})

# ==============================================================================
# 4. PARTE SUPERIOR: GRÁFICO DINÁMICO
# ==============================================================================
def dibujar_mueble(ancho, alto, zocalo, columnas, configs, espesor_mat):
    fig = go.Figure()
    fig.update_layout(
        margin=dict(t=30, b=0, l=0, r=0), 
        height=400,
        xaxis=dict(visible=False, range=[-50, ancho+50]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]),
        plot_bgcolor="white",
        title=f"Vista Previa: {ancho}x{alto} mm"
    )

    # Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2C3E50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4))

    ancho_col = ancho / columnas
    
    for i, conf in enumerate(configs):
        x_s = i * ancho_col
        x_e = (i + 1) * ancho_col
        y_c = zocalo 
        
        if i < columnas: 
             fig.add_shape(type="line", x0=x_e, y0=zocalo, x1=x_e, y1=alto, line=dict(color="#5D4037", width=2))

        # Inferior
        if conf["inf_tipo"] == "Cajonera":
            h_total = conf["inf_data"]["alto"]
            cant = conf["inf_data"]["cant"]
            
            # Tapa Cajonera (Visual)
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
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=y_c+h-2, fillcolor="#ABEBC6", line=dict(color="#196F3D"))
            px = x_e - 20 if i % 2 == 0 else x_s + 20
            fig.add_shape(type="circle", x0=px-5, y0=y_c+h-50, x1=px+5, y1=y_c+h-40, fillcolor="black")
            y_c += h

        elif conf["inf_tipo"] == "Puerta Entera":
            fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="#D2B4DE", line=dict(color="#6C3483"))
            px = x_e - 20 if i % 2 == 0 else x_s + 20
            fig.add_shape(type="circle", x0=px-5, y0=zocalo+900, x1=px+5, y1=zocalo+910, fillcolor="black")
            y_c = alto

        # Superior
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
                 fig.add_shape(type="rect", x0=x_s+3, y0=y_c+2, x1=x_e-3, y1=alto-2, fillcolor="#F9E79F", line=dict(color="#D4AC0D"))
                 px = x_e - 20 if i % 2 == 0 else x_s + 20
                 fig.add_shape(type="circle", x0=px-5, y0=y_c+50, x1=px+5, y1=y_c+60, fillcolor="black")

    return fig

# Inyectamos el gráfico en el contenedor superior
with contenedor_grafico:
    st.plotly_chart(dibujar_mueble(ancho, alto, zocalo, cant_columnas, configuracion_columnas, espesor), use_container_width=True)

# ==============================================================================
# 5. BOTÓN DE ACCIÓN (CENTRADO AL FINAL)
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
    
    # A. Estructura Base
    alto_int = alto - zocalo - (espesor * 2) 
    ancho_int_total = ancho - (espesor * 2)
    
    piezas.append({"Pieza": "Lat. Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_int_total, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
    
    if cant_columnas > 1:
        piezas.append({"Pieza": "Divisor Vert", "Cant": cant_columnas-1, "Largo": alto_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

    descuento_parantes = (cant_columnas - 1) * espesor
    ancho_hueco = (ancho_int_total - descuento_parantes) / cant_columnas

    # B. Columnas
    for i, conf in enumerate(configuracion_columnas):
        
        # CAJONES
        if conf["inf_tipo"] == "Cajonera":
            cant = conf["inf_data"]["cant"]
            h_modulo_total = conf["inf_data"]["alto"]
            
            # TAPA CAJONERA
            piezas.append({
                "Pieza": f"Tapa Cajonera (Col {i+1})", "Cant": 1, 
                "Largo": ancho_hueco, "Ancho": prof, "Veta": "↔️ Horiz", 
                "Mat": f"Melamina {espesor}", "Nota": "Estructural"
            })
            
            h_disponible_frentes = h_modulo_total - espesor
            luz = 3
            alto_frente_real = (h_disponible_frentes - ((cant - 1) * luz)) / cant
            
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant, "Largo": ancho_hueco-4, "Ancho": alto_frente_real, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
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

        # PUERTAS
        def calc_bisagras(h):
            return 2 if h < 900 else (3 if h < 1600 else (4 if h < 2100 else 5))

        if "Puerta" in conf["inf_tipo"]:
            h = conf["inf_data"]["alto"] if conf["inf_tipo"] == "Puerta Baja" else (alto - zocalo)
            piezas.append({"Pieza": conf["inf_tipo"], "Cant": 1, "Largo": h-4, "Ancho": ancho_hueco-4, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            compras.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": calc_bisagras(h), "Unidad": "u.", "Costo": costo_bisagra})

        if conf["sup_tipo"] == "Puerta Alta":
             h_usada = conf["inf_data"].get("alto", 0)
             h_rest = alto - zocalo - h_usada
             piezas.append({"Pieza": "Puerta Alta", "Cant": 1, "Largo": h_rest-4, "Ancho": ancho_hueco-4, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
             compras.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": calc_bisagras(h_rest), "Unidad": "u.", "Costo": costo_bisagra})

        # ESTANTES
        if conf["sup_tipo"] == "Estantes":
            cant = conf["sup_data"]["cant"]
            piezas.append({"Pieza": "Estante Móvil", "Cant": cant, "Largo": ancho_hueco-2, "Ancho": prof-20, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
            compras.append({"Item": "Soportes Estante", "Cant": cant*4, "Unidad": "u.", "Costo": 50})

        # BARRAL
        if conf["sup_tipo"] == "Barral":
            compras.append({"Item": "Barral Oval", "Cant": 1, "Unidad": "tira", "Nota": f"Cortar a {ancho_hueco-5:.0f}mm", "Costo": 3000})
            compras.append({"Item": "Soportes Barral", "Cant": 2, "Unidad": "u.", "Costo": 500})

    # C. Insumos Generales
    compras.insert(0, {"Item": "Tornillos 4x50", "Cant": len(piezas)*4, "Unidad": "u.", "Costo": 10})
    mts_canto = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1000
    compras.append({"Item": "Tapacanto PVC", "Cant": int(mts_canto*1.2), "Unidad": "m", "Costo": precio_canto})

    # Costos
    area_mela = sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1e6
    placas_mela = math.ceil((area_mela * 1.3) / 4.75)
    area_fondo = sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Fibro" in p["Mat"]]) / 1e6
    placas_fondo = math.ceil((area_fondo * 1.2) / 4.75)
    
    costo_total = (placas_mela * precio_placa) + (placas_fondo * precio_fondo) + sum([c.get("Costo",0) * c["Cant"] for c in compras])

    # Visualización Final
    t1, t2, t3 = st.tabs(["📋 Despiece Técnico", "🔩 Herrajes", "💰 Costos"])
    
    with t1:
        df = pd.DataFrame(piezas)
        st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
        st.download_button("📥 Bajar CSV", df.to_csv(index=False).encode(), "corte.csv")
        
    with t2:
        df_c = pd.DataFrame(compras)
        st.dataframe(df_c.groupby(["Item", "Unidad"], as_index=False).agg({"Cant": "sum", "Nota": "first"}), use_container_width=True, hide_index=True)
        
    with t3:
        st.info(f"Costo Materiales Aprox: $ {costo_total:,.0f}")
