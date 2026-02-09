import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CarpinterIA: Master Suite", page_icon="🪚", layout="wide")
st.title("🪚 CarpinterIA: Diseñador y Calculista (V10)")

# --- 1. CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Materiales")
    espesor = st.selectbox("Espesor Estructura", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70)
    
    st.divider()
    st.header("🎨 Terminación")
    veta_frentes = st.radio("Veta Visual", ["↔️ Horizontal", "↕️ Vertical"], index=0)

# --- 2. MEDIDAS GLOBALES ---
col_dims, col_config = st.columns([1, 2])

with col_dims:
    st.subheader("1. Medidas del Casco")
    ancho = st.number_input("Ancho Total (mm)", 500, 3000, 1200, step=50)
    alto = st.number_input("Alto Total (mm)", 1000, 2600, 2000, step=50)
    prof = st.number_input("Profundidad (mm)", 300, 900, 550, step=50)
    
    st.subheader("2. Estructura")
    cant_columnas = st.slider("Cantidad de Columnas", 1, 4, 2)

# --- 3. CONFIGURACIÓN DETALLADA POR COLUMNA ---
configuracion_columnas = []

with col_config:
    st.subheader("3. Diseño Interior")
    tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
    
    for i, tab in enumerate(tabs):
        with tab:
            c1, c2 = st.columns(2)
            
            # --- SECTOR INFERIOR ---
            with c1:
                st.write("🔽 **Abajo**")
                tipo_inf = st.selectbox(f"Componente Inf (Col {i+1})", 
                                       ["Vacío", "Cajonera", "Puerta Baja", "Puerta Entera"], 
                                       key=f"inf_{i}")
                
                detalles_inf = {}
                if tipo_inf == "Cajonera":
                    # Dinamismo: El usuario decide cuánto espacio ocupan los cajones
                    altura_cajonera = st.slider(f"Altura del Módulo (mm)", 300, 1200, 720, key=f"h_caj_{i}")
                    cant_cajones = st.slider(f"Cant. Cajones", 2, 8, 3, key=f"qty_caj_{i}")
                    
                    # Cálculo previo para mostrar info
                    alto_frente = (altura_cajonera / cant_cajones)
                    st.caption(f"Frentes de aprox {alto_frente:.0f}mm")
                    
                    detalles_inf = {"alto": altura_cajonera, "cant": cant_cajones}
                
                elif tipo_inf == "Puerta Baja":
                    altura_puerta = st.slider(f"Altura Puerta (mm)", 300, 1200, 720, key=f"h_p_inf_{i}")
                    detalles_inf = {"alto": altura_puerta}

            # --- SECTOR SUPERIOR ---
            with c2:
                st.write("🔼 **Arriba**")
                if tipo_inf == "Puerta Entera":
                    st.info("Ocupado por puerta entera.")
                    tipo_sup = "Nada"
                    detalles_sup = {}
                else:
                    tipo_sup = st.selectbox(f"Componente Sup (Col {i+1})", 
                                           ["Estantes", "Barral", "Espacio Libre", "Puerta Alta"], 
                                           key=f"sup_{i}")
                    
                    detalles_sup = {}
                    if tipo_sup == "Estantes":
                        cant_estantes = st.slider(f"Cant. Estantes", 1, 8, 3, key=f"qty_est_{i}")
                        detalles_sup = {"cant": cant_estantes}

            # Guardamos config
            configuracion_columnas.append({
                "inf_tipo": tipo_inf, "inf_data": detalles_inf,
                "sup_tipo": tipo_sup, "sup_data": detalles_sup
            })

