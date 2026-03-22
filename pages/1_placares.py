import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(page_title="CarpinterIA Placares", page_icon="🗄️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stNumberInput, .stSelectbox, .stSlider { margin-bottom: -10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; border-radius: 4px 4px 0 0; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# HELPERS LOGICOS
# ==============================================================================
def get_limit_cajones(h_util):
    return max(1, int(h_util / 75)) if h_util > 70 else 1

# ==============================================================================
# 1. BARRA LATERAL (NAVEGACIÓN PERSONALIZADA Y AJUSTES)
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <style>
        /* Ocultar el menú lateral por defecto de Streamlit */
        [data-testid="stSidebarNav"] {display: none;}
        
        /* Tipografía personalizada para nuestros links de navegación */
        .stPageLink a {
            font-family: 'Trebuchet MS', 'Lucida Sans Unicode', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.15rem !important;
            color: #2C3E50 !important;
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .stPageLink a:hover {
            color: #E67E22 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("CarpinterIA")
    
    st.markdown("### 📍 Navegación")
    st.page_link("app.py", label="Menú Principal", icon="🏠")
    st.page_link("pages/1_placares.py", label="Módulo Placares", icon="🗄️")
    st.page_link("pages/2_escritorios.py", label="Módulo Escritorios", icon="🪑")
    st.divider()

    with st.expander("🪵 1. Materiales y Espesores", expanded=True):
        espesor = st.selectbox("Espesor Placa (mm)", [15, 18, 25], index=1)
        espesor_fondo = st.selectbox("Espesor Fondo (mm)", [3, 5.5, 18], index=0)
        tipo_canto = st.selectbox("Tipo de Canto", ["Melamínico 0.45mm", "PVC 0.45mm", "PVC 2mm ABS"], index=1)
        zocalo = st.number_input("Altura Zócalo (mm)", value=70, step=10)
    
    with st.expander("🔩 2. Herrajes Estándar", expanded=False):
        tipo_corredera = st.selectbox("Correderas Cajón", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
        es_push = "Push" in tipo_corredera
        descuento_guia = 26 if ("Telescópicas" in tipo_corredera or es_push) else 25
        costo_guia_ref = 6500 if ("Telescópicas" in tipo_corredera or es_push) else 2500
        tipo_bisagra = st.selectbox("Bisagras", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)", "Push"])

    with st.expander("💲 3. Costos y Precios", expanded=False):
        precio_placa = st.number_input("Placa Melamina ($)", value=85000, step=1000)
        precio_fondo_placa = st.number_input("Placa Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input(f"Metro Canto {tipo_canto[:3]} ($)", value=800, step=50)
        c_bis = st.number_input("Bisagra ($)", value=2500, step=100)
        c_guia = st.number_input("Par Guías ($)", value=costo_guia_ref, step=500)
        margen = st.number_input("Ganancia (Multiplicador)", value=2.5, step=0.1)

# ==============================================================================
# LAYOUT PRINCIPAL A DOS COLUMNAS
# ==============================================================================
col_controles, col_visual = st.columns([1.1, 1.9], gap="large")

# ------------------------------------------------------------------------------
# ZONA IZQUIERDA: CONTROLES Y DISEÑO DE CAJA
# ------------------------------------------------------------------------------
with col_controles:
    st.header("📐 Diseño de Módulo / Placard")
    
    with st.container(border=True):
        st.subheader("1. Dimensiones Generales")
        c_dim1, c_dim2, c_dim3 = st.columns(3)
        ancho_total = c_dim1.number_input("Ancho Total (mm)", value=800, min_value=300, step=10)
        alto_total = c_dim2.number_input("Alto Total (mm)", value=2000, min_value=400, step=10)
        prof_total = c_dim3.number_input("Prof. Total (mm)", value=550, min_value=250, step=10)
        
        st.divider()
        tiene_fondo = st.toggle("Incluir panel de fondo (Fondo ranurado/clavado)", value=True)

    st.subheader("2. Configuración Interna")
    
    h_util_caja = alto_total - zocalo - (espesor * 2)
    w_util_caja = ancho_total - (espesor * 2)
    
    with st.container(border=True):
        funcion = st.radio("Función Principal del Módulo", ["Estantes Abiertos", "Puertas", "Cajonera Mixta"], horizontal=True)
        
        config = {"funcion": funcion}
        
        if funcion == "Estantes Abiertos" or funcion == "Puertas":
            cant_estantes = st.number_input("Cantidad de Estantes Móviles/Fijos", min_value=0, max_value=10, value=3, step=1)
            config["estantes"] = cant_estantes
            if funcion == "Puertas":
                config["puertas"] = 2 if ancho_total > 600 else 1
                
        elif funcion == "Cajonera Mixta":
            c_mix1, c_mix2 = st.columns(2)
            limite_cajones = get_limit_cajones(h_util_caja)
            cant_cajones = c_mix1.number_input("Cantidad Cajones (Abajo)", min_value=1, max_value=limite_cajones, value=3)
            config["cajones"] = cant_cajones
            
            # Espacio sobrante arriba
            alto_cajones = cant_cajones * 200 # Aprox 20cm por cajon para calcular sobrante
            espacio_restante = h_util_caja - alto_cajones
            
            if espacio_restante > 300:
                tiene_puerta_sup = c_mix2.toggle("Puerta en espacio superior", value=True)
                config["puerta_sup"] = tiene_puerta_sup
            else:
                config["puerta_sup"] = False

# ------------------------------------------------------------------------------
# ZONA DERECHA: VISUALIZADOR 3D
# ------------------------------------------------------------------------------
with col_visual:
    st.header("👁️ Vista Previa 3D")
    
    # Coordenadas maestras (Centrado en X=0)
    x0 = -ancho_total / 2; x1 = ancho_total / 2
    y0 = 0; y1 = prof_total
    
    fig = go.Figure()
    
    color_carcasa = "#8B4513" # Madera oscura
    color_frentes = "#AED6F1" # Azul claro translúcido
    color_estantes = "#A0522D"
    
    def dibujar_placa(px0, px1, py0, py1, pz0, pz1, color, nombre, opacidad=1):
        dim_x = int(abs(px1 - px0)); dim_y = int(abs(py1 - py0)); dim_z = int(abs(pz1 - pz0))
        hover_text = f"<b>{nombre}</b><br>{dim_x} x {dim_y} x {dim_z} mm"
        fig.add_trace(go.Mesh3d(x=[px0,px1,px1,px0,px0,px1,px1,px0], y=[py0,py0,py1,py1,py0,py0,py1,py1], z=[pz0,pz0,pz0,pz0,pz1,pz1,pz1,pz1],
            i=[7,0,0,0,4,4,3,3,7,2,6,6], j=[3,4,1,2,5,6,2,3,6,7,1,2], k=[0,7,2,3,6,7,1,0,2,5,5,1],
            opacity=opacidad, color=color, flatshading=True, name=nombre, hoverinfo="text", text=hover_text)) 

    # CARCASA
    dibujar_placa(x0, x0 + espesor, y0, y1, zocalo, alto_total, color_carcasa, "Lateral Izquierdo")
    dibujar_placa(x1 - espesor, x1, y0, y1, zocalo, alto_total, color_carcasa, "Lateral Derecho")
    dibujar_placa(x0 + espesor, x1 - espesor, y0, y1, zocalo, zocalo + espesor, color_carcasa, "Piso")
    dibujar_placa(x0 + espesor, x1 - espesor, y0, y1, alto_total - espesor, alto_total, color_carcasa, "Techo")
    
    if zocalo > 0:
        dibujar_placa(x0 + espesor, x1 - espesor, y0, y0 + espesor, 0, zocalo, color_carcasa, "Zócalo Frontal")
        dibujar_placa(x0 + espesor, x1 - espesor, y1 - espesor, y1, 0, zocalo, color_carcasa, "Zócalo Trasero")

    if tiene_fondo:
        dibujar_placa(x0 + espesor, x1 - espesor, y1 - espesor_fondo, y1, zocalo + espesor, alto_total - espesor, "#D2B48C", "Fondo Módulo")

    # INTERIOR Y FRENTES
    int_x0 = x0 + espesor; int_x1 = x1 - espesor
    int_y0 = y0 + 5; int_y1 = y1 - (espesor_fondo if tiene_fondo else 0) - 10
    z_base = zocalo + espesor

    if funcion == "Estantes Abiertos" or funcion == "Puertas":
        cant_e = config.get("estantes", 0)
        if cant_e > 0:
            espacio_entre = h_util_caja / (cant_e + 1)
            for k in range(cant_e):
                z_e = z_base + (espacio_entre * (k + 1))
                dibujar_placa(int_x0 + 2, int_x1 - 2, int_y0 + 20, int_y1, z_e, z_e + espesor, color_estantes, f"Estante {k+1}")

        if funcion == "Puertas":
            if config["puertas"] == 1:
                dibujar_placa(x0 + 2, x1 - 2, y0 - espesor, y0, z_base - 2, alto_total - 2, color_frentes, "Puerta", 0.7)
            else:
                dibujar_placa(x0 + 2, 0 - 2, y0 - espesor, y0, z_base - 2, alto_total - 2, color_frentes, "Puerta Izq", 0.7)
                dibujar_placa(0 + 2, x1 - 2, y0 - espesor, y0, z_base - 2, alto_total - 2, color_frentes, "Puerta Der", 0.7)

    elif funcion == "Cajonera Mixta":
        cant_c = config.get("cajones", 1)
        h_bloque_cajones = cant_c * 200
        hu_frente = h_bloque_cajones / cant_c
        
        for k in range(cant_c):
            z_f_0 = z_base + (k * hu_frente) + (k * 3)
            dibujar_placa(x0 + 2, x1 - 2, y0 - espesor, y0, z_f_0, z_f_0 + hu_frente - 3, color_frentes, f"Frente Cajón {k+1}", 0.85)
            
        if config.get("puerta_sup", False):
            z_puerta_sup = z_base + h_bloque_cajones + 10
            dibujar_placa(x0 + 2, x1 - 2, y0 - espesor, y0, z_puerta_sup, alto_total - 2, color_frentes, "Puerta Superior", 0.7)
            
            h_hueco_sup = alto_total - espesor - z_puerta_sup
            z_estante_sup = z_puerta_sup + (h_hueco_sup / 2)
            dibujar_placa(int_x0 + 2, int_x1 - 2, int_y0 + 20, int_y1, z_estante_sup, z_estante_sup + espesor, color_estantes, "Estante Sup.")

    # CONFIGURACIÓN DE ESCENA LIMPIA
    max_dim = max(ancho_total, alto_total)
    no_axis = dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False, title="", visible=False)
    fig.update_layout(
        scene=dict(xaxis=no_axis, yaxis=no_axis, zaxis=no_axis, aspectmode='data'),
        margin=dict(r=0, l=0, b=0, t=0), scene_camera=dict(eye=dict(x=1.6, y=-1.6, z=0.5)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ------------------------------------------------------------------------------
    # MOTOR DE CÁLCULO E INSUMOS
    # ------------------------------------------------------------------------------
    st.markdown("---")
    
    pz = []; buy = []
    
    def add_p(nombre, cant, largo, ancho, esp, mat, nota=""):
        canto = "-"
        if any(p in nombre for p in ["Frente Cajón", "Puerta"]): canto = "4L"
        elif any(p in nombre for p in ["Lateral"]): canto = "1L" 
        elif any(p in nombre for p in ["Piso", "Techo", "Estante", "Zócalo"]): canto = "1L"
            
        pz.append({"Pieza": nombre, "Cant": cant, "Largo": largo, "Ancho": ancho, "Espesor": esp, "Mat": mat, "Cantos": canto, "Nota": nota})

    # CARCASA
    add_p("Lateral Izquierdo", 1, alto_total, prof_total, espesor, "Estruct", "Carcasa")
    add_p("Lateral Derecho", 1, alto_total, prof_total, espesor, "Estruct", "Carcasa")
    add_p("Piso", 1, w_util_caja, prof_total, espesor, "Estruct", "Carcasa")
    add_p("Techo", 1, w_util_caja, prof_total, espesor, "Estruct", "Carcasa")
    
    if zocalo > 0:
        add_p("Zócalo Frontal", 1, w_util_caja, zocalo, espesor, "Estruct", "Base")
        add_p("Zócalo Trasero", 1, w_util_caja, zocalo, espesor, "Estruct", "Base")

    if tiene_fondo:
        pz.append({"Pieza": "Fondo Módulo", "Cant": 1, "Largo": alto_total - 5, "Ancho": ancho_total - 5, "Espesor": espesor_fondo, "Mat": f"Fondo {espesor_fondo}", "Cantos": "-", "Nota": "Clavado/Ranurado"})

    # INTERIOR
    w_hueco = w_util_caja
    w_frente = w_hueco + (espesor * 2) - 4 
    prof_estante = prof_total - (espesor_fondo if tiene_fondo else 0) - 20

    if funcion == "Estantes Abiertos" or funcion == "Puertas":
        cant_e = config.get("estantes", 0)
        if cant_e > 0:
            add_p("Estante Móvil", cant_e, w_hueco - 2, prof_estante, espesor, "Estruct", "Interior")
            
        if funcion == "Puertas":
            h_frente = alto_total - zocalo - 4
            cant_p = config["puertas"]
            if cant_p == 1:
                add_p("Puerta Entera", 1, h_frente, w_frente, espesor, "Frentes", "Apertura Lateral")
                buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": 4 if h_frente > 1500 else 3, "Unidad": "u.", "Costo": c_bis})
            else:
                add_p("Puerta Media", 2, h_frente, (w_frente/2) - 2, espesor, "Frentes", "Apertura Doble")
                buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": 8 if h_frente > 1500 else 6, "Unidad": "u.", "Costo": c_bis})

    elif funcion == "Cajonera Mixta":
        cant_c = config.get("cajones", 1)
        h_bloque_cajones = cant_c * 200
        hf = (h_bloque_cajones - ((cant_c - 1) * 3)) / cant_c
        
        # Frentes
        add_p("Frente Cajón", cant_c, w_frente, hf, espesor, "Frentes", "")
        
        # Caja de cajón
        l_guia = min(500, max(250, int((prof_total - 30) // 50) * 50))
        h_lateral_cajon = max(70, int(hf - 40)) 
        w_contrafrente = w_hueco - descuento_guia - (espesor * 2)
        
        add_p("Lat. Cajón", cant_c * 2, l_guia, h_lateral_cajon, espesor, "Estruct", "Cajón")
        add_p("Contra-Frente", cant_c * 2, w_contrafrente, h_lateral_cajon, espesor, "Estruct", "Cajón")
        pz.append({"Pieza": "Fondo Cajón", "Cant": cant_c, "Largo": l_guia, "Ancho": w_hueco - descuento_guia, "Espesor": 3, "Mat": "Fibro 3", "Cantos": "-", "Nota": "Cajón"})
        buy.append({"Item": f"Guías {tipo_corredera} {l_guia}mm", "Cant": cant_c, "Unidad": "par", "Costo": c_guia})

        if config.get("puerta_sup", False):
            h_puerta_sup = alto_total - zocalo - h_bloque_cajones - 10
            add_p("Puerta Superior", 1, h_puerta_sup, w_frente, espesor, "Frentes", "Arriba de cajones")
            buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": 2, "Unidad": "u.", "Costo": c_bis})
            add_p("Estante Móvil", 1, w_hueco - 2, prof_estante, espesor, "Estruct", "Interior Sup.")

    # INSUMOS
    buy.insert(0, {"Item": "Tornillos 4x50 / Minifix", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 15})
    
    m_canto_mm = 0
    for p in pz:
        if p["Cantos"] == "4L": m_canto_mm += (p["Largo"]*2 + p["Ancho"]*2) * p["Cant"]
        elif p["Cantos"] == "1L": m_canto_mm += p["Largo"] * p["Cant"]
            
    buy.append({"Item": f"Canto {tipo_canto}", "Cant": math.ceil((m_canto_mm/1000)*1.2), "Unidad": "m", "Costo": precio_canto})

    # TABS DE RESULTADOS
    t1, t2, t3 = st.tabs(["📝 Despiece y Cantos", "🔩 Herrajes", "💰 Presupuesto"])
    with t1: 
        df = pd.DataFrame(pz)
        st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar CSV", df.to_csv(index=False).encode(), "corte_placares.csv")
    with t2: 
        st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True, hide_index=True)
    with t3: 
        placas = math.ceil((sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in pz if "Fondo" not in str(p["Mat"]) and p["Mat"]!="Fibro 3"])/1e6*1.3)/4.75)
        c_mat = (placas * precio_placa)
        c_herr = sum([c["Costo"]*c["Cant"] for c in buy])
        st.write(f"- Melamina base (estructura/frentes): ~{placas} placas (${c_mat:,.0f})")
        st.write(f"- Total Insumos (Herrajes/Cantos): ${c_herr:,.0f}")
        st.metric("PRECIO SUGERIDO VENTA", f"${(c_mat + c_herr) * margen:,.0f}")
