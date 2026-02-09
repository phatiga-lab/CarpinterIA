import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CarpinterIA: Architect", page_icon="📐", layout="wide")
st.title("📐 CarpinterIA: Diseñador de Interiores (V9)")

# --- 1. CONFIGURACIÓN LATERAL ---
with st.sidebar:
    st.header("⚙️ Materiales")
    espesor = st.selectbox("Espesor Placa", [18, 15], index=0)
    zocalo = st.number_input("Altura Zócalo", value=70)
    st.divider()
    st.info("💡 Ahora podés configurar cada columna por separado.")

# --- 2. DEFINICIÓN GLOBAL ---
col_dims, col_config = st.columns([1, 2])

with col_dims:
    st.subheader("1. Medidas Exteriores")
    ancho = st.number_input("Ancho Total (mm)", 500, 3000, 1200, step=50)
    alto = st.number_input("Alto Total (mm)", 1000, 2600, 2000, step=50)
    prof = st.number_input("Profundidad (mm)", 300, 900, 550, step=50)
    
    st.subheader("2. Estructura")
    cant_columnas = st.slider("Cantidad de Columnas", 1, 4, 2)

# --- 3. CONFIGURACIÓN DETALLADA POR COLUMNA ---
# Creamos una lista para guardar la config de cada columna
configuracion_columnas = []

with col_config:
    st.subheader("3. Diseño por Columna")
    
    # Creamos pestañas para cada columna para que sea prolijo
    tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
    
    for i, tab in enumerate(tabs):
        with tab:
            c1, c2 = st.columns(2)
            
            # --- SECTOR INFERIOR ---
            with c1:
                st.write("🔽 **Sector Inferior**")
                tipo_inf = st.selectbox(f"Componente Abajo (Col {i+1})", 
                                       ["Vacío", "Cajonera", "Puerta Baja", "Puerta Entera"], 
                                       key=f"inf_{i}")
                
                detalles_inf = {}
                if tipo_inf == "Cajonera":
                    altura_cajonera = st.slider(f"Altura Total Cajonera (mm)", 300, 1200, 700, key=f"h_caj_{i}", help="Espacio total que ocuparán los cajones")
                    cant_cajones = st.slider(f"Cantidad Cajones", 2, 8, 3, key=f"qty_caj_{i}")
                    detalles_inf = {"alto": altura_cajonera, "cant": cant_cajones}
                    
                    # Cálculo dinámico visual
                    alto_unitario = altura_cajonera / cant_cajones
                    st.caption(f"Cada cajón tendrá {alto_unitario:.0f}mm de frente.")
                
                elif tipo_inf == "Puerta Baja":
                    altura_puerta = st.slider(f"Altura Puerta (mm)", 300, 1200, 700, key=f"h_p_inf_{i}")
                    detalles_inf = {"alto": altura_puerta}

            # --- SECTOR SUPERIOR ---
            with c2:
                st.write("🔼 **Sector Superior**")
                # Si hay puerta entera, no hay sector superior
                if tipo_inf == "Puerta Entera":
                    st.info("La puerta ocupa toda la columna.")
                    tipo_sup = "Nada"
                    detalles_sup = {}
                else:
                    tipo_sup = st.selectbox(f"Componente Arriba (Col {i+1})", 
                                           ["Estantes", "Barral de Colgar", "Espacio Libre", "Puerta Alta"], 
                                           key=f"sup_{i}")
                    
                    detalles_sup = {}
                    if tipo_sup == "Estantes":
                        cant_estantes = st.slider(f"Cantidad Estantes", 1, 10, 3, key=f"qty_est_{i}")
                        detalles_sup = {"cant": cant_estantes}
                    
                    elif tipo_sup == "Puerta Alta":
                        st.caption("Ocupa el espacio restante hasta el techo.")

            # Guardamos la config de esta columna
            configuracion_columnas.append({
                "inf_tipo": tipo_inf, "inf_data": detalles_inf,
                "sup_tipo": tipo_sup, "sup_data": detalles_sup
            })

