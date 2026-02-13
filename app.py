import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

st.set_page_config(page_title="CarpinterIA: V21 Full", page_icon="🪚", layout="wide")

# ==============================================================================
# 1. BARRA LATERAL
# ==============================================================================
with st.sidebar:
    st.title("🪚 CarpinterIA V21")
    st.markdown("### ⚙️ Configuración")
    
    # Materiales
    st.write("**1. Tableros**")
    espesor = st.selectbox("Espesor Melamina", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70, step=5)
    veta_frentes = st.radio("Veta Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    st.divider()
    
    # Herrajes
    st.write("**2. Herrajes Estándar**")
    tipo_corredera = st.selectbox("Correderas Cajón", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
    es_push = "Push" in tipo_corredera
    
    if "Telescópicas" in tipo_corredera or "Push" in tipo_corredera:
        descuento_guia = 26 
        costo_guia_ref = 6500
    else:
        descuento_guia = 25 
        costo_guia_ref = 2500

    tipo_bisagra = st.selectbox("Bisagras Lateral", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)", "Push"])
    
    st.divider()
    
    # Costos
    with st.expander("💲 Lista de Precios"):
        precio_placa = st.number_input("Placa Melamina ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Placa Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input("Metro Canto ($)", value=800, step=50)
        st.caption("Herrajes Unitarios:")
        c_bis = st.number_input("Bisagra ($)", value=2500, step=100)
        c_guia = st.number_input("Par Guías ($)", value=costo_guia_ref, step=500)
        c_piston = st.number_input("Pistón a Gas ($)", value=4500, step=500)
        c_kit = st.number_input("Kit Placard (x Metro) ($)", value=15000, step=1000)
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

# Helper de límites
def get_limit(h):
    if h <= 0: return 1
    return max(1, int(h / 75))

with contenedor_controles:
    col_medidas, col_distribucion = st.columns([1, 2])
    
    # --- Medidas Generales ---
    with col_medidas:
        st.subheader("1. Casco General")
        ancho = st.number_input("Ancho Total (mm)", value=1600, step=10)
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
                modo_col = st.radio(f"Estructura C{i+1}", ["Dividida", "Entera"], horizontal=True, label_visibility="collapsed", key=f"m_{i}")
                
                detalles_inf = {}
                detalles_sup = {}
                tipo_inf = "Vacío"
                tipo_sup = "Vacío"

                # === HELPERS DE UI ===
                def ui_interior(s):
                    with st.expander("Interior (Opcional)"):
                        t = st.selectbox("Tipo", ["Vacío", "Estantes", "Cubos"], key=f"t_{s}")
                        d = {}
                        if t=="Estantes": d={"tipo":"Estantes","cant":st.number_input("Cant.",1,10,3,key=f"e_{s}")}
                        elif t=="Cubos":
                            c1,c2=st.columns(2)
                            d={"tipo":"Cubos","cols":c1.number_input("Cols",1,5,2,key=f"cc_{s}"),"rows":c2.number_input("Filas",1,10,3,key=f"cr_{s}")}
                        return d

                def ui_puerta_detalles(s, label):
                    st.markdown(f"**Configuración {label}**")
                    c1, c2 = st.columns(2)
                    apertura = c1.selectbox("Apertura", ["Lateral (Bisagra)", "Rebatible Arriba (Pistón)", "Rebatible Abajo (Pistón)"], key=f"ap_{s}")
                    montaje = c2.selectbox("Montaje", ["Externa (Sobrepuesta)", "Interna (Dentro del marco)"], key=f"mnt_{s}")
                    
                    # Si es lateral, preguntar doble. Si es rebatible, suele ser 1 hoja ancha.
                    doble = False
                    if "Lateral" in apertura:
                        doble = st.checkbox("Doble Hoja", False, key=f"d_{s}")
                    
                    return {"apertura": apertura, "montaje": montaje, "doble": doble, "interior": ui_interior(s)}

                # === MODO ENTERO ===
                if "Entera" in modo_col:
                    tipo_inf = st.selectbox("Componente Único", ["Vacío", "Cajonera", "Puerta Entera", "Frente Placard (Kit)", "Estantes", "Barral"], key=f"ent_{i}")
                    h_util = alto - zocalo
                    
                    if tipo_inf == "Cajonera":
                        max_c = get_limit(h_util)
                        cant = st.number_input("Cant.", 1, max_c, min(6, max_c), key=f"qe_{i}")
                        detalles_inf = {"alto": h_util, "cant": cant}
                    
                    elif tipo_inf == "Puerta Entera":
                        detalles_inf = ui_puerta_detalles(f"ent_{i}", "Puerta")
                        detalles_inf["alto"] = h_util
                        
                    elif tipo_inf == "Frente Placard (Kit)":
                        hojas = st.number_input("Cant. Hojas Corredizas", 2, 4, 2, key=f"kit_{i}")
                        if prof < 600:
                            st.error("⚠️ Profundidad < 600mm. Las perchas chocarán con las puertas corredizas.")
                        detalles_inf = {"alto": h_util, "hojas": hojas, "tipo_apertura": "Corrediza"}
                        
                    elif tipo_inf == "Estantes": 
                        detalles_sup={"cant":st.number_input("Cant.",1,15,5,key=f"es_{i}")}
                        tipo_sup="Estantes"; tipo_inf="Vacío"
                    elif tipo_inf == "Barral": 
                        tipo_sup="Barral"; tipo_inf="Vacío"

                # === MODO DIVIDIDO ===
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("🔽 **Abajo**")
                        tipo_inf = st.selectbox("Tipo", ["Vacío", "Cajonera", "Puerta Baja"], key=f"inf_{i}")
                        h_mod = st.number_input("Alto (mm)", value=720, step=10, key=f"h_{i}")
                        
                        if tipo_inf == "Cajonera":
                            max_c = get_limit(h_mod)
                            cant = st.number_input("Cant.", 1, max_c, min(3, max_c), key=f"qi_{i}")
                            detalles_inf = {"alto": h_mod, "cant": cant}
                        elif tipo_inf == "Puerta Baja":
                            detalles_inf = ui_puerta_detalles(f"inf_{i}", "Puerta Baja")
                            detalles_inf["alto"] = h_mod
                        else:
                            detalles_inf = {"alto": h_mod}

                    with c2:
                        st.markdown("🔼 **Arriba**")
                        h_rest = alto - zocalo - h_mod
                        st.caption(f"Libre: {h_rest}mm")
                        
                        if h_rest > 70:
                            tipo_sup = st.selectbox("Tipo", ["Vacío", "Estantes", "Barral", "Puerta Alta", "Cajonera"], key=f"sup_{i}")
                            
                            if tipo_sup == "Cajonera":
                                max_c = get_limit(h_rest)
                                cant = st.number_input("Cant.", 1, max_c, min(2, max_c), key=f"qs_{i}")
                                detalles_sup = {"cant": cant}
                            elif tipo_sup == "Estantes":
                                cant = st.number_input("Cant.", 1, 10, 3, key=f"qe_{i}")
                                detalles_sup = {"cant": cant}
                            elif tipo_sup == "Puerta Alta":
                                detalles_sup = ui_puerta_detalles(f"sup_{i}", "Puerta Alta")
                        else:
                            st.error("Sin espacio")
                            tipo_sup = "Vacío"

                configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup, "modo": modo_col})

# ==============================================================================
# 4. GRÁFICO COMPACTO
# ==============================================================================
def dibujar_mueble(ancho, alto, zocalo, columnas, configs, espesor_mat, es_push):
    # REDUCIDO A 350px DE ALTO
    fig = go.Figure()
    fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=350, xaxis=dict(visible=False, range=[-50, ancho+50]), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]), plot_bgcolor="white", title=f"Vista {ancho}x{alto}mm")

    # Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2C3E50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4))
    ancho_col = ancho / columnas
    
    def manija(cx, cy, orientacion="v"):
        if not es_push: 
            if orientacion=="v": fig.add_shape(type="line", x0=cx, y0=cy-15, x1=cx, y1=cy+15, line=dict(color="#154360", width=4))
            else: fig.add_shape(type="line", x0=cx-15, y0=cy, x1=cx+15, y1=cy, line=dict(color="#154360", width=4))

    def interior(x0, x1, y0, h, d):
        if not d: return
        t=d.get("tipo")
        if t=="Estantes":
            c=d["cant"]; p=h/(c+1)
            for k in range(c): y=y0+(p*(k+1)); fig.add_shape(type="line", x0=x0+5, y0=y, x1=x1-5, y1=y, line=dict(color="#A04000", width=2, dash="dot"))
        elif t=="Cubos":
            cols=d["cols"]; rows=d["rows"]
            ph=h/rows; pw=(x1-x0)/cols
            for r in range(1,rows): y=y0+(ph*r); fig.add_shape(type="line", x0=x0+5, y0=y, x1=x1-5, y1=y, line=dict(color="#A04000", width=2, dash="dot"))
            for c in range(1,cols): x=x0+(pw*c); fig.add_shape(type="line", x0=x, y0=y0+5, x1=x, y1=y0+h-5, line=dict(color="#A04000", width=2, dash="dot"))

    for i, conf in enumerate(configs):
        xs = i * ancho_col; xe = (i + 1) * ancho_col; yc = zocalo 
        if i < columnas: fig.add_shape(type="line", x0=xe, y0=zocalo, x1=xe, y1=alto, line=dict(color="#5D4037", width=2))

        if "Dividida" in conf["modo"]:
            y_div = zocalo + conf["inf_data"]["alto"]
            fig.add_shape(type="rect", x0=xs, y0=y_div-espesor_mat, x1=xe, y1=y_div, fillcolor="#8B4513", line=dict(width=0))

        # --- DIBUJAR COMPONENTES ---
        def dibujar_bloque(tipo, data, y_start, h_bloque):
            if tipo == "Cajonera":
                c=data["cant"]
                if c > 0:
                    hu=h_bloque/c
                    for k in range(c): 
                        yp=y_start+(k*hu)
                        fig.add_shape(type="rect", x0=xs+3, y0=yp+2, x1=xe-3, y1=yp+hu-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                        manija(xs+ancho_col/2, yp+hu/2, "h")
            
            elif tipo == "Frente Placard (Kit)":
                hojas = data["hojas"]
                ancho_h = (xe - xs) / hojas
                for h in range(hojas):
                    x_h = xs + (h * ancho_h)
                    # Solape visual
                    fig.add_shape(type="rect", x0=x_h+2, y0=y_start+2, x1=x_h+ancho_h+10, y1=y_start+h_bloque-2, fillcolor="rgba(100,100,100,0.2)", line=dict(color="black"))
                    # Perfil manija
                    fig.add_shape(type="line", x0=x_h+5, y0=y_start+10, x1=x_h+5, y1=y_start+h_bloque-10, line=dict(color="gray", width=3))

            elif "Puerta" in tipo:
                interior(xs, xe, y_start, h_bloque, data.get("interior"))
                colf="rgba(171, 235, 198, 0.6)" if "Baja" in tipo else "rgba(210, 180, 222, 0.6)"
                dob=data.get("doble")
                ap=data.get("apertura", "Lateral")
                
                fig.add_shape(type="rect", x0=xs+3, y0=y_start+2, x1=xe-3, y1=y_start+h_bloque-2, fillcolor=colf, line=dict(color="gray"))
                
                if dob: 
                    mid=xs+ancho_col/2
                    fig.add_shape(type="line", x0=mid, y0=y_start+2, x1=mid, y1=y_start+h_bloque-2, line=dict(color="gray", width=1))
                    manija(mid-15, y_start+h_bloque/2); manija(mid+15, y_start+h_bloque/2)
                else: 
                    # Manija según apertura
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

        # INFERIOR
        h_inf = conf["inf_data"].get("alto", 0)
        h_util_inf = h_inf - espesor_mat if "Dividida" in conf["modo"] else h_inf
        dibujar_bloque(conf["inf_tipo"], conf["inf_data"], yc, h_util_inf)
        yc += h_inf

        # SUPERIOR
        rest = alto - yc
        if rest > 0:
            dibujar_bloque(conf["sup_tipo"], conf["sup_data"], yc, rest)

    return fig

with contenedor_grafico: st.plotly_chart(dibujar_mueble(ancho, alto, zocalo, cant_columnas, configuracion_columnas, espesor, es_push), use_container_width=True)

# ==============================================================================
# 5. CÁLCULO
# ==============================================================================
with contenedor_boton:
    if st.button("🚀 PROCESAR PROYECTO", type="primary", use_container_width=True):
        pz = []; buy = []; err = []
        
        # --- HELPERS DE CÁLCULO ---
        def get_cantos(pieza):
            # Asignación automática de cantos según tipo de pieza
            if "Frente" in pieza or "Puerta" in pieza: return "4L" # 4 Lados
            if "Lat. Caj" in pieza or "Contra" in pieza: return "1L" # Arriba
            if "Estante" in pieza or "Techo" in pieza or "Piso" in pieza or "Divisor" in pieza: return "1L" # Frente
            if "Lat. Externo" in pieza: return "1L" # Frente
            return "-"

        def add_p(nombre, cant, largo, ancho, veta, mat, nota=""):
            c = get_cantos(nombre)
            pz.append({"Pieza": nombre, "Cant": cant, "Largo": largo, "Ancho": ancho, "Veta": veta, "Mat": mat, "Cantos": c, "Nota": nota})

        # Estructura
        h_int = alto - zocalo - (espesor * 2); w_int = ancho - (espesor * 2)
        add_p("Lat. Externo", 2, alto, prof, "↕️", f"Mela {espesor}")
        add_p("Techo/Piso", 2, w_int, prof, "↔️", f"Mela {espesor}")
        add_p("Fondo", 1, alto-15, ancho-15, "-", f"Fibro {fondo_esp}")
        if cant_columnas > 1: add_p("Divisor Vert", cant_columnas-1, h_int, prof, "↕️", f"Mela {espesor}")

        w_hueco = (w_int - ((cant_columnas - 1) * espesor)) / cant_columnas
        if w_hueco < 150: st.error(f"Hueco de {w_hueco:.0f}mm muy angosto."); st.stop()

        for i, conf in enumerate(configuracion_columnas):
            
            if "Dividida" in conf["modo"]:
                add_p(f"Estante Fijo (Div C{i+1})", 1, w_hueco, prof, "↔️", f"Mela {espesor}", "Estructural")

            # --- CAJONES ---
            def do_cajon(pos, cant, h_tot, is_sup):
                h_disp = h_tot
                if "Dividida" in conf["modo"] and not is_sup: h_disp -= espesor
                
                hf = (h_disp - ((cant-1)*3)) / cant
                if hf < 70: err.append(f"C{i+1}: Cajón muy bajo."); return

                add_p(f"Frente {pos}", cant, w_hueco-4, hf, veta_frentes, f"Mela {espesor}")
                
                espacio = hf - 30; hl = 0
                for size in [180, 150, 100]:
                    if espacio >= (size + 10): hl = size; break
                if hl==0: err.append(f"C{i+1}: No entra lateral."); return
                
                wc = w_hueco - (descuento_guia * 2) - 36
                add_p("Lat. Cajón", cant*2, 500, hl, "↔️", "Blanca 18")
                add_p("Contra-Frente", cant, wc, hl, "↔️", "Blanca 18")
                add_p("Fondo Cajón", cant, 500, wc, "-", "Fibro 3")
                buy.append({"Item": f"Guías {tipo_corredera} 500mm", "Cant": cant, "Unidad": "par", "Costo": c_guia})

            # --- PUERTAS (Con Apertura y Montaje) ---
            def do_puerta(nom, h, data):
                ap = data.get("apertura", "Lateral")
                montaje = data.get("montaje", "Externa")
                dob = data.get("doble")
                din = data.get("interior")
                
                # Ajuste de altura por estante fijo
                h_real = h - espesor if ("Dividida" in conf["modo"] and "Baja" in nom) else h
                
                # Ajuste por Montaje (Interna vs Externa)
                # Externa: W = Hueco - 4 (luz). H = Hueco - 4.
                # Interna: W = Hueco - (2*Gap). Gap ~3mm -> Hueco - 6.
                descuento_w = 4 if "Externa" in montaje else 6
                descuento_h = 4 if "Externa" in montaje else 6

                hojas = 2 if dob else 1
                wa = (w_hueco - descuento_w - (2 if dob else 0))/hojas if dob else (w_hueco - descuento_w)
                ha = h_real - descuento_h

                add_p(f"{nom} ({ap[:3]})", hojas, ha, wa, veta_frentes, f"Mela {espesor}", f"{montaje}")
                
                # Herrajes según apertura
                if "Lateral" in ap:
                    bi = 2 if ha<900 else (3 if ha<1600 else (4 if ha<2100 else 5))
                    b_tipo = "Codo 18" if "Interna" in montaje else tipo_bisagra # Forzar Codo 18 si es interna
                    buy.append({"Item": f"Bisagras {b_tipo}", "Cant": bi*hojas, "Unidad": "u.", "Costo": c_bis})
                elif "Rebatible" in ap:
                    bi = 2 # Generalmente 2 bisagras superiores
                    buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": bi, "Unidad": "u.", "Costo": c_bis})
                    # Pistones
                    buy.append({"Item": "Pistón a Gas (Elev/Desc)", "Cant": 1, "Unidad": "u.", "Costo": c_piston})

                # Interior
                if din:
                    pint = prof - 20 if "Externa" in montaje else prof - 40 # Mas profundo si es interna
                    if din["tipo"]=="Estantes":
                        add_p("Estante Int.", din["cant"], w_hueco-2, pint, "↔️", f"Mela {espesor}")
                    elif din["tipo"]=="Cubos":
                        c=din["cols"]; r=din["rows"]
                        if c>1: add_p("Div. Vert. Cubo", c-1, ha-2, pint, "↕️", f"Mela {espesor}")
                        if r>1: add_p("Estante Cubo", r-1, w_hueco-2, pint, "↔️", f"Mela {espesor}")

            # --- CORREDIZAS (KIT) ---
            def do_kit(h, hojas):
                # Ancho hoja = (Ancho total hueco + (Cruces * Solape)) / Cant Hojas
                # Solape estandar kit ~ 30mm
                cruces = hojas - 1
                solape = 30
                wa = (w_hueco + (cruces * solape)) / hojas
                add_p("Hoja Corrediza", hojas, h-40, wa, veta_frentes, f"Mela {espesor}", "Kit Placard") 
                # h-40 es aprox para rieles
                buy.append({"Item": "Kit Corredizo (Riel+Ruedas)", "Cant": w_hueco/1000, "Unidad": "ml", "Costo": c_kit})

            # EJECUCIÓN
            d_inf = conf["inf_data"]; d_sup = conf["sup_data"]
            
            # Inferior / Entero
            if conf["inf_tipo"] == "Cajonera": do_cajon("Inf", d_inf["cant"], d_inf["alto"], False)
            elif "Puerta" in conf["inf_tipo"]: 
                h = d_inf["alto"] if "Baja" in conf["inf_tipo"] else (alto-zocalo)
                do_puerta(conf["inf_tipo"], h, d_inf)
            elif conf["inf_tipo"] == "Frente Placard (Kit)":
                do_kit(alto-zocalo, d_inf["hojas"])
            
            # Superior
            if "Dividida" in conf["modo"]:
                h_inf = d_inf.get("alto", 0); h_rest = alto - zocalo - h_inf 
                if conf["sup_tipo"] == "Cajonera": do_cajon("Sup", d_sup["cant"], h_rest, True)
                elif conf["sup_tipo"] == "Puerta Alta": do_puerta("Puerta Alta", h_rest, d_sup)
                elif conf["sup_tipo"] == "Estantes": add_p("Estante Móvil", d_sup["cant"], w_hueco-2, prof-20, "↔️", f"Mela {espesor}")
                elif conf["sup_tipo"] == "Barral": buy.append({"Item": "Barral", "Cant": 1, "Unidad": "u.", "Costo": 3000})

        if err:
            for e in err: st.error(e)
        else:
            buy.insert(0, {"Item": "Tornillos 4x50", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 10})
            
            t1,t2,t3=st.tabs(["Corte & Cantos","Herrajes","$$$"])
            with t1: 
                df = pd.DataFrame(pz)
                st.dataframe(df, use_container_width=True)
                st.download_button("📥 Bajar CSV", df.to_csv(index=False).encode(), "corte_v21.csv")
            with t2: st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True)
            with t3: 
                cost = (math.ceil(sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in pz if "Mela" in p["Mat"]])/1e6*1.3/4.75)*precio_placa) + sum([c["Costo"]*c["Cant"] for c in buy])
                st.metric("Total", f"${cost*margen:,.0f}")
