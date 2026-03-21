import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(page_title="CarpinterIA Pro", page_icon="🪚", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado para afinar detalles estéticos
st.markdown("""
    <style>
    /* Achicar espacio superior */
    .block-container { padding-top: 2rem; }
    /* Estilizar los tabs para que parezcan carpetas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; border-radius: 4px 4px 0 0; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. BARRA LATERAL (AJUSTES GLOBALES)
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063080.png", width=60) # Ícono de carpintería
    st.title("CarpinterIA")
    st.caption("v23 - Master Suite")
    st.divider()

    with st.expander("🪵 1. Tableros y Materiales", expanded=True):
        espesor = st.selectbox("Espesor Estructural", [18, 15], index=0)
        fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
        zocalo = st.number_input("Altura Zócalo (mm)", value=70, step=5)
        veta_frentes = st.radio("Veta Visual Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    with st.expander("🔩 2. Herrajes Estándar", expanded=False):
        tipo_corredera = st.selectbox("Correderas Cajón", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
        es_push = "Push" in tipo_corredera
        descuento_guia = 26 if ("Telescópicas" in tipo_corredera or es_push) else 25
        costo_guia_ref = 6500 if ("Telescópicas" in tipo_corredera or es_push) else 2500
        
        tipo_bisagra = st.selectbox("Bisagras Lateral", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)", "Push"])

    with st.expander("💲 3. Costos y Precios", expanded=False):
        precio_placa = st.number_input("Placa Melamina ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Placa Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input("Metro Canto ($)", value=800, step=50)
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

configuracion_columnas = []

# ==============================================================================
# LAYOUT PRINCIPAL A DOS COLUMNAS
# ==============================================================================
col_controles, col_visual = st.columns([1.1, 1.9], gap="large")

# ------------------------------------------------------------------------------
# ZONA IZQUIERDA: CONTROLES Y DISEÑO
# ------------------------------------------------------------------------------
with col_controles:
    st.header("📐 Configuración")
    
    # --- TARJETA 1: DIMENSIONES GLOBALES ---
    with st.container(border=True):
        st.subheader("1. Casco General")
        c_dim1, c_dim2, c_dim3 = st.columns(3)
        ancho = c_dim1.number_input("Ancho (mm)", value=1600, step=10)
        alto = c_dim2.number_input("Alto (mm)", value=2000, step=10)
        prof = c_dim3.number_input("Profundidad (mm)", value=600, step=10)
        
        st.divider()
        cant_columnas = st.number_input("Divisiones Verticales (Columnas)", min_value=1, max_value=5, value=2, step=1)
        
        tiene_placard = st.toggle("🚪 Envolver con Frente Corredizo", value=False)
        hojas_placard = 0
        if tiene_placard:
            hojas_placard = st.slider("Cantidad de Hojas", 2, 4, 2)
            if prof < 600:
                st.warning("⚠️ Profundidad < 600mm. Recomendamos más profundidad para el sistema corredizo.")

    # --- TARJETA 2: DISEÑO INTERNO ---
    st.subheader("2. Diseño Interno")
    tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
    
    for i, tab in enumerate(tabs):
        with tab:
            # Selector de estructura sutil
            modo_col = st.radio("Estructura", ["Dividida (Estante Medio)", "Entera (De piso a techo)"], horizontal=True, label_visibility="collapsed", key=f"m_{i}")
            
            detalles_inf = {}
            detalles_sup = {}
            tipo_inf = "Vacío"
            tipo_sup = "Vacío"

            # Helpers UI encapsulados
            def ui_interior(s):
                with st.expander("⚙️ Equipar interior", expanded=False):
                    t = st.radio("Tipo Interior", ["Vacío", "Estantes", "Cubos"], horizontal=True, key=f"t_{s}")
                    if t == "Estantes": 
                        return {"tipo": "Estantes", "cant": st.number_input("Cant.", 1, 10, 3, key=f"e_{s}")}
                    elif t == "Cubos":
                        c1, c2 = st.columns(2)
                        return {"tipo": "Cubos", "cols": c1.number_input("Cols", 1, 5, 2, key=f"cc_{s}"), "rows": c2.number_input("Filas", 1, 10, 3, key=f"cr_{s}")}
                    return {}

            def ui_puerta(s):
                c1, c2 = st.columns(2)
                ap = c1.selectbox("Apertura", ["Lateral", "Rebatible Arriba", "Rebatible Abajo"], key=f"ap_{s}")
                mnt = c2.selectbox("Montaje", ["Externa", "Interna"], key=f"mnt_{s}")
                dob = st.checkbox("Doble Hoja", False, key=f"d_{s}") if "Lateral" in ap else False
                return {"apertura": ap, "montaje": mnt, "doble": dob, "interior": ui_interior(s)}

            # --- MODO ENTERO ---
            if "Entera" in modo_col:
                with st.container(border=True):
                    tipo_inf = st.selectbox("Módulo Único", ["Vacío", "Cajonera", "Puerta Entera", "Estantes", "Barral"], key=f"ent_{i}")
                    h_util = alto - zocalo
                    
                    if tipo_inf == "Cajonera":
                        mc = get_limit(h_util)
                        detalles_inf = {"alto": h_util, "cant": st.number_input("Cant. Cajones", 1, mc, min(6, mc), key=f"qe_{i}")}
                    elif tipo_inf == "Puerta Entera":
                        detalles_inf = ui_puerta(f"ent_{i}")
                        detalles_inf["alto"] = h_util
                    elif tipo_inf == "Estantes": 
                        detalles_sup={"cant": st.number_input("Cant. Estantes", 1, 15, 5, key=f"es_{i}")}
                        tipo_sup="Estantes"; tipo_inf="Vacío"
                    elif tipo_inf == "Barral": 
                        tipo_sup="Barral"; tipo_inf="Vacío"

            # --- MODO DIVIDIDO ---
            else:
                # Modulo Abajo
                with st.container(border=True):
                    st.markdown("🔽 **Sector Inferior**")
                    c_tipo, c_alto = st.columns([2, 1])
                    tipo_inf = c_tipo.selectbox("Componente", ["Vacío", "Cajonera", "Puerta Baja"], key=f"inf_{i}", label_visibility="collapsed")
                    h_mod = c_alto.number_input("Alto (mm)", value=720, step=10, key=f"h_{i}")
                    
                    if tipo_inf == "Cajonera":
                        mc = get_limit(h_mod)
                        detalles_inf = {"alto": h_mod, "cant": st.number_input("Cajones", 1, mc, min(3, mc), key=f"qi_{i}")}
                    elif tipo_inf == "Puerta Baja":
                        detalles_inf = ui_puerta(f"inf_{i}")
                        detalles_inf["alto"] = h_mod
                    else:
                        detalles_inf = {"alto": h_mod}

                # Modulo Arriba
                with st.container(border=True):
                    h_rest = alto - zocalo - h_mod
                    st.markdown(f"🔼 **Sector Superior** *(Espacio libre: {h_rest}mm)*")
                    
                    if h_rest > 70:
                        tipo_sup = st.selectbox("Componente", ["Vacío", "Estantes", "Barral", "Puerta Alta", "Cajonera"], key=f"sup_{i}", label_visibility="collapsed")
                        if tipo_sup == "Cajonera":
                            mc = get_limit(h_rest)
                            detalles_sup = {"cant": st.number_input("Cajones", 1, mc, min(2, mc), key=f"qs_{i}")}
                        elif tipo_sup == "Estantes":
                            detalles_sup = {"cant": st.number_input("Estantes", 1, 10, 3, key=f"qe_s_{i}")}
                        elif tipo_sup == "Puerta Alta":
                            detalles_sup = ui_puerta(f"sup_{i}")
                    else:
                        st.error("No hay altura suficiente")
                        tipo_sup = "Vacío"

            configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup, "modo": modo_col})

# ------------------------------------------------------------------------------
# ZONA DERECHA: VISUALIZADOR Y RESULTADOS
# ------------------------------------------------------------------------------
with col_visual:
    st.header("👁️ Vista Previa en Vivo")
    
    # MOTOR GRÁFICO (Integrado aquí para usar los valores actualizados)
    fig = go.Figure()
    fig.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=400, xaxis=dict(visible=False, range=[-50, ancho+50]), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]), plot_bgcolor="#F8F9F9")

    # Casco Externo
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#34495E", line=dict(color="black")) # Zocalo oscuro
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=5))
    
    ancho_col = ancho / cant_columnas
    
    def manija(cx, cy, orientacion="v"):
        if not es_push: 
            if orientacion=="v": fig.add_shape(type="line", x0=cx, y0=cy-15, x1=cx, y1=cy+15, line=dict(color="#1A5276", width=4))
            else: fig.add_shape(type="line", x0=cx-15, y0=cy, x1=cx+15, y1=cy, line=dict(color="#1A5276", width=4))

    def interior(x0, x1, y0, h, d):
        if not d: return
        t=d.get("tipo")
        if t=="Estantes":
            c=d["cant"]; p=h/(c+1)
            for k in range(c): y=y0+(p*(k+1)); fig.add_shape(type="line", x0=x0+5, y0=y, x1=x1-5, y1=y, line=dict(color="#BA4A00", width=2, dash="dot"))
        elif t=="Cubos":
            cols=d["cols"]; rows=d["rows"]; ph=h/rows; pw=(x1-x0)/cols
            for r in range(1,rows): y=y0+(ph*r); fig.add_shape(type="line", x0=x0+5, y0=y, x1=x1-5, y1=y, line=dict(color="#BA4A00", width=2, dash="dot"))
            for c in range(1,cols): x=x0+(pw*c); fig.add_shape(type="line", x0=x, y0=y0+5, x1=x, y1=y0+h-5, line=dict(color="#BA4A00", width=2, dash="dot"))

    # Dibujar componentes internos
    for i, conf in enumerate(configuracion_columnas):
        xs = i * ancho_col; xe = (i + 1) * ancho_col; yc = zocalo 
        if i < cant_columnas: fig.add_shape(type="line", x0=xe, y0=zocalo, x1=xe, y1=alto, line=dict(color="#5D4037", width=2))

        if "Dividida" in conf["modo"]:
            y_div = zocalo + conf["inf_data"]["alto"]
            fig.add_shape(type="rect", x0=xs, y0=y_div-espesor, x1=xe, y1=y_div, fillcolor="#8B4513", line=dict(width=0))

        def dibujar_bloque(tipo, data, y_start, h_bloque):
            if tipo == "Cajonera":
                c=data["cant"]
                if c > 0:
                    hu=h_bloque/c
                    for k in range(c): 
                        yp=y_start+(k*hu)
                        fig.add_shape(type="rect", x0=xs+3, y0=yp+2, x1=xe-3, y1=yp+hu-2, fillcolor="#AED6F1", line=dict(color="#2874A6"))
                        manija(xs+ancho_col/2, yp+hu/2, "h")

            elif "Puerta" in tipo:
                interior(xs, xe, y_start, h_bloque, data.get("interior"))
                colf="rgba(169, 223, 191, 0.7)" if "Baja" in tipo else "rgba(215, 189, 226, 0.7)"
                dob=data.get("doble"); ap=data.get("apertura", "Lateral")
                
                fig.add_shape(type="rect", x0=xs+3, y0=y_start+2, x1=xe-3, y1=y_start+h_bloque-2, fillcolor=colf, line=dict(color="gray"))
                
                if dob: 
                    mid=xs+ancho_col/2
                    fig.add_shape(type="line", x0=mid, y0=y_start+2, x1=mid, y1=y_start+h_bloque-2, line=dict(color="gray", width=1))
                    manija(mid-15, y_start+h_bloque/2); manija(mid+15, y_start+h_bloque/2)
                else: 
                    if "Arriba" in ap: manija(xs+ancho_col/2, y_start+30, "h")
                    elif "Abajo" in ap: manija(xs+ancho_col/2, y_start+h_bloque-30, "h")
                    else: 
                        px=xe-20 if i%2==0 else xs+20
                        manija(px, y_start+h_bloque/2)

            elif tipo == "Estantes": interior(xs, xe, y_start, h_bloque, {"tipo":"Estantes","cant":data["cant"]})
            elif tipo == "Barral": 
                yb=y_start+(h_bloque*0.2) if h_bloque<500 else y_start+100
                fig.add_shape(type="line", x0=xs+10, y0=yb, x1=xe-10, y1=yb, line=dict(color="gray", width=5))
                fig.add_annotation(x=xs+ancho_col/2, y=yb-30, text="👕", showarrow=False)

        # Inf
        h_inf = conf["inf_data"].get("alto", 0)
        h_util_inf = h_inf - espesor if "Dividida" in conf["modo"] else h_inf
        dibujar_bloque(conf["inf_tipo"], conf["inf_data"], yc, h_util_inf)
        yc += h_inf

        # Sup
        rest = alto - yc
        if rest > 0: dibujar_bloque(conf["sup_tipo"], conf["sup_data"], yc, rest)

    # Frente Corredizo (Overlay visual)
    if tiene_placard:
        ancho_h_visual = ancho / hojas_placard
        fig.add_shape(type="line", x0=0, y0=zocalo, x1=ancho, y1=zocalo, line=dict(color="#7F8C8D", width=6))
        fig.add_shape(type="line", x0=0, y0=alto, x1=ancho, y1=alto, line=dict(color="#7F8C8D", width=6))
        for h in range(hojas_placard):
            xh = h * ancho_h_visual
            fig.add_shape(type="rect", x0=xh, y0=zocalo+3, x1=xh+ancho_h_visual+15, y1=alto-3, fillcolor="rgba(236, 240, 241, 0.7)", line=dict(color="#95A5A6", width=2))
            fig.add_shape(type="line", x0=xh+10, y0=zocalo+10, x1=xh+10, y1=alto-10, line=dict(color="#7F8C8D", width=4))

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # ------------------------------------------------------------------------------
    # MOTOR DE CÁLCULO
    # ------------------------------------------------------------------------------
    st.header("📋 Resultados")
    
    procesar = st.button("🚀 PROCESAR DESPIECE Y PRESUPUESTO", type="primary", use_container_width=True)

    if procesar:
        pz = []; buy = []; err = []
        
        def add_p(nombre, cant, largo, ancho, veta, mat, nota=""):
            # Lógica simple de tapacantos
            c = "4L" if ("Frente" in nombre or "Puerta" in nombre or "Hoja" in nombre) else ("1L" if "Lat. Caj" in nombre or "Contra" in nombre or "Estante" in nombre or "Techo" in nombre or "Piso" in nombre or "Divisor" in nombre or "Lat. Externo" in nombre else "-")
            pz.append({"Pieza": nombre, "Cant": cant, "Largo": largo, "Ancho": ancho, "Veta": veta, "Mat": mat, "Cantos": c, "Nota": nota})

        prof_int = prof - 85 if tiene_placard else prof
        h_int = alto - zocalo - (espesor * 2); w_int = ancho - (espesor * 2)
        
        add_p("Lat. Externo", 2, alto, prof, "↕️", f"Mela {espesor}") 
        add_p("Techo/Piso", 2, w_int, prof, "↔️", f"Mela {espesor}")
        add_p("Fondo", 1, alto-15, ancho-15, "-", f"Fibro {fondo_esp}")
        
        if cant_columnas > 1: add_p("Divisor Vert", cant_columnas-1, h_int, prof_int, "↕️", f"Mela {espesor}")

        w_hueco = (w_int - ((cant_columnas - 1) * espesor)) / cant_columnas
        
        if tiene_placard:
            wa = (w_int + ((hojas_placard - 1) * 30)) / hojas_placard
            add_p("Hoja Corrediza", hojas_placard, alto-zocalo-40, wa, veta_frentes, f"Mela {espesor}", "Kit Placard")
            buy.append({"Item": "Kit Corredizo (Rieles)", "Cant": ancho/1000, "Unidad": "ml", "Costo": c_kit})

        for i, conf in enumerate(configuracion_columnas):
            if "Dividida" in conf["modo"]:
                add_p(f"Estante Fijo C{i+1}", 1, w_hueco, prof_int, "↔️", f"Mela {espesor}", "Estructural")

            def do_cajon(pos, cant, h_tot, is_sup):
                h_disp = h_tot - (espesor if ("Dividida" in conf["modo"] and not is_sup) else 0)
                hf = (h_disp - ((cant-1)*3)) / cant
                add_p(f"Frente {pos} C{i+1}", cant, w_hueco-4, hf, veta_frentes, f"Mela {espesor}")
                
                esp = hf - 30; hl = 180 if esp>=190 else (150 if esp>=160 else (100 if esp>=110 else 0))
                if hl==0: err.append(f"C{i+1}: Frente muy bajo para cajón."); return
                
                l_guia = min(550, max(250, int((prof_int - 15) // 50) * 50))
                wc = w_hueco - (descuento_guia * 2) - 36
                add_p("Lat. Cajón", cant*2, l_guia, hl, "↔️", "Blanca 18")
                add_p("Contra-Frente", cant, wc, hl, "↔️", "Blanca 18")
                add_p("Fondo Cajón", cant, l_guia, wc, "-", "Fibro 3")
                buy.append({"Item": f"Guías {tipo_corredera} {l_guia}mm", "Cant": cant, "Unidad": "par", "Costo": c_guia})

            def do_puerta(nom, h, data):
                ap = data.get("apertura", "Lateral"); mnt = data.get("montaje", "Externa")
                dob = data.get("doble"); din = data.get("interior")
                
                h_real = h - espesor if ("Dividida" in conf["modo"] and "Baja" in nom) else h
                dw = 4 if "Externa" in mnt else 6; dh = 4 if "Externa" in mnt else 6
                hojas = 2 if dob else 1
                wa = (w_hueco - dw - (2 if dob else 0))/hojas if dob else (w_hueco - dw)
                ha = h_real - dh

                add_p(f"{nom} ({ap[:3]})", hojas, ha, wa, veta_frentes, f"Mela {espesor}", mnt)
                
                if "Lateral" in ap:
                    bi = 2 if ha<900 else (3 if ha<1600 else (4 if ha<2100 else 5))
                    b_tipo = "Codo 18" if "Interna" in mnt else tipo_bisagra 
                    buy.append({"Item": f"Bisagras {b_tipo}", "Cant": bi*hojas, "Unidad": "u.", "Costo": c_bis})
                elif "Rebatible" in ap:
                    buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": 2, "Unidad": "u.", "Costo": c_bis})
                    buy.append({"Item": "Pistón a Gas", "Cant": 1, "Unidad": "u.", "Costo": c_piston})

                if din:
                    pint = prof_int - 20 if "Externa" in mnt else prof_int - 40 
                    if din["tipo"]=="Estantes": add_p("Estante Int.", din["cant"], w_hueco-2, pint, "↔️", f"Mela {espesor}")
                    elif din["tipo"]=="Cubos":
                        if din["cols"]>1: add_p("Div. Vert. Cubo", din["cols"]-1, ha-2, pint, "↕️", f"Mela {espesor}")
                        if din["rows"]>1: add_p("Estante Cubo", din["rows"]-1, w_hueco-2, pint, "↔️", f"Mela {espesor}")

            # Procesar
            d_inf = conf["inf_data"]; d_sup = conf["sup_data"]
            
            if conf["inf_tipo"] == "Cajonera": do_cajon("Inf", d_inf["cant"], d_inf["alto"], False)
            elif "Puerta" in conf["inf_tipo"]: do_puerta(conf["inf_tipo"], d_inf["alto"] if "Baja" in conf["inf_tipo"] else (alto-zocalo), d_inf)
            
            if "Dividida" in conf["modo"]:
                h_inf = d_inf.get("alto", 0); h_rest = alto - zocalo - h_inf 
                if conf["sup_tipo"] == "Cajonera": do_cajon("Sup", d_sup["cant"], h_rest, True)
                elif conf["sup_tipo"] == "Puerta Alta": do_puerta("Puerta Alta", h_rest, d_sup)
                elif conf["sup_tipo"] == "Estantes": add_p("Estante Móvil", d_sup["cant"], w_hueco-2, prof_int-20, "↔️", f"Mela {espesor}")
                elif conf["sup_tipo"] == "Barral": buy.append({"Item": "Barral", "Cant": 1, "Unidad": "u.", "Costo": 3000})

        if err:
            for e in err: st.error(e)
        else:
            buy.insert(0, {"Item": "Tornillos 4x50", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 10})
            
            # Tabs de resultados
            t1, t2, t3 = st.tabs(["📝 Despiece", "🔩 Insumos", "💰 Costos"])
            
            with t1: 
                df = pd.DataFrame(pz)
                st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
                st.download_button("📥 Exportar CSV para Corte", df.to_csv(index=False).encode(), "corte_pro.csv")
            
            with t2: 
                st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True, hide_index=True)
            
            with t3: 
                # Costo aprox (optimizado visualmente)
                placas = math.ceil((sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in pz if "Mela" in p["Mat"]])/1e6*1.3)/4.75)
                c_mat = (placas * precio_placa)
                c_herr = sum([c["Costo"]*c["Cant"] for c in buy])
                st.write(f"- Melamina necesaria: ~{placas} placas (${c_mat:,.0f})")
                st.write(f"- Total Herrajes: ${c_herr:,.0f}")
                st.metric("PRECIO DE VENTA", f"${(c_mat + c_herr) * margen:,.0f}")
