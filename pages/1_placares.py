import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(page_title="CarpinterIA V25 - CAM Veta Pro", page_icon="🗄️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; border-radius: 4px 4px 0 0; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. BARRA LATERAL (NAVEGACIÓN Y AJUSTES GLOBALES)
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

    with st.expander("🪵 1. Tableros y Materiales", expanded=True):
        espesor = st.selectbox("Espesor Estructural", [18, 15], index=0)
        fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
        
        formato_placa = st.selectbox("Formato de Placa (Melamina)", ["2750 x 1830 mm (Estándar Faplac)", "2600 x 1830 mm (Sadepan)", "2800 x 2070 mm (Egger)", "Personalizada..."])
        if "Personalizada" in formato_placa:
            c1_p, c2_p = st.columns(2)
            placa_largo = c1_p.number_input("Largo (mm)", 1000, 4000, 2750)
            placa_ancho = c2_p.number_input("Ancho (mm)", 1000, 3000, 1830)
        else:
            placa_largo = int(formato_placa.split("x")[0].strip())
            placa_ancho = int(formato_placa.split("x")[1].split("mm")[0].strip())
        
        tipo_canto = st.selectbox("Tipo de Canto", ["Melamínico 0.45mm", "PVC 0.45mm", "PVC 2mm ABS"], index=1)
        veta_frentes = st.radio("Veta Visual Frentes y Puertas", ["Vertical", "Horizontal"], index=0)
        zocalo = st.number_input("Altura Zócalo (mm)", value=70, step=5)

    with st.expander("🔩 2. Herrajes Estándar", expanded=False):
        tipo_corredera = st.selectbox("Correderas Cajón", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
        es_push = "Push" in tipo_corredera
        descuento_guia = 26 if ("Telescópicas" in tipo_corredera or es_push) else 25
        costo_guia_ref = 6500 if ("Telescópicas" in tipo_corredera or es_push) else 2500
        
        tipo_bisagra = st.selectbox("Bisagras Lateral", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)", "Push"])

    with st.expander("💲 3. Costos y Precios", expanded=False):
        precio_placa = st.number_input("Placa Melamina ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Placa Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input(f"Metro Canto {tipo_canto[:3]} ($)", value=800, step=50)
        c_bis = st.number_input("Bisagra ($)", value=2500, step=100)
        c_guia = st.number_input("Par Guías ($)", value=costo_guia_ref, step=500)
        c_piston = st.number_input("Pistón a Gas ($)", value=4500, step=500)
        c_kit = st.number_input("Kit Corredizo ml ($)", value=15000, step=1000)
        margen = st.number_input("Multiplicador (Ganancia)", value=2.5, step=0.1)

# ==============================================================================
# HELPERS LOGICOS
# ==============================================================================
def get_limit(h):
    return max(1, int(h / 75)) if h > 0 else 1

def ui_puerta(s):
    c1, c2 = st.columns(2)
    ap = c1.selectbox("Apertura", ["Lateral", "Rebatible Arriba", "Rebatible Abajo"], key=f"ap_{s}")
    mnt = c2.selectbox("Montaje", ["Externa", "Interna"], key=f"mnt_{s}")
    dob = st.checkbox("Doble Hoja", False, key=f"d_{s}") if "Lateral" in ap else False
    
    st.caption("🔍 Interior (Detrás de la puerta)")
    t = st.radio("Tipo Interior", ["Vacío", "Estantes", "Cubos"], horizontal=True, key=f"t_int_{s}")
    d = {}
    if t == "Estantes": 
        d = {"tipo": "Estantes", "cant": st.number_input("Cant.", 1, 10, 3, key=f"e_{s}")}
    elif t == "Cubos":
        cc1, cc2 = st.columns(2)
        d = {"tipo": "Cubos", "cols": cc1.number_input("Cols", 1, 5, 2, key=f"cc_{s}"), "rows": cc2.number_input("Filas", 1, 10, 3, key=f"cr_{s}")}
    
    return {"apertura": ap, "montaje": mnt, "doble": dob, "interior": d}

configuracion_columnas = []

# ==============================================================================
# LAYOUT PRINCIPAL A DOS COLUMNAS
# ==============================================================================
col_controles, col_visual = st.columns([1.1, 1.9], gap="large")

with col_controles:
    st.header("📐 Configuración")
    
    with st.container(border=True):
        st.subheader("1. Casco General")
        c_dim1, c_dim2, c_dim3 = st.columns(3)
        ancho = c_dim1.number_input("Ancho (mm)", value=1600, step=10)
        alto = c_dim2.number_input("Alto (mm)", value=2000, step=10)
        prof = c_dim3.number_input("Prof. (mm)", value=600, step=10)
        
        st.divider()
        tiene_placard = st.toggle("🚪 Envolver con Frente Corredizo", value=False)
        hojas_placard = 0
        if tiene_placard:
            hojas_placard = st.slider("Cantidad de Hojas", 2, 4, 2)

    st.subheader("2. Diseño Interno por Columna")
    cant_columnas = st.number_input("Columnas Internas", min_value=1, max_value=5, value=2, step=1)
    tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
    
    for i, tab in enumerate(tabs):
        with tab:
            num_mods = st.radio("Módulos Verticales", [1, 2, 3, 4], index=1, horizontal=True, key=f"nm_{i}")
            
            h_total_disp = alto - zocalo
            h_acum = 0
            modulos_columna = []
            
            for m in range(num_mods):
                with st.container(border=True):
                    is_top = (m == num_mods - 1)
                    etiqueta = "Inferior" if m == 0 else ("Superior" if is_top else "Medio")
                    st.markdown(f"**Módulo {m+1} ({etiqueta})**")
                    
                    if not is_top:
                        reserva = (num_mods - 1 - m) * 100
                        max_h_permitido = max(100, int(h_total_disp - h_acum - reserva))
                        val_sugerido = min(720, max_h_permitido)
                        h_mod = st.number_input("Alto (mm)", min_value=100, max_value=max_h_permitido, value=val_sugerido, step=10, key=f"h_{i}_{m}")
                        h_acum += h_mod
                    else:
                        h_mod = h_total_disp - h_acum
                        st.caption(f"Alto calculado (Espacio restante): {h_mod}mm")
                    
                    if h_mod < 70:
                        st.error("Sin espacio útil")
                        modulos_columna.append({"tipo": "Vacío", "alto": h_mod, "h_util": h_mod, "data": {}})
                        continue

                    h_util = h_mod - (espesor if not is_top else 0)

                    tipo = st.selectbox("Componente", ["Vacío", "Cajonera", "Puerta", "Estantes", "Cubos", "Barral"], key=f"tc_{i}_{m}", label_visibility="collapsed")
                    
                    data = {}
                    if tipo == "Cajonera":
                        mc = get_limit(h_util)
                        data["cant"] = st.number_input("Cajones", 1, mc, min(3 if m==0 else 2, mc), key=f"q_{i}_{m}")
                    elif tipo == "Puerta":
                        data = ui_puerta(f"p_{i}_{m}")
                    elif tipo == "Estantes":
                        data["cant"] = st.number_input("Estantes", 1, 15, 3, key=f"es_{i}_{m}")
                    elif tipo == "Cubos":
                        cc1, cc2 = st.columns(2)
                        data["cols"] = cc1.number_input("Columnas", 1, 5, 2, key=f"c_col_{i}_{m}")
                        data["rows"] = cc2.number_input("Filas", 1, 10, 3, key=f"c_row_{i}_{m}")

                    modulos_columna.append({
                        "tipo": tipo, 
                        "alto": h_mod,
                        "h_util": h_util,
                        "data": data
                    })
            
            configuracion_columnas.append(modulos_columna)

with col_visual:
    c_v1, c_v2 = st.columns([1, 1])
    with c_v1:
        st.header("👁️ Previsualización")
    with c_v2:
        modo_vista = st.radio("Modo", ["📐 Planos 2D (Cotas)", "📦 Render 3D"], horizontal=True, label_visibility="collapsed")
    
    w_int = ancho - (espesor * 2)
    w_hueco = (w_int - ((cant_columnas - 1) * espesor)) / cant_columnas
    x_base = -ancho / 2
    y_base = 0 
    prof_int = prof - 85 if tiene_placard else prof
    
    if "3D" in modo_vista:
        fig = go.Figure()
        color_carcasa = "#5D4037"; color_estantes = "#D4AC0D"; color_cajones = "#2874A6"; color_frentes = "#85C1E9" 
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
                lighting=dict(ambient=1, diffuse=0, specular=0, roughness=1, fresnel=0))) 
            track_edges(x0, x1, y0, y1, z0, z1)

        def dibujar_plano_y(px0, px1, py, pz0, pz1, color, nombre, opacidad=0.5):
            dim_x = int(abs(px1 - px0)); dim_y = 18; dim_z = int(abs(pz1 - pz0)) 
            hover_text = f"<b>{nombre}</b><br>{dim_x} x {dim_y} x {dim_z} mm"
            fig.add_trace(go.Mesh3d(x=[px0, px1, px1, px0], y=[py, py, py, py], z=[pz0, pz0, pz1, pz1],
                i=[0, 0], j=[1, 2], k=[2, 3], opacity=opacidad, color=color, name=nombre, hoverinfo="text", text=hover_text,
                lighting=dict(ambient=1, diffuse=0, specular=0, roughness=1, fresnel=0)))
            edges_x.extend([px0, px1, px1, px0, px0, None]); edges_y.extend([py, py, py, py, py, None]); edges_z.extend([pz0, pz0, pz1, pz1, pz0, None])

        dibujar_placa(x_base, x_base + espesor, y_base, prof, 0, alto, color_carcasa, "Lateral Izquierdo")
        dibujar_placa(x_base + ancho - espesor, x_base + ancho, y_base, prof, 0, alto, color_carcasa, "Lateral Derecho")
        dibujar_placa(x_base + espesor, x_base + ancho - espesor, y_base, prof, zocalo, zocalo + espesor, color_carcasa, "Piso")
        dibujar_placa(x_base + espesor, x_base + ancho - espesor, y_base, prof, alto - espesor, alto, color_carcasa, "Techo")
        dibujar_placa(x_base + espesor, x_base + ancho - espesor, prof - fondo_esp, prof, zocalo + espesor, alto - espesor, "#D2B48C", "Fondo")
        
        if zocalo > 0:
            dibujar_placa(x_base + espesor, x_base + ancho - espesor, y_base + 25, y_base + 25 + espesor, 0, zocalo, color_carcasa, "Zócalo Frontal")
            y_trasero = prof - fondo_esp 
            dibujar_placa(x_base + espesor, x_base + ancho - espesor, y_trasero - 25 - espesor, y_trasero - 25, 0, zocalo, color_carcasa, "Zócalo Trasero")

        for i, modulos in enumerate(configuracion_columnas):
            col_x0 = x_base + espesor + i * (w_hueco + espesor)
            col_x1 = col_x0 + w_hueco
            zc = zocalo + espesor
            
            if i < cant_columnas - 1:
                dibujar_placa(col_x1, col_x1 + espesor, y_base, prof_int, zocalo + espesor, alto - espesor, color_carcasa, f"Divisor Vertical {i+1}")

            for m, mod in enumerate(modulos):
                tipo = mod["tipo"]; data = mod["data"]; h_mod = mod["alto"]; h_util = mod["h_util"]
                if m < len(modulos) - 1:
                    z_div = zc + h_util
                    dibujar_placa(col_x0, col_x1, y_base, prof_int, z_div, z_div + espesor, color_carcasa, f"Estante Fijo C{i+1} M{m+1}")

                int_y0 = y_base + 5; int_y1 = prof_int - 5

                def interior_3d(d_int, z_start):
                    if not d_int: return
                    t_int = d_int.get("tipo")
                    if t_int == "Estantes":
                        ce = d_int.get("cant", 1); pe = h_util / (ce + 1)
                        for k in range(ce):
                            ze = z_start + (pe * (k + 1))
                            dibujar_placa(col_x0 + 2, col_x1 - 2, int_y0 + 20, int_y1, ze, ze + espesor, color_estantes, f"Estante Int {k+1}")
                    elif t_int == "Cubos":
                        cols = d_int.get("cols", 1); rows = d_int.get("rows", 1)
                        ph = h_util / rows; pw = w_hueco / cols
                        for r in range(1, rows):
                            ze = z_start + (ph * r)
                            dibujar_placa(col_x0 + 2, col_x1 - 2, int_y0 + 20, int_y1, ze, ze + espesor, color_estantes, "Estante Cubo")
                        for c in range(1, cols):
                            xe = col_x0 + (pw * c)
                            dibujar_placa(xe, xe + espesor, int_y0 + 20, int_y1, z_start + 2, z_start + h_util - 2, color_estantes, "Divisor Cubo")

                if tipo == "Cajonera" and data.get("cant", 0) > 0:
                    c = data["cant"]; hu = h_util / c
                    for k in range(c): 
                        zp = zc + (k * hu) + 2
                        dibujar_placa(col_x0 + 2, col_x1 - 2, y_base, y_base + espesor, zp, zp + hu - 4, color_cajones, f"Frente Cajón C{i+1}")
                elif tipo == "Puerta":
                    interior_3d(data.get("interior"), zc)
                    mnt = data.get("montaje", "Externa")
                    dob = data.get("doble", False)
                    p_y0 = y_base - espesor if "Externa" in mnt else y_base
                    if dob:
                        mid = col_x0 + (w_hueco / 2)
                        dibujar_plano_y(col_x0 + 2, mid - 1, p_y0, zc + 2, zc + h_util - 2, color_frentes, "Puerta Izq", 0.65)
                        dibujar_plano_y(mid + 1, col_x1 - 2, p_y0, zc + 2, zc + h_util - 2, color_frentes, "Puerta Der", 0.65)
                    else:
                        dibujar_plano_y(col_x0 + 2, col_x1 - 2, p_y0, zc + 2, zc + h_util - 2, color_frentes, "Puerta", 0.65)
                elif tipo == "Estantes": interior_3d({"tipo":"Estantes", "cant":data.get("cant", 0)}, zc)
                elif tipo == "Cubos": interior_3d({"tipo":"Cubos", "cols":data.get("cols", 1), "rows":data.get("rows", 1)}, zc)
                elif tipo == "Barral": 
                    zb = zc + (h_util * 0.2) if h_util < 500 else zc + h_util - 80
                    fig.add_trace(go.Scatter3d(x=[col_x0 + 10, col_x1 - 10], y=[int_y0 + (prof_int/2)]*2, z=[zb]*2, mode='lines', line=dict(color='gray', width=12), name="Barral"))
                zc += h_mod

        if tiene_placard:
            ancho_h_visual = ancho / hojas_placard
            for h in range(hojas_placard):
                xh = x_base + (h * ancho_h_visual)
                p_y0 = y_base + 10 if h % 2 == 0 else y_base + 40
                dibujar_plano_y(xh, xh + ancho_h_visual + 20, p_y0, zocalo + 5, alto - 5, "rgba(236, 240, 241, 0.7)", f"Hoja Corrediza {h+1}", 0.6)

        fig.add_trace(go.Scatter3d(x=edges_x, y=edges_y, z=edges_z, mode='lines', line=dict(color='black', width=3), hoverinfo='skip', showlegend=False))
        no_axis = dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False, title="", visible=False)
        fig.update_layout(uirevision="cam_state", scene=dict(xaxis=no_axis, yaxis=no_axis, zaxis=no_axis, aspectmode='data'),
            margin=dict(r=0, l=0, b=0, t=0), scene_camera=dict(eye=dict(x=1.6, y=-1.6, z=0.5)), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    else:
        fig2d = go.Figure()
        fig2d.add_annotation(x=ancho/2, y=alto+150, text=f"<b>{int(ancho)} mm</b>", showarrow=False, font=dict(size=14, color="black"))
        fig2d.add_shape(type="line", x0=0, y0=alto+100, x1=ancho, y1=alto+100, line=dict(color="black", width=1))
        fig2d.add_shape(type="line", x0=0, y0=alto+80, x1=0, y1=alto+120, line=dict(color="black", width=1))
        fig2d.add_shape(type="line", x0=ancho, y0=alto+80, x1=ancho, y1=alto+120, line=dict(color="black", width=1))
        
        fig2d.add_annotation(x=-150, y=alto/2, text=f"<b>{int(alto)} mm</b>", showarrow=False, textangle=-90, font=dict(size=14, color="black"))
        fig2d.add_shape(type="line", x0=-100, y0=0, x1=-100, y1=alto, line=dict(color="black", width=1))
        fig2d.add_shape(type="line", x0=-80, y0=0, x1=-120, y1=0, line=dict(color="black", width=1))
        fig2d.add_shape(type="line", x0=-80, y0=alto, x1=-120, y1=alto, line=dict(color="black", width=1))

        fig2d.add_shape(type="rect", x0=0, y0=0, x1=espesor, y1=alto, fillcolor="#5D4037", line=dict(width=0)) 
        fig2d.add_shape(type="rect", x0=ancho-espesor, y0=0, x1=ancho, y1=alto, fillcolor="#5D4037", line=dict(width=0)) 
        fig2d.add_shape(type="rect", x0=espesor, y0=alto-espesor, x1=ancho-espesor, y1=alto, fillcolor="#5D4037", line=dict(width=0)) 
        fig2d.add_shape(type="rect", x0=espesor, y0=zocalo, x1=ancho-espesor, y1=zocalo+espesor, fillcolor="#5D4037", line=dict(width=0)) 
        
        if zocalo > 0:
            fig2d.add_shape(type="rect", x0=espesor, y0=0, x1=ancho-espesor, y1=zocalo, fillcolor="#BFC9CA", line=dict(width=0))

        for i, modulos in enumerate(configuracion_columnas):
            x_col = espesor + i * (w_hueco + espesor)
            if i < cant_columnas - 1:
                fig2d.add_shape(type="rect", x0=x_col+w_hueco, y0=zocalo+espesor, x1=x_col+w_hueco+espesor, y1=alto-espesor, fillcolor="#5D4037", line=dict(width=0))
            
            fig2d.add_annotation(x=x_col+(w_hueco/2), y=alto-espesor-30, text=f"W: {int(w_hueco)}", showarrow=False, font=dict(color="white", size=10), bgcolor="#2C3E50")

            y_curr = zocalo + espesor
            for m, mod in enumerate(modulos):
                h_mod = mod["alto"]; h_util = mod["h_util"]; tipo = mod["tipo"]
                
                if m < len(modulos) - 1:
                    fig2d.add_shape(type="rect", x0=x_col, y0=y_curr+h_util, x1=x_col+w_hueco, y1=y_curr+h_util+espesor, fillcolor="#5D4037", line=dict(width=0))
                
                if tipo == "Cajonera" and mod["data"].get("cant", 0) > 0:
                    c = mod["data"]["cant"]; hu = h_util / c
                    for k in range(c): fig2d.add_shape(type="rect", x0=x_col+2, y0=y_curr+(k*hu)+2, x1=x_col+w_hueco-2, y1=y_curr+((k+1)*hu)-2, fillcolor="#AED6F1", line=dict(color="#2874A6"))
                elif tipo == "Puerta":
                    fig2d.add_shape(type="rect", x0=x_col+2, y0=y_curr+2, x1=x_col+w_hueco-2, y1=y_curr+h_util-2, fillcolor="rgba(133, 193, 233, 0.4)", line=dict(color="#85C1E9", width=2))
                
                fig2d.add_annotation(x=x_col+w_hueco/2, y=y_curr+h_util/2, text=f"<b>H: {int(h_util)}</b><br>{tipo}", showarrow=False, font=dict(color="#5D6D7E", size=11))
                y_curr += h_mod

        fig2d.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1, visible=False, range=[-200, alto+250]), xaxis=dict(visible=False, range=[-250, ancho+250]), plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=0, b=0, l=0, r=0), height=550)
        st.plotly_chart(fig2d, use_container_width=True, config={'displayModeBar': False})

