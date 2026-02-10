¡Entendido! Vamos a rediseñar la interfaz visual (UI) sin tocar la "inteligencia" del código.

El desafío técnico aquí es que **Streamlit lee el código de arriba a abajo**. Para poner el gráfico *arriba* pero que dependa de las medidas que escribís *abajo*, tenemos que usar "Contenedores" (`st.container`). Primero reservamos el espacio de arriba, luego dibujamos los controles de abajo, y finalmente "inyectamos" el gráfico en el espacio que reservamos al principio.

Aquí tienes la **Versión 13: Layout Profesional**.
Mantiene toda la lógica de la V12 (tapa de cajonera, herrajes, validaciones), pero con la distribución exacta que pediste.

### 💻 Copiá y pegá este código en `app.py`:

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# Configuración de página amplia
st.set_page_config(page_title="CarpinterIA: Layout Pro", page_icon="🪚", layout="wide")

# ==============================================================================
# 1. BARRA LATERAL (IZQUIERDA): GENERALIDADES Y CONFIGURACIÓN
# ==============================================================================
with st.sidebar:
    st.title("🪚 CarpinterIA")
    st.markdown("### ⚙️ Configuración General")
    
    # Materiales
    st.write("**1. Tableros**")
    espesor = st.selectbox("Espesor Estructural", [18, 15], index=0, help="Espesor de la melamina para el casco.")
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0, help="Espesor del fondo (Fibroplus/Chapadur).")
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)
    veta_frentes = st.radio("Veta Visual (Frentes)", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    st.divider()
    
    # Herrajes
    st.write("**2. Selección de Herrajes**")
    tipo_corredera = st.selectbox("Correderas", ["Telescópicas (Bolillas)", "Comunes (Z)"])
    # Lógica de descuento según corredera
    if "Telescópicas" in tipo_corredera:
        descuento_guia = 26 
        costo_guia_ref = 6500
    else:
        descuento_guia = 25 
        costo_guia_ref = 2500

    tipo_bisagra = st.selectbox("Bisagras", ["Codo 0 (Cobertura Total)", "Codo 9 (Media)", "Codo 18 (Interior)"])
    
    st.divider()
    
    # Costos
    with st.expander("💲 Lista de Precios y Costos"):
        precio_placa = st.number_input("Precio Placa Melamina ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Precio Placa Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input("Precio Metro Canto ($)", value=800, step=50)
        costo_bisagra = st.number_input("Costo x Bisagra ($)", value=2500, step=100)
        costo_guia = st.number_input("Costo x Par Correderas ($)", value=costo_guia_ref, step=500)
        margen = st.slider("Margen de Ganancia", 1.5, 4.0, 2.5)

# ==============================================================================
# 2. DEFINICIÓN DE CONTENEDORES (LAYOUT CENTRAL)
# ==============================================================================
# Definimos el orden visual: Primero Gráfico, luego Controles
contenedor_grafico = st.container() # Parte Central Superior
st.divider() # Línea divisoria visual
contenedor_controles = st.container() # Parte Central Inferior

# ==============================================================================
# 3. PARTE CENTRAL INFERIOR: MEDIDAS Y CONFIGURACIÓN (Inputs)
# ==============================================================================
with contenedor_controles:
    col_medidas, col_distribucion = st.columns([1, 2])
    
    # --- A. Medidas Generales ---
    with col_medidas:
        st.subheader("1. Medidas del Mueble")
        ancho = st.number_input("Ancho Total (mm)", 500, 3000, 1200, step=50)
        alto = st.number_input("Alto Total (mm)", 600, 2600, 2000, step=50)
        prof = st.number_input("Profundidad (mm)", 300, 900, 550, step=50)
        st.write("---")
        cant_columnas = st.slider("Cantidad de Columnas", 1, 4, 2)
        st.caption(f"🔧 Descuento guías activo: {descuento_guia}mm")

    # --- B. Configuración por Columna ---
    configuracion_columnas = []
    
    with col_distribucion:
        st.subheader("2. Distribución y Configuración")
        tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
        
        for i, tab in enumerate(tabs):
            with tab:
                c1, c2 = st.columns(2)
                
                # Sector Inferior
                with c1:
                    st.markdown("##### 🔽 Sector Inferior")
                    tipo_inf = st.selectbox(f"Componente", ["Vacío", "Cajonera", "Puerta Baja", "Puerta Entera"], key=f"inf_{i}")
                    
                    detalles_inf = {}
                    if tipo_inf == "Cajonera":
                        h_mod = st.slider(f"Altura Módulo (mm)", 300, 1200, 720, key=f"h_caj_{i}")
                        cant_caj = st.slider(f"Cant. Cajones", 2, 8, 3, key=f"qty_caj_{i}")
                        
                        # Validación visual
                        alto_frente = (h_mod - espesor) / cant_caj # Descuento tapa
                        if alto_frente < 140: st.error(f"⚠️ Cajones muy bajos ({alto_frente:.0f}mm)")
                        else: st.caption(f"ℹ️ Frentes aprox: {alto_frente:.0f}mm (Inc. tapa)")
                        
                        detalles_inf = {"alto": h_mod, "cant": cant_caj}
                    
                    elif tipo_inf == "Puerta Baja":
                        h_p = st.slider(f"Altura Puerta (mm)", 300, 1200, 720, key=f"h_p_inf_{i}")
                        detalles_inf = {"alto": h_p}

                # Sector Superior
                with c2:
                    st.markdown("##### 🔼 Sector Superior")
                    if tipo_inf == "Puerta Entera":
                        st.info("🚫 Ocupado por puerta entera.")
                        tipo_sup = "Nada"
                        detalles_sup = {}
                    else:
                        tipo_sup = st.selectbox(f"Componente", ["Estantes", "Barral", "Espacio Libre", "Puerta Alta"], key=f"sup_{i}")
                        
                        detalles_sup = {}
                        if tipo_sup == "Estantes":
                            cant_est = st.slider(f"Cant. Estantes", 1, 8, 3, key=f"qty_est_{i}")
                            detalles_sup = {"cant": cant_est}

                configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup})