# --- 4. MOTOR GRÁFICO (PLOTLY) ---
def generar_grafico_v10(ancho, alto, zocalo, columnas, configs):
    fig = go.Figure()
    fig.update_layout(
        margin=dict(t=30, b=0, l=0, r=0), 
        height=400,
        xaxis=dict(showgrid=False, visible=False, range=[-50, ancho+50]),
        yaxis=dict(showgrid=False, visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]),
        plot_bgcolor="white"
    )

    # Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#34495E", line=dict(color="black")) # Zocalo
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4)) # Marco

    ancho_col = ancho / columnas
    
    for i, conf in enumerate(configs):
        x_start = i * ancho_col
        x_end = (i + 1) * ancho_col
        y_cursor = zocalo
        
        # Divisor
        if i < columnas:
             fig.add_shape(type="line", x0=x_end, y0=zocalo, x1=x_end, y1=alto, line=dict(color="#5D4037", width=2))

        # Inferior
        tipo = conf["inf_tipo"]
        data = conf["inf_data"]
        
        if tipo == "Cajonera":
            h_total = data["alto"]
            cant = data["cant"]
            h_cajon = h_total / cant
            for c in range(cant):
                y_c = y_cursor + (c * h_cajon)
                fig.add_shape(type="rect", x0=x_start+4, y0=y_c+2, x1=x_end-4, y1=y_c+h_cajon-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                fig.add_shape(type="line", x0=x_start+20, y0=y_c+(h_cajon/2), x1=x_end-20, y1=y_c+(h_cajon/2), line=dict(color="#154360", width=2))
            y_cursor += h_total

        elif tipo == "Puerta Baja":
            h_p = data["alto"]
            fig.add_shape(type="rect", x0=x_start+4, y0=y_cursor+2, x1=x_end-4, y1=y_cursor+h_p-2, fillcolor="#ABEBC6", line=dict(color="#196F3D"))
            y_cursor += h_p

        elif tipo == "Puerta Entera":
            fig.add_shape(type="rect", x0=x_start+4, y0=y_cursor+2, x1=x_end-4, y1=alto-2, fillcolor="#D2B4DE", line=dict(color="#6C3483"))
            y_cursor = alto

        # Superior
        restante = alto - y_cursor
        if restante > 0:
            tipo_sup = conf["sup_tipo"]
            data_sup = conf["sup_data"]
            
            if tipo_sup == "Estantes":
                cant = data_sup["cant"]
                paso = restante / (cant + 1)
                for e in range(cant):
                    y_e = y_cursor + (paso * (e+1))
                    fig.add_shape(type="line", x0=x_start+2, y0=y_e, x1=x_end-2, y1=y_e, line=dict(color="#6E2C00", width=2))
            
            elif tipo_sup == "Barral":
                y_b = alto - 100
                fig.add_shape(type="line", x0=x_start+10, y0=y_b, x1=x_end-10, y1=y_b, line=dict(color="gray", width=4))
                fig.add_annotation(x=x_start+(ancho_col/2), y=y_b-30, text="👕", showarrow=False)

    return fig

st.plotly_chart(generar_grafico_v10(ancho, alto, zocalo, cant_columnas, configuracion_columnas), use_container_width=True)

# --- 5. LÓGICA DE INGENIERÍA (CÁLCULO REAL) ---
if st.button("🚀 CALCULAR DESPIECE Y HERRAJES", type="primary"):
    
    piezas = []
    compras = []
    
    # A. Estructura Base
    alto_int = alto - zocalo - (espesor * 2) # Altura interna util total
    ancho_int_total = ancho - (espesor * 2)
    
    piezas.append({"Pieza": "Lateral Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": ancho_int_total, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
    piezas.append({"Pieza": "Fondo Estructural", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
    
    # Divisores
    if cant_columnas > 1:
        piezas.append({"Pieza": "Divisor Vertical", "Cant": cant_columnas-1, "Largo": alto_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

    # Calculo ancho exacto de cada columna (hueco)
    # Ancho total - (laterales + divisores) / cantidad
    descuento_espesores = (espesor * 2) + ((cant_columnas - 1) * espesor)
    ancho_hueco = (ancho - descuento_espesores) / cant_columnas

    # B. Procesar Componentes
    for conf in configuracion_columnas:
        
        # --- CAJONES (DETALLADO) ---
        if conf["inf_tipo"] == "Cajonera":
            cant = conf["inf_data"]["cant"]
            h_modulo = conf["inf_data"]["alto"]
            
            # Cálculo de frentes
            luz = 3
            alto_frente = (h_modulo / cant) - luz
            
            # Partes
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant, "Largo": ancho_hueco-4, "Ancho": alto_frente, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            
            # Estructura interna (Caja)
            lateral_h = 150 # Estándar, o podríamos calcularlo
            if alto_frente < 160: lateral_h = 100 # Si es muy bajo el frente
            
            piezas.append({"Pieza": "Lat. Cajón", "Cant": cant*2, "Largo": 500, "Ancho": lateral_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
            piezas.append({"Pieza": "Contra-Frente", "Cant": cant, "Largo": ancho_hueco-90, "Ancho": lateral_h, "Veta": "↔️ Horiz", "Mat": "Blanca 18mm"})
            piezas.append({"Pieza": "Fondo Cajón", "Cant": cant, "Largo": 500, "Ancho": ancho_hueco-90, "Veta": "---", "Mat": "Fibro 3mm"})
            
            # Herrajes Cajón
            compras.append({"Item": "Correderas 500mm", "Cant": cant, "Unidad": "pares", "Nota": "Z o Telescópicas"})
            compras.append({"Item": "Tornillos 3.5x16", "Cant": cant*12, "Unidad": "u.", "Nota": "Fijación guías"})
        
        # --- PUERTAS ---
        # Función auxiliar para calcular bisagras
        def calc_bisagras(h):
            if h < 900: return 2
            if h < 1600: return 3
            if h < 2100: return 4
            return 5

        if conf["inf_tipo"] == "Puerta Baja":
            h_p = conf["inf_data"]["alto"]
            piezas.append({"Pieza": "Puerta Baja", "Cant": 1, "Largo": h_p-4, "Ancho": ancho_hueco-4, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            compras.append({"Item": "Bisagras 35mm", "Cant": calc_bisagras(h_p), "Unidad": "u.", "Nota": "Codo 0 o 9/18 según posición"})

        if conf["inf_tipo"] == "Puerta Entera":
            h_p = alto - zocalo
            piezas.append({"Pieza": "Puerta Entera", "Cant": 1, "Largo": h_p-4, "Ancho": ancho_hueco-4, "Veta": veta_frentes, "Mat": f"Melamina {espesor}"})
            compras.append({"Item": "Bisagras 35mm", "Cant": calc_bisagras(h_p), "Unidad": "u.", "Nota": ""})

        # --- ESTANTES ---
        if conf["sup_tipo"] == "Estantes":
            cant = conf["sup_data"]["cant"]
            piezas.append({"Pieza": "Estante Móvil", "Cant": cant, "Largo": ancho_hueco-2, "Ancho": prof-20, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
            compras.append({"Item": "Soportes Estante", "Cant": cant*4, "Unidad": "u.", "Nota": "Metal o Plástico"})

        # --- BARRAL ---
        if conf["sup_tipo"] == "Barral":
            compras.append({"Item": "Barral Oval", "Cant": 1, "Unidad": "tira", "Nota": f"Cortar a {int(ancho_hueco-5)}mm"})
            compras.append({"Item": "Soportes Barral", "Cant": 2, "Unidad": "u.", "Nota": ""})

    # C. Insumos Generales
    tornillos_4x50 = (len(piezas) * 4) # Estimado estructural
    compras.insert(0, {"Item": "Tornillos 4x50", "Cant": tornillos_4x50, "Unidad": "u.", "Nota": "Estructura"})
    
    # Tapacantos
    metros_lineales = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in piezas if "Melamina" in p["Mat"]]) / 1000
    compras.append({"Item": "Tapacanto PVC", "Cant": int(metros_lineales*1.2), "Unidad": "m", "Nota": "Incluye desp."})

    # --- RESULTADOS ---
    c_izq, c_der = st.columns([1.5, 1])
    
    with c_izq:
        st.write("### 📋 Listado de Corte (Despiece)")
        df_piezas = pd.DataFrame(piezas)
        st.dataframe(df_piezas.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
        
        # Descarga
        csv = df_piezas.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Bajar CSV para Maderera", csv, "corte_v10.csv", "text/