# ==============================================================================
# 5. CÁLCULO, OPTIMIZACIÓN Y RESULTADOS 
# ==============================================================================
st.markdown("---")
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    procesar = st.button("✂️ OPTIMIZAR CORTE Y PRESUPUESTO", type="primary", use_container_width=True)
    
    c_op1, c_op2 = st.columns(2)
    placa_lisa = c_op1.checkbox("🪵 Placa Lisa (Rota TODO libremente)", value=False)
    forzar_opt = c_op2.checkbox("⚠️ Forzar Optimización (Sacrifica veta en zócalos y estantes)", value=False)

if procesar:
    pz = []; buy = []; err = []
    
    # REGLA ESTRICTA: El parámetro 'Largo' ES el eje de la veta de la pieza.
    def add_p(nombre, cant, largo, ancho, veta, mat, nota=""):
        c = "-"
        if any(p in nombre for p in ["Frente", "Puerta", "Hoja", "Lat. Externo"]): c = "4L"
        elif any(p in nombre for p in ["Techo", "Piso", "Estante", "Divisor", "Zócalo", "Contra-Frente", "Lat. Cajón"]): c = "1L"
        pz.append({"Pieza": nombre, "Cant": cant, "Largo": largo, "Ancho": ancho, "Veta": veta, "Mat": mat, "Cantos": c, "Nota": nota})

    prof_int = prof - 85 if tiene_placard else prof
    h_int = alto - zocalo - (espesor * 2); w_int = ancho - (espesor * 2)
    
    # EXTERIORES Y ESTRUCTURALES
    add_p("Lat. Externo", 2, alto, prof, "Estricto", f"Mela {espesor}") 
    add_p("Techo/Piso", 2, w_int, prof, "Estricto", f"Mela {espesor}")
    
    if zocalo > 0:
        veta_zf = "Libre" if forzar_opt else "Estricto"
        add_p("Zócalo Frontal", 1, w_int, zocalo, veta_zf, f"Mela {espesor}", "Base")
        # El trasero siempre libre porque no se ve
        add_p("Zócalo Trasero", 1, w_int, zocalo, "Libre", f"Mela {espesor}", "Base")

    pz.append({"Pieza": "Fondo", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "Libre", "Mat": f"Fibro {fondo_esp}", "Cantos": "-", "Nota": ""})
    
    if cant_columnas > 1: 
        add_p("Divisor Vert", cant_columnas-1, h_int, prof_int, "Estricto", f"Mela {espesor}")
        
    w_hueco = (w_int - ((cant_columnas - 1) * espesor)) / cant_columnas
    
    if tiene_placard:
        h_hoja = alto - zocalo - 40
        w_hoja = (w_int + ((hojas_placard - 1) * 30)) / hojas_placard
        if "Vertical" in veta_frentes:
            add_p("Hoja Corrediza", hojas_placard, h_hoja, w_hoja, "Estricto", f"Mela {espesor}", "Kit Placard")
        else:
            add_p("Hoja Corrediza", hojas_placard, w_hoja, h_hoja, "Estricto", f"Mela {espesor}", "Kit Placard")
        buy.append({"Item": "Kit Corredizo (Rieles)", "Cant": ancho/1000, "Unidad": "ml", "Costo": c_kit})

    veta_estantes = "Libre" if forzar_opt else "Estricto"

    for i, modulos in enumerate(configuracion_columnas):
        for m, mod in enumerate(modulos):
            tipo = mod["tipo"]; data = mod["data"]; h_util = mod["h_util"]
            
            if m < len(modulos) - 1:
                add_p(f"Estante Fijo C{i+1}-M{m+1}", 1, w_hueco, prof_int, veta_estantes, f"Mela {espesor}", "Estructural")

            if tipo == "Cajonera":
                cant = data.get("cant", 0); 
                if cant > 0:
                    hf = (h_util - ((cant-1)*3)) / cant
                    
                    if "Vertical" in veta_frentes:
                        add_p(f"Frente Cajón C{i+1}-M{m+1}", cant, hf, w_hueco-4, "Estricto", f"Mela {espesor}")
                    else:
                        add_p(f"Frente Cajón C{i+1}-M{m+1}", cant, w_hueco-4, hf, "Estricto", f"Mela {espesor}")
                    
                    esp = hf - 30; hl = 180 if esp>=190 else (150 if esp>=160 else (100 if esp>=110 else 0))
                    if hl==0: err.append(f"C{i+1} M{m+1}: Frente muy bajo para cajón."); continue
                    
                    l_guia = min(550, max(250, int((prof_int - 15) // 50) * 50))
                    wc = w_hueco - (descuento_guia * 2) - 36
                    # Interiores de cajon van en placa Blanca, son libres de rotar allá.
                    add_p("Lat. Cajón", cant*2, l_guia, hl, "Libre", "Blanca 18")
                    add_p("Contra-Frente", cant, wc, hl, "Libre", "Blanca 18")
                    pz.append({"Pieza": "Fondo Cajón", "Cant": cant, "Largo": l_guia, "Ancho": wc, "Veta": "Libre", "Mat": "Fibro 3", "Cantos": "-", "Nota": ""})
                    buy.append({"Item": f"Guías {tipo_corredera} {l_guia}mm", "Cant": cant, "Unidad": "par", "Costo": c_guia})

            elif tipo == "Puerta":
                ap = data.get("apertura", "Lateral"); mnt = data.get("montaje", "Externa")
                dob = data.get("doble"); din = data.get("interior")
                
                dw = 4 if "Externa" in mnt else 6; dh = 4 if "Externa" in mnt else 6
                hojas = 2 if dob else 1; wa = (w_hueco - dw - (2 if dob else 0))/hojas if dob else (w_hueco - dw); ha = h_util - dh

                if "Vertical" in veta_frentes:
                    add_p(f"Puerta {ap[:3]} C{i+1}-M{m+1}", hojas, ha, wa, "Estricto", f"Mela {espesor}", mnt)
                else:
                    add_p(f"Puerta {ap[:3]} C{i+1}-M{m+1}", hojas, wa, ha, "Estricto", f"Mela {espesor}", mnt)
                
                if "Lateral" in ap:
                    bi = 2 if ha<900 else (3 if ha<1600 else (4 if ha<2100 else 5))
                    b_tipo = "Codo 18" if "Interna" in mnt else tipo_bisagra 
                    buy.append({"Item": f"Bisagras {b_tipo}", "Cant": bi*hojas, "Unidad": "u.", "Costo": c_bis})
                elif "Rebatible" in ap:
                    buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": 2, "Unidad": "u.", "Costo": c_bis})
                    buy.append({"Item": "Pistón a Gas", "Cant": 1, "Unidad": "u.", "Costo": c_piston})

                if din:
                    pint = prof_int - 20 if "Externa" in mnt else prof_int - 40 
                    if din["tipo"]=="Estantes": add_p(f"Estante Int. C{i+1}", din["cant"], w_hueco-2, pint, veta_estantes, f"Mela {espesor}")
                    elif din["tipo"]=="Cubos":
                        if din.get("cols", 1)>1: add_p("Div. Vert. Cubo", din["cols"]-1, ha-2, pint, "Estricto", f"Mela {espesor}")
                        if din.get("rows", 1)>1: add_p("Estante Cubo", din["rows"]-1, w_hueco-2, pint, veta_estantes, f"Mela {espesor}")

            elif tipo == "Estantes":
                add_p(f"Estante Móvil C{i+1}", data.get("cant", 0), w_hueco-2, prof_int-20, veta_estantes, f"Mela {espesor}")
                
            elif tipo == "Cubos":
                c = data.get("cols", 1); r = data.get("rows", 1)
                if c > 1: add_p(f"Div. Vert. Cubo C{i+1}-M{m+1}", c-1, h_util-2, prof_int-20, "Estricto", f"Mela {espesor}")
                if r > 1: add_p(f"Estante Cubo C{i+1}-M{m+1}", r-1, w_hueco-2, prof_int-20, veta_estantes, f"Mela {espesor}")
                
            elif tipo == "Barral":
                buy.append({"Item": "Barral Aluminio", "Cant": 1, "Unidad": "u.", "Costo": 3000})

    if err:
        for e in err: st.error(e)
    else:
        buy.insert(0, {"Item": "Tornillos 4x50", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 10})
        m_canto_mm = 0
        for p in pz:
            if p["Cantos"] == "4L": m_canto_mm += (p["Largo"]*2 + p["Ancho"]*2) * p["Cant"]
            elif p["Cantos"] == "1L": m_canto_mm += p["Largo"] * p["Cant"]
        buy.append({"Item": f"Canto {tipo_canto}", "Cant": math.ceil((m_canto_mm/1000)*1.2), "Unidad": "m", "Costo": precio_canto})

        t1, t2, t3 = st.tabs(["📝 Despiece", "🔩 Insumos", "✂️ Optimización de Placas (Pro)"])
        with t1: 
            df = pd.DataFrame(pz)
            st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar CSV para Corte", df.to_csv(index=False).encode(), "corte_v25_CAM.csv")
        with t2: 
            st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True, hide_index=True)
        with t3: 
            
            class PlacaOptimizada:
                def __init__(self, w, h):
                    self.w = w
                    self.h = h
                    self.free_rects = [{"x": 0, "y": 0, "w": w, "h": h}]
                    self.piezas = []

                def insertar(self, pw, ph, nombre, can_rotate):
                    best_score = float('inf')
                    best_rect_idx = -1
                    best_node = None
                    is_rot = False

                    for i, rect in enumerate(self.free_rects):
                        if pw <= rect["w"] and ph <= rect["h"]:
                            score = min(rect["w"] - pw, rect["h"] - ph)
                            if score < best_score:
                                best_score = score; best_rect_idx = i
                                best_node = {"x": rect["x"], "y": rect["y"], "w": pw, "h": ph}
                                is_rot = False
                        
                        if can_rotate and ph <= rect["w"] and pw <= rect["h"]:
                            score = min(rect["w"] - ph, rect["h"] - pw)
                            if score < best_score:
                                best_score = score; best_rect_idx = i
                                best_node = {"x": rect["x"], "y": rect["y"], "w": ph, "h": pw}
                                is_rot = True

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
            refile_perimetral = 15
            l_util = placa_largo - (refile_perimetral * 2)
            a_util = placa_ancho - (refile_perimetral * 2)
            
            st.markdown(f"**Geometría de Optimización:**")
            st.caption(f"📏 Placa Bruta: {placa_largo}x{placa_ancho}mm | 📐 Área Útil: {l_util}x{a_util}mm | ⚙️ Sierra: {esp_sierra}mm")
            
            piezas_opt = []
            for p in pz:
                if "Mela" in p["Mat"]:
                    for _ in range(p["Cant"]):
                        rotacion_permitida = placa_lisa or (p["Veta"] == "Libre")
                        piezas_opt.append({
                            "nombre": p["Pieza"], 
                            "w": p["Largo"] + esp_sierra, 
                            "h": p["Ancho"] + esp_sierra,
                            "can_rotate": rotacion_permitida
                        })
            
            # ORDENAMIENTO ESTRICTO: Primero las piezas más largas (Para que entren enteras antes de que se fragmente la placa)
            piezas_opt.sort(key=lambda item: max(item["w"], item["h"]), reverse=True)
            
            placas_usadas = []

            for p in piezas_opt:
                insertado = False
                for placa in placas_usadas:
                    if placa.insertar(p["w"], p["h"], p["nombre"], p["can_rotate"]):
                        insertado = True
                        break
                
                if not insertado:
                    nueva_placa = PlacaOptimizada(l_util, a_util)
                    nueva_placa.insertar(p["w"], p["h"], p["nombre"], p["can_rotate"])
                    placas_usadas.append(nueva_placa)

            st.success(f"✔️ Optimizado. Se requirieron **{len(placas_usadas)} placas** reales.")
            
            for idx, placa in enumerate(placas_usadas):
                fig_board = go.Figure()
                fig_board.add_shape(type="rect", x0=0, y0=0, x1=l_util, y1=a_util, line=dict(color="#34495E", width=3), fillcolor="#EAECEE")
                
                for pieza in placa.piezas:
                    px0, py0 = pieza["x"], pieza["y"]
                    px1, py1 = px0 + pieza["w"] - esp_sierra, py0 + pieza["h"] - esp_sierra
                    
                    color_p = "#E67E22" if pieza["rotada"] else "#F5B041"
                    
                    fig_board.add_shape(type="rect", x0=px0, y0=py0, x1=px1, y1=py1, line=dict(color="#17202A", width=1.5), fillcolor=color_p)
                    
                    txt = pieza["nombre"].split(" ")[0] + " " + pieza["nombre"].split(" ")[1] if " " in pieza["nombre"] else pieza["nombre"]
                    if pieza["rotada"]: txt += " 🔄"
                    fig_board.add_annotation(x=px0+((px1-px0)/2), y=py0+((py1-py0)/2), text=txt, showarrow=False, font=dict(size=10, color="black"))
                
                fig_board.update_layout(
                    title=dict(text=f"📐 Patrón de Corte - Placa #{idx+1}", font=dict(size=14)),
                    xaxis=dict(range=[-50, l_util+50], visible=False), 
                    yaxis=dict(range=[-50, a_util+50], visible=False, scaleanchor="x", scaleratio=1), 
                    margin=dict(t=40, b=10, l=10, r=10), height=400, plot_bgcolor="white"
                )
                st.plotly_chart(fig_board, use_container_width=True, config={'displayModeBar': False})
            
            c_mat = (len(placas_usadas) * precio_placa)
            c_herr = sum([c["Costo"]*c["Cant"] for c in buy])
            st.metric("PRECIO SUGERIDO DE VENTA", f"${(c_mat + c_herr) * margen:,.0f}")