# ==============================================================================
# 4. PARTE CENTRAL SUPERIOR: GRÁFICO DINÁMICO (Se inyecta ahora)
# ==============================================================================
def dibujar_mueble_tecnico(ancho, alto, zocalo, columnas, configs, espesor_mat):
    fig = go.Figure()
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=400,
        xaxis=dict(visible=False, range=[-50, ancho+50]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]),
        plot_bgcolor="white", title=f"Vista Previa: {ancho}x{alto}x{prof} mm")

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
            
            # TAPA CAJONERA
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
            # Pomo
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

# INYECTAMOS EL GRÁFICO EN EL CONTENEDOR SUPERIOR
with contenedor_grafico:
    st.plotly_chart(dibujar_mueble_tecnico(ancho, alto, zocalo, cant_columnas, configuracion_columnas, espesor), use_container_width=True)

# ==============================================================================
# 5. BOTÓN DE PROCESAR (CENTRADO ABAJO)
# ==============================================================================
st.markdown("---")
col_spacer1, col_btn, col_spacer2 = st.columns([1, 2, 1])

with col_btn:
    procesar = st.button("🚀 PROCESAR PROYECTO COMPLETO", type="primary", use_container_width=True)

# ==============================================================================
# 6. LÓGICA DE CÁLCULO (Se ejecuta al tocar el botón)
# ==============================================================================
if procesar:
    
    piezas = []
    compras = []
    
    # --- A. Estructura Base ---
    alto_int = alto - zocalo - (espesor * 2) 
    ancho_int_total = ancho - (espesor * 2)
    
    piezas.append({"Pieza": "Lat. Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_int_total, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Mueble", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
    
    if cant_columnas > 1:
        piezas.append({"Pieza": "Divisor Vert", "Cant": cant_columnas-1, "Largo": alto_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

    descuento_parantes = (cant_columnas - 1) * espesor
    ancho_hueco = (ancho_int_total - descuento_parantes) / cant_columnas

    # --- B. Procesar Columnas ---
    for i, conf in enumerate(configuracion_columnas):
        
        # CAJONES
        if conf["inf_tipo"] == "Cajonera":
            cant = conf["inf_data"]["cant"]
            h_modulo_total = conf["inf_data"]["alto"]
            
            # 1. TAPA CAJONERA
            piezas.append({
                "Pieza": f"Tapa Cajonera (Col {i+1})", "Cant": 1, 
                "Largo": ancho_hueco, "Ancho": prof, 
                "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}", "Nota": "Estructural"
            })
            
            # 2. CAJONES
            h_disponible_frentes = h_modulo_total - espesor
            luz = 3
            alto_frente_real = (h_disponible_frentes - ((cant - 1) * luz)) / cant
            
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant, "Largo": ancho_hueco-4, "Ancho": alto_frente_real, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
            # Validación Lateral
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
            compras.append({"Item": "Barral Oval", "Cant": 1, "Unidad": "tira", "Costo": 3000, "Nota": f"Cortar a {ancho_hueco-5:.0f}mm"})
            compras.append({"Item": "Soportes Barral", "Cant": 2, "Unidad": "u.", "Costo": 500})

    # --- C. RESULTADOS FINALES ---
    st.success("✅ Proyecto procesado con éxito.")
    
    # Insumos globales
    compras.insert(0, {"Item": "Tornillos 4x50", "Cant": len(piezas)*4, "Unidad": "u.", "Costo": 10})
    mts_canto = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1000
    compras.append({"Item": "Tapacanto PVC", "Cant": int(mts_canto*1.2), "Unidad": "m", "Costo": precio_canto})

    # Costos
    area_mela = sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1e6
    placas_mela = math.ceil((area_mela * 1.3) / 4.75)
    area_fondo = sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in piezas if "Fibro" in p["Mat"]]) / 1e6
    placas_fondo = math.ceil((area_fondo * 1.2) / 4.75)
    costo_total = (placas_mela * precio_placa) + (placas_fondo * precio_fondo) + sum([c.get("Costo",0) * c["Cant"] for c in compras])

    # Visualización
    t1, t2, t3 = st.tabs(["📋 Despiece Técnico", "🔩 Herrajes", "💰 Presupuesto"])
    
    with t1:
        df = pd.DataFrame(piezas)
        st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
        st.download_button("📥 Bajar CSV", df.to_csv(index=False).encode(), "corte.csv")
        
    with t2:
        df_c = pd.DataFrame(compras)
        st.dataframe(df_c.groupby(["Item", "Unidad", "Nota"], as_index=False).sum(), use_container_width=True, hide_index=True)
        
    with t3:
        c1, c2 = st.columns(2)
        c1.metric("Costo Materiales", f"$ {costo_total:,.0f}")
        c2.metric("Precio Venta", f"$ {costo_total * margen:,.0f}")

```