# --- 4. MOTOR GRÁFICO (PLOTLY) ---
def generar_grafico(ancho, alto, zocalo, columnas, configs):
    fig = go.Figure()
    
    # Lienzo
    fig.update_layout(
        title="Vista Previa Dinámica",
        xaxis=dict(range=[-50, ancho+50], showgrid=False, visible=False),
        yaxis=dict(range=[-50, alto+50], showgrid=False, visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="white", height=600, margin=dict(t=30, b=0, l=0, r=0)
    )

    # Zócalo y Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2c3e50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4)) # Marco

    # Ancho de cada columna
    ancho_col = ancho / columnas
    
    # DIBUJAR CONTENIDO POR COLUMNA
    for i, conf in enumerate(configs):
        x_start = i * ancho_col
        x_end = (i + 1) * ancho_col
        y_cursor = zocalo # Cursor que sube desde el zócalo
        
        # Divisor vertical (si no es la ultima)
        if i < columnas:
             fig.add_shape(type="line", x0=x_end, y0=zocalo, x1=x_end, y1=alto, line=dict(color="#5D4037", width=2))

        # --- PARTE INFERIOR ---
        tipo = conf["inf_tipo"]
        data = conf["inf_data"]
        
        if tipo == "Cajonera":
            alto_total = data["alto"]
            cant = data["cant"]
            alto_cajon = alto_total / cant
            
            for c in range(cant):
                y_cajon = y_cursor + (c * alto_cajon)
                fig.add_shape(type="rect", 
                    x0=x_start+4, y0=y_cajon+2, x1=x_end-4, y1=y_cajon+alto_cajon-2, 
                    fillcolor="#AED6F1", line=dict(color="#2874A6", width=2))
                # Manija
                fig.add_shape(type="line", x0=x_start+(ancho_col/2)-30, y0=y_cajon+(alto_cajon/2), x1=x_start+(ancho_col/2)+30, y1=y_cajon+(alto_cajon/2), line=dict(color="#2874A6", width=3))
            
            y_cursor += alto_total # Subimos el cursor

        elif tipo == "Puerta Baja":
            alto_p = data["alto"]
            fig.add_shape(type="rect", 
                x0=x_start+4, y0=y_cursor+2, x1=x_end-4, y1=y_cursor+alto_p-2, 
                fillcolor="#ABEBC6", line=dict(color="#1D8348", width=2))
            # Picaporte (derecha o izquierda según columna)
            pos_x_pica = x_end - 20 if i % 2 == 0 else x_start + 20
            fig.add_shape(type="circle", x0=pos_x_pica-5, y0=y_cursor+(alto_p/2), x1=pos_x_pica+5, y1=y_cursor+(alto_p/2)+10, fillcolor="black")
            
            y_cursor += alto_p

        elif tipo == "Puerta Entera":
            alto_p = alto - zocalo
            fig.add_shape(type="rect", 
                x0=x_start+4, y0=y_cursor+2, x1=x_end-4, y1=alto-2, 
                fillcolor="#D7BDE2", line=dict(color="#884EA0", width=2))
            pos_x_pica = x_end - 20 if i % 2 == 0 else x_start + 20
            fig.add_shape(type="circle", x0=pos_x_pica-5, y0=zocalo+900, x1=pos_x_pica+5, y1=zocalo+910, fillcolor="black")
            y_cursor = alto # Ocupa todo

        # --- PARTE SUPERIOR ---
        # El espacio restante es Alto Total - Donde quedó el cursor
        espacio_restante = alto - y_cursor
        
        if espacio_restante > 0:
            tipo_sup = conf["sup_tipo"]
            data_sup = conf["sup_data"]
            
            if tipo_sup == "Estantes":
                cant = data_sup["cant"]
                # Distribuimos los estantes en el espacio restante
                # Espacio entre estantes = Espacio / (cant + 1)
                paso = espacio_restante / (cant + 1)
                
                for e in range(cant):
                    y_est = y_cursor + (paso * (e + 1))
                    fig.add_shape(type="line", x0=x_start, y0=y_est, x1=x_end, y1=y_est, line=dict(color="#5D4037", width=3))
            
            elif tipo_sup == "Barral de Colgar":
                y_barral = alto - 100 # 10cm desde el techo
                fig.add_shape(type="line", x0=x_start+10, y0=y_barral, x1=x_end-10, y1=y_barral, line=dict(color="gray", width=5))
                # Dibujo de percha esquemática
                fig.add_annotation(x=x_start+(ancho_col/2), y=y_barral-50, text="👕", showarrow=False, font=dict(size=20))

            elif tipo_sup == "Puerta Alta":
                 fig.add_shape(type="rect", 
                    x0=x_start+4, y0=y_cursor+2, x1=x_end-4, y1=alto-2, 
                    fillcolor="#F9E79F", line=dict(color="#D4AC0D", width=2))
                 pos_x_pica = x_end - 20 if i % 2 == 0 else x_start + 20
                 fig.add_shape(type="circle", x0=pos_x_pica-5, y0=y_cursor+100, x1=pos_x_pica+5, y1=y_cursor+110, fillcolor="black")

    return fig

# --- 5. RENDERIZADO DEL GRÁFICO ---
st.markdown("---")
figura = generar_grafico(ancho, alto, zocalo, cant_columnas, configuracion_columnas)
st.plotly_chart(figura, use_container_width=True)

# --- 6. CÁLCULO DE CORTE BASADO EN EL DISEÑO ---
if st.button("🚀 GENERAR LISTA DE CORTE DE ESTE DISEÑO", type="primary"):
    piezas = []
    
    # Estructura Base
    piezas.append({"Pieza": "Lat. Externo", "Cant": 2, "Medidas": f"{alto}x{prof}", "Mat": "Melamina"})
    piezas.append({"Pieza": "Techo/Piso", "Cant": 2, "Medidas": f"{ancho-(espesor*2)}x{prof}", "Mat": "Melamina"})
    piezas.append({"Pieza": "Fondo", "Cant": 1, "Medidas": f"{alto-15}x{ancho-15}", "Mat": "Fibro"})
    
    # Divisores
    if cant_columnas > 1:
        alto_interior = alto - zocalo - (espesor*2)
        piezas.append({"Pieza": "Divisor Vertical", "Cant": cant_columnas-1, "Medidas": f"{alto_interior}x{prof}", "Mat": "Melamina"})
    
    # Iterar configuraciones para sumar piezas
    ancho_col = (ancho - (espesor * (cant_columnas + 1))) / cant_columnas # Calculo preciso de luz
    
    for conf in configuracion_columnas:
        # Cajones
        if conf["inf_tipo"] == "Cajonera":
            cant = conf["inf_data"]["cant"]
            h_total = conf["inf_data"]["alto"]
            h_frente = (h_total / cant) - 3 # Descuento luz
            
            piezas.append({"Pieza": "Frente Cajón", "Cant": cant, "Medidas": f"{int(ancho_col-4)}x{int(h_frente)}", "Mat": "Melamina"})
            piezas.append({"Pieza": "Caja Cajón", "Cant": cant, "Medidas": "Kit Estándar", "Mat": "Blanca"})
        
        # Estantes
        if conf["sup_tipo"] == "Estantes":
            cant = conf["sup_data"]["cant"]
            piezas.append({"Pieza": "Estante", "Cant": cant, "Medidas": f"{int(ancho_col-2)}x{prof-20}", "Mat": "Melamina"})
            
        # Puertas
        if conf["inf_tipo"] == "Puerta Baja":
             piezas.append({"Pieza": "Puerta Baja", "Cant": 1, "Medidas": f"{int(ancho_col-4)}x{conf['inf_data']['alto']}", "Mat": "Melamina"})
        if conf["inf_tipo"] == "Puerta Entera":
             piezas.append({"Pieza": "Puerta Entera", "Cant": 1, "Medidas": f"{int(ancho_col-4)}x{alto-zocalo-4}", "Mat": "Melamina"})
        if conf["sup_tipo"] == "Puerta Alta":
             # Hay que calcular la altura restante
             h_restante = alto - zocalo - conf["inf_data"].get("alto", 0)
             piezas.append({"Pieza": "Puerta Alta", "Cant": 1, "Medidas": f"{int(ancho_col-4)}x{int(h_restante-4)}", "Mat": "Melamina"})

    st.write("### 📋 Listado Preliminar")
    st.dataframe(pd.DataFrame(piezas), use_container_width=True)
