import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y UI/UX PRO MAX (ESTILOS GLOBALES)
# ==============================================================================
st.set_page_config(page_title="CarpinterIA - Escritorios Pro", page_icon="🪑", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* 1. Reset de márgenes y eliminación de header nativo */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 98% !important; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 2. Estilo Tarjetas Flotantes (UI Pro Max) para contenedores */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid rgba(44, 62, 80, 0.1) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        background-color: #ffffff !important;
        padding: 5px !important;
        transition: all 0.2s ease-in-out;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
    }

    /* 3. Estilo de Pestañas (Tabs) tipo macOS */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        background-color: #F8F9F9;
        padding: 8px 10px 0px 10px;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [data-baseweb="tab"] { 
        padding: 10px 20px; 
        border-radius: 6px 6px 0 0; 
        border: none !important;
        background-color: transparent;
        font-weight: 600;
        color: #7F8C8D;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { 
        background-color: #FFFFFF; 
        color: #E67E22;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
    }

    /* 4. Títulos más limpios */
    h1, h2, h3 { font-family: 'Trebuchet MS', sans-serif !important; color: #2C3E50 !important; }
    
    /* 5. Botón de Procesar Destacado */
    [data-testid="baseButton-primary"] {
        background-color: #E67E22 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(230, 126, 34, 0.3) !important;
    }
    [data-testid="baseButton-primary"]:hover {
        background-color: #D35400 !important;
        box-shadow: 0 6px 8px rgba(211, 84, 0, 0.4) !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. BARRA LATERAL (IDÉNTICA A PLACARES PARA CONSISTENCIA)
# ==============================================================================
with st.sidebar:
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        .stPageLink a {
            font-family: 'Trebuchet MS', 'Lucida Sans Unicode', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.15rem !important;
            color: #2C3E50 !important;
            padding-top: 5px;
            padding-bottom: 5px;
        }
        .stPageLink a:hover { color: #E67E22 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.title("CarpinterIA")
    st.markdown("### 📍 Navegación")
    st.page_link("app.py", label="Menú Principal", icon="🏠")
    st.page_link("pages/1_placares.py", label="Módulo Placares", icon="🗄️")
    st.page_link("pages/2_escritorios.py", label="Módulo Escritorios", icon="🪑")
    st.divider()

    with st.expander("🪵 1. Tableros y Materiales", expanded=True):
        espesor = st.selectbox("Espesor Estructural", [18, 15], index=0)
        fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
        
        formato_placa = st.selectbox("Formato de Placa", ["2750 x 1830 mm (Estándar Faplac)", "2600 x 1830 mm (Sadepan)", "2800 x 2070 mm (Egger)", "Personalizada..."])
        if "Personalizada" in formato_placa:
            c1_p, c2_p = st.columns(2)
            placa_largo = c1_p.number_input("Largo (mm)", 1000, 4000, 2750)
            placa_ancho = c2_p.number_input("Ancho (mm)", 1000, 3000, 1830)
        else:
            placa_largo = int(formato_placa.split("x")[0].strip())
            placa_ancho = int(formato_placa.split("x")[1].split("mm")[0].strip())
        
        tipo_canto = st.selectbox("Tipo de Canto", ["Melamínico 0.45mm", "PVC 0.45mm", "PVC 2mm ABS"], index=2) # 2mm por defecto para escritorios
        veta_frentes = st.radio("Veta Cajones/Puertas", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    with st.expander("🔩 2. Herrajes Estándar", expanded=False):
        tipo_corredera = st.selectbox("Correderas Cajón", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
        descuento_guia = 26 if ("Telescópicas" in tipo_corredera or "Push" in tipo_corredera) else 25
        costo_guia_ref = 6500 if ("Telescópicas" in tipo_corredera or "Push" in tipo_corredera) else 2500

    with st.expander("💲 3. Costos y Precios", expanded=False):
        precio_placa = st.number_input("Placa Melamina ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Placa Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input(f"Metro Canto ($)", value=1200, step=50) # Canto 2mm es más caro
        c_guia = st.number_input("Par Guías ($)", value=costo_guia_ref, step=500)
        margen = st.number_input("Multiplicador (Ganancia)", value=2.5, step=0.1)

# ==============================================================================
# LAYOUT PRINCIPAL: WORKSPACE
# ==============================================================================
visor_container = st.container()
st.markdown("---")

# ------------------------------------------------------------------------------
# PANEL INFERIOR: CONFIGURACIÓN
# ------------------------------------------------------------------------------
col_casco, col_interno = st.columns([1, 1], gap="large")

with col_casco:
    st.header("📐 Dimensiones Generales")
    with st.container(border=True):
        c_dim1, c_dim2, c_dim3 = st.columns(3)
        ancho = c_dim1.number_input("Ancho Total (mm)", value=1200, step=10)
        alto = c_dim2.number_input("Alto Total (mm)", value=750, step=10)
        prof = c_dim3.number_input("Prof. Tapa (mm)", value=600, step=10)
        
        st.divider()
        st.subheader("Estructura Base")
        tipo_patas = st.radio("Soporte Lateral", ["Placa Entera", "Cajonera Lado Izquierdo", "Cajonera Lado Derecho", "Doble Cajonera"], horizontal=True)
        tiene_faldon = st.toggle("Incluir Faldón Estructural (Recomendado para evitar pandeo)", value=True)
        if tiene_faldon:
            alto_faldon = st.slider("Alto del Faldón (mm)", 150, 400, 250, step=10)
        else:
            alto_faldon = 0

with col_interno:
    st.header("🗄️ Cajoneras")
    if "Cajonera" in tipo_patas:
        with st.container(border=True):
            c_c1, c_c2 = st.columns(2)
            w_cajonera = c_c1.number_input("Ancho Cajonera (mm)", min_value=300, max_value=600, value=400, step=10)
            prof_cajonera = c_c2.number_input("Prof. Cajonera (mm)", min_value=300, max_value=prof, value=min(500, prof), step=10)
            
            st.divider()
            cant_cajones = st.slider("Cantidad de Cajones", 1, 5, 3)
            tipo_apertura = st.radio("Apertura Cajones", ["Manijas (Sin descuento)", "Perfil Gola / Uñero (Descuento superior)"], horizontal=True)
            descuento_gola = 30 if "Gola" in tipo_apertura else 0
    else:
        st.info("💡 Seleccioná una opción con Cajonera en el panel izquierdo para configurar sus detalles.")
        w_cajonera, prof_cajonera, cant_cajones, descuento_gola = 0, 0, 0, 0

# ------------------------------------------------------------------------------
# PANEL SUPERIOR: VISOR 3D/2D
# ------------------------------------------------------------------------------
with visor_container:
    c_v_left, c_v_center, c_v_right = st.columns([1, 4, 1])
    with c_v_center:
        st.header("👁️ Previsualización 3D", anchor=False)
    with c_v_right:
        st.write("") 
        modo_vista = st.radio("Modo", ["📦 Render 3D"], horizontal=True, label_visibility="collapsed") # En escritorio el 3D es el rey
    
    x_base = -ancho / 2
    y_base = 0 
    
    _, col_plot_center, _ = st.columns([0.2, 4.6, 0.2])
    
    with col_plot_center:
        fig = go.Figure()
        color_madera = "#E59866" # Color madera claro para escritorio
        color_cajones = "#5D6D7E"
        edges_x, edges_y, edges_z = [], [], []

        def track_edges(x0, x1, y0, y1, z0, z1):
            edges_x.extend([x0, x1, x1, x0, x0, None, x0, x1, x1, x0, x0, None, x0, x0, None, x1, x1, None, x1, x1, None, x0, x0, None])
            edges_y.extend([y0, y0, y1, y1, y0, None, y0, y0, y1, y1, y0, None, y0, y0, None, y0, y0, None, y1, y1, None, y1, y1, None])
            edges_z.extend([z0, z0, z0, z0, z0, None, z1, z1, z1, z1, z1, None, z0, z1, None, z0, z1, None, z0, z1, None, z0, z1, None])

        def dibujar_placa(x0, x1, y0, y1, z0, z1, color, nombre):
            dim_x = int(abs(x1 - x0)); dim_y = int(abs(y1 - y0)); dim_z = int(abs(z1 - z0))
            hover_text = f"<b>{nombre}</b><br>{dim_x} x {dim_y} x {dim_z} mm"
            fig.add_trace(go.Mesh3d(x=[x0,x1,x1,x0,x0,x1,x1,x0], y=[y0,y0,y1,y1,y0,y0,y1,y1], z=[z0,z0,z0,z0,z1,z1,z1,z1],
                i=[7,0,0,0,4,4,3,3,7,2,6,6], j=[3,4,1,2,5,6,2,3,6,7,1,2], k=[0,7,2,3,6,7,1,0,2,5,5,1],
                opacity=1, color=color, flatshading=True, name=nombre, hoverinfo="text", text=hover_text,
                lighting=dict(ambient=1, diffuse=0.8, specular=0.1, roughness=0.8, fresnel=0))) 
            track_edges(x0, x1, y0, y1, z0, z1)

        # 1. DIBUJAR TAPA
        dibujar_placa(x_base, x_base + ancho, y_base, prof, alto - espesor, alto, color_madera, "Tapa Escritorio")

        # 2. DIBUJAR ESTRUCTURA Y CAJONERAS
        # Lógica: La pata simple tiene profundidad de la tapa - 20mm (voladizo trasero)
        prof_pata = prof - 20 
        
        def dibujar_cajonera(x_start, nombre_lado):
            # Casco Cajonera
            dibujar_placa(x_start, x_start + espesor, y_base, prof_cajonera, 0, alto - espesor, color_madera, f"Lat. Cajonera Ext {nombre_lado}")
            dibujar_placa(x_start + w_cajonera - espesor, x_start + w_cajonera, y_base, prof_cajonera, 0, alto - espesor, color_madera, f"Lat. Cajonera Int {nombre_lado}")
            dibujar_placa(x_start + espesor, x_start + w_cajonera - espesor, y_base, prof_cajonera, 0, espesor, color_madera, f"Piso Cajonera {nombre_lado}")
            
            # Frentes
            h_util = alto - espesor - espesor - descuento_gola
            h_frente = (h_util - ((cant_cajones - 1) * 3)) / cant_cajones
            for k in range(cant_cajones):
                z_f = espesor + (k * h_frente) + (k * 3)
                dibujar_placa(x_start + 2, x_start + w_cajonera - 2, y_base, y_base + espesor, z_f, z_f + h_frente, color_cajones, f"Frente Cajón {k+1}")

        # Izquierda
        if "Cajonera Lado Izquierdo" in tipo_patas or "Doble" in tipo_patas:
            dibujar_cajonera(x_base, "Izq")
        else:
            dibujar_placa(x_base + 10, x_base + 10 + espesor, y_base + 10, prof_pata, 0, alto - espesor, color_madera, "Pata Izquierda")

        # Derecha
        if "Cajonera Lado Derecho" in tipo_patas or "Doble" in tipo_patas:
            dibujar_cajonera(x_base + ancho - w_cajonera, "Der")
        else:
            dibujar_placa(x_base + ancho - 10 - espesor, x_base + ancho - 10, y_base + 10, prof_pata, 0, alto - espesor, color_madera, "Pata Derecha")

        # 3. DIBUJAR FALDÓN
        if tiene_faldon:
            x_f_start = x_base + (w_cajonera if ("Izquierdo" in tipo_patas or "Doble" in tipo_patas) else 10 + espesor)
            x_f_end = x_base + ancho - (w_cajonera if ("Derecho" in tipo_patas or "Doble" in tipo_patas) else 10 + espesor)
            y_faldon = prof - 100 # Remetido 10cm desde el fondo
            dibujar_placa(x_f_start, x_f_end, y_faldon, y_faldon + espesor, alto - espesor - alto_faldon, alto - espesor, color_madera, "Faldón Estructural")

        # Dibujar contornos negros
        fig.add_trace(go.Scatter3d(x=edges_x, y=edges_y, z=edges_z, mode='lines', line=dict(color='#2C3E50', width=4), hoverinfo='skip', showlegend=False))
        
        no_axis = dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False, title="", visible=False)
        fig.update_layout(
            uirevision="cam_state", 
            scene=dict(xaxis=no_axis, yaxis=no_axis, zaxis=no_axis, aspectmode='data'),
            margin=dict(r=0, l=0, b=0, t=0), 
            scene_camera=dict(eye=dict(x=1.8, y=-1.8, z=0.8)), 
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=500
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ==============================================================================
# MOTOR CAM: DESPIECE Y OPTIMIZACIÓN (HEREDADO DE PLACARES)
# ==============================================================================
st.markdown("---")
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    procesar = st.button("✂️ GENERAR DESPIECE Y OPTIMIZAR CORTE", type="primary", use_container_width=True)
    c_op1, c_op2 = st.columns(2)
    placa_lisa = c_op1.checkbox("🪵 Placa Lisa (Rota TODO libremente para ahorro)", value=False)
    forzar_opt = c_op2.checkbox("⚠️ Forzar Optimización (Ignora veta de piezas no visibles)", value=False)

if procesar:
    pz = []; buy = []; err = []
    
    # REGLA ESTRICTA DE VETA: Largo = Dirección de la veta.
    def add_p(nombre, cant, largo_veta, ancho_contra_veta, veta, mat, nota=""):
        c = "4L" if ("Tapa" in nombre or "Frente" in nombre or "Pata" in nombre) else "1L"
        pz.append({"Pieza": nombre, "Cant": cant, "Largo": largo_veta, "Ancho": ancho_contra_veta, "Veta": veta, "Mat": mat, "Cantos": c, "Nota": nota})

    # 1. TAPA (Veta horizontal -> Largo = ancho del escritorio)
    add_p("Tapa Escritorio", 1, ancho, prof, "Estricto", f"Mela {espesor}", "Engrosar a 36mm opcional")

    # 2. PATAS / ESTRUCTURA
    if "Cajonera Lado Izquierdo" not in tipo_patas and "Doble" not in tipo_patas:
        add_p("Pata Izquierda", 1, alto - espesor, prof - 20, "Estricto", f"Mela {espesor}") # Veta vertical (Alto = Largo)
    if "Cajonera Lado Derecho" not in tipo_patas and "Doble" not in tipo_patas:
        add_p("Pata Derecha", 1, alto - espesor, prof - 20, "Estricto", f"Mela {espesor}")
        
    if tiene_faldon:
        w_faldon = ancho - (w_cajonera if ("Izquierdo" in tipo_patas or "Doble" in tipo_patas) else 10 + espesor) - (w_cajonera if ("Derecho" in tipo_patas or "Doble" in tipo_patas) else 10 + espesor)
        veta_faldon = "Libre" if forzar_opt else "Estricto"
        add_p("Faldón Estructural", 1, w_faldon, alto_faldon, veta_faldon, f"Mela {espesor}") # Veta horizontal

    # 3. CAJONERAS
    num_cajoneras = 0
    if "Cajonera Lado Izquierdo" in tipo_patas or "Cajonera Lado Derecho" in tipo_patas: num_cajoneras = 1
    elif "Doble" in tipo_patas: num_cajoneras = 2

    if num_cajoneras > 0:
        # Casco (Veta vertical para laterales)
        add_p("Lat. Cajonera", num_cajoneras * 2, alto - espesor, prof_cajonera, "Estricto", f"Mela {espesor}")
        add_p("Piso Cajonera", num_cajoneras, w_cajonera - (espesor*2), prof_cajonera, "Libre" if forzar_opt else "Estricto", f"Mela {espesor}")
        add_p("Faja Unión Superior", num_cajoneras * 2, w_cajonera - (espesor*2), 100, "Libre", f"Mela {espesor}")
        
        # Fondo Cajonera
        pz.append({"Pieza": "Fondo Cajonera", "Cant": num_cajoneras, "Largo": alto - espesor - 15, "Ancho": w_cajonera - 15, "Veta": "Libre", "Mat": f"Fibro {fondo_esp}", "Cantos": "-", "Nota": ""})

        # Cajones Interiores
        h_util = alto - (espesor*2) - descuento_gola
        h_frente = (h_util - ((cant_cajones - 1) * 3)) / cant_cajones
        hl = 180 if h_frente>=220 else (150 if h_frente>=190 else (100 if h_frente>=140 else 80))
        l_guia = min(550, max(250, int((prof_cajonera - 15) // 50) * 50))
        wc = w_cajonera - (espesor*2) - (descuento_guia * 2)

        for _ in range(num_cajoneras):
            # Frentes
            if "Horizontal" in veta_frentes:
                add_p("Frente Cajón", cant_cajones, w_cajonera - 4, h_frente, "Estricto", f"Mela {espesor}")
            else:
                add_p("Frente Cajón", cant_cajones, h_frente, w_cajonera - 4, "Estricto", f"Mela {espesor}")
            
            # Interior (Placa blanca libre)
            add_p("Lat. Cajón Interior", cant_cajones*2, l_guia, hl, "Libre", "Blanca 18")
            add_p("Contra-Frente Interior", cant_cajones*2, wc, hl, "Libre", "Blanca 18") # x2 porque es frente y fondo interno
            pz.append({"Pieza": "Fondo Cajón", "Cant": cant_cajones, "Largo": l_guia, "Ancho": wc, "Veta": "Libre", "Mat": "Fibro 3", "Cantos": "-", "Nota": ""})
            buy.append({"Item": f"Guías {tipo_corredera} {l_guia}mm", "Cant": cant_cajones, "Unidad": "par", "Costo": c_guia})

    buy.insert(0, {"Item": "Tornillos 4x50", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 10})

    t1, t2, t3 = st.tabs(["📝 Despiece", "🔩 Insumos", "✂️ Optimizador Guillotina Pro"])
    with t1: 
        df = pd.DataFrame(pz)
        st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
    with t2: 
        st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True, hide_index=True)
    with t3: 
        class PlacaOptimizada:
            def __init__(self, w, h):
                self.w = w; self.h = h; self.free_rects = [{"x": 0, "y": 0, "w": w, "h": h}]; self.piezas = []

            def insertar(self, pw, ph, nombre, can_rotate):
                best_score = float('inf'); best_rect_idx = -1; best_node = None; is_rot = False
                for i, rect in enumerate(self.free_rects):
                    if pw <= rect["w"] and ph <= rect["h"]:
                        score = min(rect["w"] - pw, rect["h"] - ph)
                        if score < best_score:
                            best_score = score; best_rect_idx = i; best_node = {"x": rect["x"], "y": rect["y"], "w": pw, "h": ph}; is_rot = False
                    if can_rotate and ph <= rect["w"] and pw <= rect["h"]:
                        score = min(rect["w"] - ph, rect["h"] - pw)
                        if score < best_score:
                            best_score = score; best_rect_idx = i; best_node = {"x": rect["x"], "y": rect["y"], "w": ph, "h": pw}; is_rot = True

                if best_node:
                    rect = self.free_rects.pop(best_rect_idx)
                    w_r1, h_r1 = rect["w"] - best_node["w"], best_node["h"]
                    w_t1, h_t1 = rect["w"], rect["h"] - best_node["h"]
                    w_r2, h_r2 = rect["w"] - best_node["w"], rect["h"]
                    w_t2, h_t2 = best_node["w"], rect["h"] - best_node["h"]

                    if max(w_r1*h_r1, w_t1*h_t1) > max(w_r2*h_r2, w_t2*h_t2):
                        if w_r1 > 0 and h_r1 > 0: self.free_rects.append({"x": rect["x"] + best_node["w"], "y": rect["y"], "w": w_r1, "h": h_r1})
                        if w_t1 > 0 and h_t1 > 0: self.free_rects.append({"x": rect["x"], "y": rect["y"] + best_node["h"], "w": w_t1, "h": h_t1})
                    else:
                        if w_r2 > 0 and h_r2 > 0: self.free_rects.append({"x": rect["x"] + best_node["w"], "y": rect["y"], "w": w_r2, "h": h_r2})
                        if w_t2 > 0 and h_t2 > 0: self.free_rects.append({"x": rect["x"], "y": rect["y"] + best_node["h"], "w": w_t2, "h": h_t2})
                    self.piezas.append({"nombre": nombre, "x": best_node["x"], "y": best_node["y"], "w": best_node["w"], "h": best_node["h"], "rotada": is_rot})
                    return True
                return False

        esp_sierra = 4
        l_util = placa_largo - 30; a_util = placa_ancho - 30
        
        piezas_opt = []
        for p in pz:
            if "Mela" in p["Mat"]:
                for _ in range(p["Cant"]):
                    rotacion_permitida = placa_lisa or (p["Veta"] == "Libre")
                    piezas_opt.append({"nombre": p["Pieza"], "w": p["Largo"] + esp_sierra, "h": p["Ancho"] + esp_sierra, "can_rotate": rotacion_permitida})
        
        piezas_opt.sort(key=lambda item: max(item["w"], item["h"]), reverse=True)
        placas_usadas = []

        for p in piezas_opt:
            insertado = False
            for placa in placas_usadas:
                if placa.insertar(p["w"], p["h"], p["nombre"], p["can_rotate"]): insertado = True; break
            if not insertado:
                np = PlacaOptimizada(l_util, a_util); np.insertar(p["w"], p["h"], p["nombre"], p["can_rotate"]); placas_usadas.append(np)

        st.success(f"✔️ Optimizado. Placas necesarias: **{len(placas_usadas)}**")
        
        for idx, placa in enumerate(placas_usadas):
            fig_board = go.Figure()
            fig_board.add_shape(type="rect", x0=0, y0=0, x1=l_util, y1=a_util, line=dict(color="#34495E", width=3), fillcolor="#EAECEE")
            for pieza in placa.piezas:
                px0, py0 = pieza["x"], pieza["y"]; px1, py1 = px0 + pieza["w"] - esp_sierra, py0 + pieza["h"] - esp_sierra
                color_p = "#E67E22" if pieza["rotada"] else "#F5B041"
                fig_board.add_shape(type="rect", x0=px0, y0=py0, x1=px1, y1=py1, line=dict(color="#17202A", width=1.5), fillcolor=color_p)
                txt = pieza["nombre"].split(" ")[0] + (" 🔄" if pieza["rotada"] else "")
                fig_board.add_annotation(x=px0+((px1-px0)/2), y=py0+((py1-py0)/2), text=txt, showarrow=False, font=dict(size=10, color="black"))
            
            fig_board.update_layout(title=dict(text=f"📐 Placa #{idx+1}", font=dict(size=14)), xaxis=dict(range=[-50, l_util+50], visible=False), yaxis=dict(range=[-50, a_util+50], visible=False, scaleanchor="x", scaleratio=1), margin=dict(t=40, b=10, l=10, r=10), height=350)
            st.plotly_chart(fig_board, use_container_width=True, config={'displayModeBar': False})
