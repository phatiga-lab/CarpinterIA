import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(page_title="CarpinterIA Pro V24", page_icon="🪚", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; border-radius: 4px 4px 0 0; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. BARRA LATERAL (AJUSTES GLOBALES)
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063080.png", width=60)
    st.title("CarpinterIA")
    st.caption("v24 - Multi-Tier Pro")
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

def ui_interior(s):
    with st.expander("⚙️ Equipar interior", expanded=False):
        t = st.radio("Tipo Interior", ["Vacío", "Estantes", "Cubos"], horizontal=True, key=f"t_int_{s}")
        d = {}
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
    
    with st.container(border=True):
        st.subheader("1. Casco General")
        c_dim1, c_dim2, c_dim3 = st.columns(3)
        ancho = c_dim1.number_input("Ancho (mm)", value=1600, step=10)
        alto = c_dim2.number_input("Alto (mm)", value=2000, step=10)
        prof = c_dim3.number_input("Prof. (mm)", value=600, step=10)
        
        st.divider()
        cant_columnas = st.number_input("Columnas Internas", min_value=1, max_value=5, value=2, step=1)
        
        tiene_placard = st.toggle("🚪 Envolver con Frente Corredizo", value=False)
        hojas_placard = 0
        if tiene_placard:
            hojas_placard = st.slider("Cantidad de Hojas", 2, 4, 2)
            if prof < 600:
                st.warning("⚠️ Profundidad < 600mm. Recomendamos más profundidad para los rieles corredizos.")

    st.subheader("2. Diseño Interno por Columna")
    tabs = st.tabs([f"Columna {i+1}" for i in range(cant_columnas)])
    
    for i, tab in enumerate(tabs):
        with tab:
            # NUEVO: Selector de 1 a 4 módulos
            num_mods = st.radio("Módulos Verticales", [1, 2, 3, 4], index=1, horizontal=True, key=f"nm_{i}")
            
            h_total_disp = alto - zocalo
            h_acum = 0
            modulos_columna = []
            
            for m in range(num_mods):
                with st.container(border=True):
                    is_top = (m == num_mods - 1)
                    etiqueta = "Inferior" if m == 0 else ("Superior" if is_top else "Medio")
                    st.markdown(f"**Módulo {m+1} ({etiqueta})**")
                    
                    # 1. Calcular Alturas
                    if not is_top:
                        # Reservar 100mm para cada modulo restante
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

                    # 2. Descuento de Estante Fijo (Si no es el top)
                    h_util = h_mod - (espesor if not is_top else 0)

                    # 3. Selección de Componente
                    tipo = st.selectbox("Componente", ["Vacío", "Cajonera", "Puerta", "Estantes", "Barral"], key=f"tc_{i}_{m}", label_visibility="collapsed")
                    
                    data = {}
                    if tipo == "Cajonera":
                        mc = get_limit(h_util)
                        data["cant"] = st.number_input("Cajones", 1, mc, min(3 if m==0 else 2, mc), key=f"q_{i}_{m}")
                    elif tipo == "Puerta":
                        data = ui_puerta(f"p_{i}_{m}")
                    elif tipo == "Estantes":
                        data["cant"] = st.number_input("Estantes", 1, 15, 3, key=f"es_{i}_{m}")

                    modulos_columna.append({
                        "tipo": tipo, 
                        "alto": h_mod,   # Ocupación total del bloque
                        "h_util": h_util, # Espacio interno neto descontando el divisor si existe
                        "data": data
                    })
            
            configuracion_columnas.append(modulos_columna)

# ------------------------------------------------------------------------------
# ZONA DERECHA: VISUALIZADOR Y RESULTADOS
# ------------------------------------------------------------------------------
with col_visual:
    st.header("👁️ Vista Previa en Vivo")
    
    fig = go.Figure()
    fig.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=450, xaxis=dict(visible=False, range=[-50, ancho+50]), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]), plot_bgcolor="#F8F9F9")

    # Casco
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#34495E", line=dict(color="black"))
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

    # DIBUJO MULTI-MODULO
    for i, modulos in enumerate(configuracion_columnas):
        xs = i * ancho_col; xe = xs + ancho_col; yc = zocalo 
        if i < cant_columnas: fig.add_shape(type="line", x0=xe, y0=zocalo, x1=xe, y1=alto, line=dict(color="#5D4037", width=2))

        for m, mod in enumerate(modulos):
            tipo = mod["tipo"]
            data = mod["data"]
            h_mod = mod["alto"]
            h_util = mod["h_util"]
            
            # Dibujar Divisor Fijo si no es el último módulo
            if m < len(modulos) - 1:
                y_div = yc + h_mod
                fig.add_shape(type="rect", x0=xs, y0=y_div-espesor, x1=xe, y1=y_div, fillcolor="#8B4513", line=dict(width=0))

            # Dibujar Componente usando h_util
            if tipo == "Cajonera" and data.get("cant", 0) > 0:
                c = data["cant"]; hu = h_util/c
                for k in range(c): 
                    yp = yc + (k*hu)
                    fig.add_shape(type="rect", x0=xs+3, y0=yp+2, x1=xe-3, y1=yp+hu-2, fillcolor="#AED6F1", line=dict(color="#2874A6"))
                    manija(xs+ancho_col/2, yp+hu/2, "h")

            elif tipo == "Puerta":
                interior(xs, xe, yc, h_util, data.get("interior"))
                # Colores variados según posición para dar profundidad
                colf="rgba(169, 223, 191, 0.7)" if m==0 else ("rgba(249, 231, 159, 0.7)" if m==len(modulos)-1 else "rgba(215, 189, 226, 0.7)")
                dob=data.get("doble"); ap=data.get("apertura", "Lateral")
                
                fig.add_shape(type="rect", x0=xs+3, y0=yc+2, x1=xe-3, y1=yc+h_util-2, fillcolor=colf, line=dict(color="gray"))
                
                if dob: 
                    mid=xs+ancho_col/2; fig.add_shape(type="line", x0=mid, y0=yc+2, x1=mid, y1=yc+h_util-2, line=dict(color="gray", width=1))
                    manija(mid-15, yc+h_util/2); manija(mid+15, yc+h_util/2)
                else: 
                    if "Arriba" in ap: manija(xs+ancho_col/2, yc+30, "h")
                    elif "Abajo" in ap: manija(xs+ancho_col/2, yc+h_util-30, "h")
                    else: manija(xe-20 if i%2==0 else xs+20, yc+h_util/2)

            elif tipo == "Estantes": 
                interior(xs, xe, yc, h_util, {"tipo":"Estantes","cant":data.get("cant",0)})
            elif tipo == "Barral": 
                yb = yc + (h_util*0.2) if h_util<500 else yc + 100
                fig.add_shape(type="line", x0=xs+10, y0=yb, x1=xe-10, y1=yb, line=dict(color="gray", width=5))
                fig.add_annotation(x=xs+ancho_col/2, y=yb-30, text="👕", showarrow=False)

            # Avanzar cursor Y
            yc += h_mod

    # Frente Corredizo Overlay
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
    # MOTOR DE CÁLCULO (DESPIECE MULTI-MODULO)
    # ------------------------------------------------------------------------------
    st.header("📋 Resultados")
    procesar = st.button("🚀 PROCESAR DESPIECE Y PRESUPUESTO", type="primary", use_container_width=True)

    if procesar:
        pz = []; buy = []; err = []
        
        def add_p(nombre, cant, largo, ancho, veta, mat, nota=""):
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

        # ITERAR MODULOS DINÁMICAMENTE
        for i, modulos in enumerate(configuracion_columnas):
            for m, mod in enumerate(modulos):
                tipo = mod["tipo"]
                data = mod["data"]
                h_util = mod["h_util"]
                
                # Divisor Fijo (Techo del modulo actual, piso del siguiente)
                if m < len(modulos) - 1:
                    add_p(f"Estante Fijo (C{i+1} M{m+1})", 1, w_hueco, prof_int, "↔️", f"Mela {espesor}", "Estructural")

                if tipo == "Cajonera":
                    cant = data["cant"]
                    hf = (h_util - ((cant-1)*3)) / cant
                    add_p(f"Frente Cajón C{i+1}-M{m+1}", cant, w_hueco-4, hf, veta_frentes, f"Mela {espesor}")
                    
                    esp = hf - 30; hl = 180 if esp>=190 else (150 if esp>=160 else (100 if esp>=110 else 0))
                    if hl==0: err.append(f"C{i+1} M{m+1}: Frente muy bajo para cajón."); continue
                    
                    l_guia = min(550, max(250, int((prof_int - 15) // 50) * 50))
                    wc = w_hueco - (descuento_guia * 2) - 36
                    add_p("Lat. Cajón", cant*2, l_guia, hl, "↔️", "Blanca 18")
                    add_p("Contra-Frente", cant, wc, hl, "↔️", "Blanca 18")
                    add_p("Fondo Cajón", cant, l_guia, wc, "-", "Fibro 3")
                    buy.append({"Item": f"Guías {tipo_corredera} {l_guia}mm", "Cant": cant, "Unidad": "par", "Costo": c_guia})

                elif tipo == "Puerta":
                    ap = data.get("apertura", "Lateral"); mnt = data.get("montaje", "Externa")
                    dob = data.get("doble"); din = data.get("interior")
                    
                    dw = 4 if "Externa" in mnt else 6; dh = 4 if "Externa" in mnt else 6
                    hojas = 2 if dob else 1
                    wa = (w_hueco - dw - (2 if dob else 0))/hojas if dob else (w_hueco - dw)
                    ha = h_util - dh

                    add_p(f"Puerta {ap[:3]} C{i+1}-M{m+1}", hojas, ha, wa, veta_frentes, f"Mela {espesor}", mnt)
                    
                    if "Lateral" in ap:
                        bi = 2 if ha<900 else (3 if ha<1600 else (4 if ha<2100 else 5))
                        b_tipo = "Codo 18" if "Interna" in mnt else tipo_bisagra 
                        buy.append({"Item": f"Bisagras {b_tipo}", "Cant": bi*hojas, "Unidad": "u.", "Costo": c_bis})
                    elif "Rebatible" in ap:
                        buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": 2, "Unidad": "u.", "Costo": c_bis})
                        buy.append({"Item": "Pistón a Gas", "Cant": 1, "Unidad": "u.", "Costo": c_piston})

                    if din:
                        pint = prof_int - 20 if "Externa" in mnt else prof_int - 40 
                        if din["tipo"]=="Estantes": add_p(f"Estante Int. C{i+1}", din["cant"], w_hueco-2, pint, "↔️", f"Mela {espesor}")
                        elif din["tipo"]=="Cubos":
                            if din["cols"]>1: add_p("Div. Vert. Cubo", din["cols"]-1, ha-2, pint, "↕️", f"Mela {espesor}")
                            if din["rows"]>1: add_p("Estante Cubo", din["rows"]-1, w_hueco-2, pint, "↔️", f"Mela {espesor}")

                elif tipo == "Estantes":
                    add_p(f"Estante Móvil C{i+1}", data["cant"], w_hueco-2, prof_int-20, "↔️", f"Mela {espesor}")
                elif tipo == "Barral":
                    buy.append({"Item": "Barral", "Cant": 1, "Unidad": "u.", "Costo": 3000})

        if err:
            for e in err: st.error(e)
        else:
            buy.insert(0, {"Item": "Tornillos 4x50", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 10})
            
            t1, t2, t3 = st.tabs(["📝 Despiece", "🔩 Insumos", "💰 Costos"])
            with t1: 
                df = pd.DataFrame(pz)
                st.dataframe(df.style.format({"Largo": "{:.0f}", "Ancho": "{:.0f}"}), use_container_width=True, hide_index=True)
                st.download_button("📥 Exportar CSV para Corte", df.to_csv(index=False).encode(), "corte_v24.csv")
            with t2: 
                st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True, hide_index=True)
            with t3: 
                placas = math.ceil((sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in pz if "Mela" in p["Mat"]])/1e6*1.3)/4.75)
                c_mat = (placas * precio_placa)
                c_herr = sum([c["Costo"]*c["Cant"] for c in buy])
                st.write(f"- Melamina necesaria: ~{placas} placas (${c_mat:,.0f})")
                st.write(f"- Total Herrajes: ${c_herr:,.0f}")
                st.metric("PRECIO DE VENTA", f"${(c_mat + c_herr) * margen:,.0f}")
