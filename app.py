import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

st.set_page_config(page_title="CarpinterIA: V20 Physics Locked", page_icon="🪚", layout="wide")

# ==============================================================================
# 1. BARRA LATERAL
# ==============================================================================
with st.sidebar:
    st.title("🪚 CarpinterIA V20")
    st.markdown("### ⚙️ Configuración")
    
    # Materiales
    st.write("**1. Tableros**")
    espesor = st.selectbox("Espesor Melamina", [18, 15], index=0)
    fondo_esp = st.selectbox("Espesor Fondo", [3, 5.5, 18], index=0)
    zocalo = st.number_input("Altura Zócalo (mm)", value=70, step=5)
    veta_frentes = st.radio("Veta Frentes", ["↔️ Horizontal", "↕️ Vertical"], index=0)

    st.divider()
    
    # Herrajes
    st.write("**2. Herrajes**")
    tipo_corredera = st.selectbox("Correderas", ["Telescópicas", "Comunes (Z)", "Push / Tip-On"])
    es_push = "Push" in tipo_corredera
    
    if "Telescópicas" in tipo_corredera or "Push" in tipo_corredera:
        descuento_guia = 26 
        costo_guia_ref = 6500
    else:
        descuento_guia = 25 
        costo_guia_ref = 2500

    tipo_bisagra = st.selectbox("Bisagras", ["Codo 0 (Ext)", "Codo 9 (Media)", "Codo 18 (Int)", "Push"])
    
    st.divider()
    
    # Costos
    with st.expander("💲 Precios (Opcional)"):
        precio_placa = st.number_input("Precio Placa ($)", value=85000, step=1000)
        precio_fondo = st.number_input("Precio Fondo ($)", value=25000, step=1000)
        precio_canto = st.number_input("Precio Canto ($)", value=800, step=50)
        costo_bisagra = st.number_input("Costo Bisagra ($)", value=2500, step=100)
        costo_guia = st.number_input("Costo Guías ($)", value=costo_guia_ref, step=500)
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
# 3. CONTROLES DE DISEÑO (CON LÓGICA LIMITANTE)
# ==============================================================================
configuracion_columnas = []

# Función auxiliar para calcular límite de cajones
def calcular_limite_cajones(altura_disponible_mm):
    # Asumimos mínimo 70mm frente + 5mm luz = 75mm
    if altura_disponible_mm <= 0: return 1
    maximo = int(altura_disponible_mm / 75)
    return max(1, maximo) # Siempre devolver al menos 1 para no romper el slider

with contenedor_controles:
    col_medidas, col_distribucion = st.columns([1, 2])
    
    # --- Medidas Generales ---
    with col_medidas:
        st.subheader("1. Casco General")
        ancho = st.number_input("Ancho Total (mm)", value=1200, step=10)
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
                modo_col = st.radio(f"Estructura C{i+1}", 
                                   ["Dividida (Estante Fijo al medio)", "Entera (Sin división fija)"], 
                                   horizontal=True, label_visibility="collapsed", key=f"mode_{i}")
                
                detalles_inf = {}
                detalles_sup = {}
                tipo_inf = "Vacío"
                tipo_sup = "Vacío"

                # Helper Interior
                def config_int(s):
                    st.caption("Interior")
                    t = st.selectbox("Tipo", ["Vacío", "Estantes", "Cubos"], key=f"t_{s}")
                    d = {}
                    if t=="Estantes": d={"tipo":"Estantes","cant":st.number_input("Cant.",1,10,3,key=f"e_{s}")}
                    elif t=="Cubos":
                        c1,c2=st.columns(2)
                        d={"tipo":"Cubos","cols":c1.number_input("Cols",1,5,2,key=f"cc_{s}"),"rows":c2.number_input("Filas",1,10,3,key=f"cr_{s}")}
                    return d

                # MODO ENTERO
                if "Entera" in modo_col:
                    tipo_inf = st.selectbox("Componente Único", ["Vacío", "Cajonera", "Puerta Entera", "Estantes", "Barral"], key=f"ent_{i}")
                    h_util = alto - zocalo
                    
                    if tipo_inf == "Cajonera":
                        # LÍMITE FÍSICO APLICADO
                        max_c = calcular_limite_cajones(h_util)
                        cant_caj = st.number_input("Cant. Cajones", min_value=1, max_value=max_c, value=min(6, max_c), step=1, key=f"qty_ent_{i}", help=f"Máximo físico: {max_c}")
                        detalles_inf = {"alto": h_util, "cant": cant_caj}
                    
                    elif tipo_inf == "Puerta Entera":
                        doble = st.checkbox("Doble", False, key=f"d_ent_{i}")
                        detalles_inf = {"alto": h_util, "doble": doble, "interior": config_int(f"ei_{i}")}
                    elif tipo_inf == "Estantes": 
                        detalles_sup={"cant":st.number_input("Cant.",1,15,5,key=f"es_ent_{i}")}
                        tipo_sup="Estantes"; tipo_inf="Vacío"
                    elif tipo_inf == "Barral": 
                        tipo_sup="Barral"; tipo_inf="Vacío"

                # MODO DIVIDIDO
                else:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("🔽 **Abajo**")
                        tipo_inf = st.selectbox("Tipo", ["Vacío", "Cajonera", "Puerta Baja"], key=f"inf_{i}")
                        h_mod = st.number_input("Alto Corte (mm)", value=720, step=10, key=f"h_inf_{i}")
                        
                        if tipo_inf == "Cajonera":
                            # LÍMITE FÍSICO APLICADO
                            max_c = calcular_limite_cajones(h_mod)
                            cant_caj = st.number_input("Cant.", min_value=1, max_value=max_c, value=min(3, max_c), step=1, key=f"q_inf_{i}", help=f"Máximo físico: {max_c}")
                            detalles_inf = {"alto": h_mod, "cant": cant_caj}
                        
                        elif tipo_inf == "Puerta Baja":
                            doble = st.checkbox("Doble", False, key=f"d_inf_{i}")
                            detalles_inf = {"alto": h_mod, "doble": doble, "interior": config_int(f"ii_{i}")}
                        else:
                            detalles_inf = {"alto": h_mod}

                    with c2:
                        st.markdown("🔼 **Arriba**")
                        h_rest = alto - zocalo - h_mod
                        st.caption(f"Libre: {h_rest}mm")
                        
                        if h_rest > 70: # Solo si hay espacio mínimo
                            tipo_sup = st.selectbox("Tipo", ["Vacío", "Estantes", "Barral", "Puerta Alta", "Cajonera"], key=f"sup_{i}")
                            
                            if tipo_sup == "Cajonera":
                                # LÍMITE FÍSICO APLICADO
                                max_c = calcular_limite_cajones(h_rest)
                                cant = st.number_input("Cant.", min_value=1, max_value=max_c, value=min(2, max_c), step=1, key=f"qc_sup_{i}", help=f"Máximo físico: {max_c}")
                                detalles_sup = {"cant": cant}
                            
                            elif tipo_sup == "Estantes":
                                cant = st.number_input("Cant.", 1, 10, 3, key=f"qs_sup_{i}")
                                detalles_sup = {"cant": cant}
                            elif tipo_sup == "Puerta Alta":
                                doble = st.checkbox("Doble", False, key=f"ds_sup_{i}")
                                detalles_sup = {"doble": doble, "interior": config_int(f"is_{i}")}
                        else:
                            st.error("Sin espacio útil")
                            tipo_sup = "Vacío"

                configuracion_columnas.append({"inf_tipo": tipo_inf, "inf_data": detalles_inf, "sup_tipo": tipo_sup, "sup_data": detalles_sup, "modo": modo_col})

# ==============================================================================
# 4. GRÁFICO
# ==============================================================================
def dibujar_mueble(ancho, alto, zocalo, columnas, configs, espesor_mat, es_push):
    fig = go.Figure()
    fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=450, xaxis=dict(visible=False, range=[-50, ancho+50]), yaxis=dict(visible=False, scaleanchor="x", scaleratio=1, range=[-50, alto+50]), plot_bgcolor="white", title=f"Vista {ancho}x{alto}mm")

    # Estructura
    fig.add_shape(type="rect", x0=0, y0=0, x1=ancho, y1=zocalo, fillcolor="#2C3E50", line=dict(color="black"))
    fig.add_shape(type="rect", x0=0, y0=zocalo, x1=ancho, y1=alto, line=dict(color="#5D4037", width=4))
    ancho_col = ancho / columnas
    
    def manija(cx, cy):
        if not es_push: fig.add_shape(type="line", x0=cx, y0=cy-15, x1=cx, y1=cy+15, line=dict(color="#154360", width=4))

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
            h_div = conf["inf_data"]["alto"]
            y_div = zocalo + h_div
            fig.add_shape(type="rect", x0=xs, y0=y_div-espesor_mat, x1=xe, y1=y_div, fillcolor="#8B4513", line=dict(width=0))

        # INFERIOR
        t=conf["inf_tipo"]; d=conf["inf_data"]
        h_inf_total = d.get("alto", 0)
        h_util_inf = h_inf_total - espesor_mat if "Dividida" in conf["modo"] else h_inf_total

        if t=="Cajonera":
            c=d["cant"]
            if c > 0: # Prevención division zero
                hu=h_util_inf/c
                for k in range(c): 
                    yp=yc+(k*hu)
                    fig.add_shape(type="rect", x0=xs+3, y0=yp+2, x1=xe-3, y1=yp+hu-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                    manija(xs+ancho_col/2, yp+hu/2)
            
        elif "Puerta" in t:
            interior(xs, xe, yc, h_util_inf, d.get("interior"))
            colf="rgba(171, 235, 198, 0.6)" if "Baja" in t else "rgba(210, 180, 222, 0.6)"; coll="#196F3D" if "Baja" in t else "#6C3483"
            dob=d.get("doble")
            fig.add_shape(type="rect", x0=xs+3, y0=yc+2, x1=xe-3, y1=yc+h_util_inf-2, fillcolor=colf, line=dict(color=coll))
            if dob: mid=xs+ancho_col/2; fig.add_shape(type="line", x0=mid, y0=yc+2, x1=mid, y1=yc+h_util_inf-2, line=dict(color=coll, width=1)); manija(mid-15, yc+h_util_inf/2); manija(mid+15, yc+h_util_inf/2)
            else: px=xe-20 if i%2==0 else xs+20; manija(px, yc+h_util_inf/2)

        yc += h_inf_total

        # SUPERIOR
        rest=alto-yc
        if rest>0:
            ts=conf["sup_tipo"]; ds=conf["sup_data"]
            if ts=="Estantes": interior(xs, xe, yc, rest, {"tipo":"Estantes","cant":ds["cant"]})
            elif ts=="Barral": yb=alto-100; fig.add_shape(type="line", x0=xs+10, y0=yb, x1=xe-10, y1=yb, line=dict(color="gray", width=5)); fig.add_annotation(x=xs+ancho_col/2, y=yb-30, text="👕", showarrow=False)
            elif ts=="Puerta Alta":
                interior(xs, xe, yc, rest, ds.get("interior")); dob=ds.get("doble")
                fig.add_shape(type="rect", x0=xs+3, y0=yc+2, x1=xe-3, y1=alto-2, fillcolor="rgba(249, 231, 159, 0.6)", line=dict(color="#D4AC0D"))
                if dob: mid=xs+ancho_col/2; fig.add_shape(type="line", x0=mid, y0=yc+2, x1=mid, y1=alto-2, line=dict(color="#D4AC0D", width=1)); manija(mid-15, yc+50); manija(mid+15, yc+50)
                else: px=xe-20 if i%2==0 else xs+20; manija(px, yc+50)
            elif ts=="Cajonera":
                c=ds["cant"]
                if c>0:
                    hu=rest/c
                    for k in range(c): 
                        yp=yc+(k*hu)
                        fig.add_shape(type="rect", x0=xs+3, y0=yp+2, x1=xe-3, y1=yp+hu-2, fillcolor="#85C1E9", line=dict(color="#2E86C1"))
                        manija(xs+ancho_col/2, yp+hu/2)

    return fig

with contenedor_grafico: st.plotly_chart(dibujar_mueble(ancho, alto, zocalo, cant_columnas, configuracion_columnas, espesor, es_push), use_container_width=True)

# ==============================================================================
# 5. CÁLCULO
# ==============================================================================
with contenedor_boton:
    if st.button("🚀 PROCESAR PROYECTO", type="primary", use_container_width=True):
        pz = []; buy = []; err = []
        
        # Estructura
        h_int = alto - zocalo - (espesor * 2); w_int = ancho - (espesor * 2)
        pz.append({"Pieza": "Lat. Externo", "Cant": 2, "Largo": alto, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})
        pz.append({"Pieza": "Techo/Piso", "Cant": 2, "Largo": w_int, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}"})
        pz.append({"Pieza": "Fondo", "Cant": 1, "Largo": alto-15, "Ancho": ancho-15, "Veta": "---", "Mat": f"Fibro {fondo_esp}"})
        if cant_columnas > 1: pz.append({"Pieza": "Divisor Vert", "Cant": cant_columnas-1, "Largo": h_int, "Ancho": prof, "Veta": "↕️ Vert", "Mat": f"Melamina {espesor}"})

        w_hueco = (w_int - ((cant_columnas - 1) * espesor)) / cant_columnas
        if w_hueco < 150: st.error(f"Hueco de {w_hueco:.0f}mm es muy angosto para herrajes."); st.stop()

        for i, conf in enumerate(configuracion_columnas):
            
            # --- DIVISOR HORIZONTAL ---
            if "Dividida" in conf["modo"]:
                pz.append({"Pieza": f"Estante Fijo (Divisor C{i+1})", "Cant": 1, "Largo": w_hueco, "Ancho": prof, "Veta": "↔️ Horiz", "Mat": f"Melamina {espesor}", "Nota": "Estructural"})

            # --- CAJONES ---
            def do_cajon(pos, cant, h_tot, is_sup):
                h_disp = h_tot
                if "Dividida" in conf["modo"] and not is_sup: h_disp -= espesor
                
                hf = (h_disp - ((cant-1)*3)) / cant
                # Doble validacion (aunque el input ya limita)
                if hf < 70: err.append(f"C{i+1}: Cajón de {hf:.0f}mm muy bajo."); return

                pz.append({"Pieza": f"Frente {pos}", "Cant": cant, "Largo": w_hueco-4, "Ancho": hf, "Veta": veta_frentes, "Mat": f"Mela {espesor}"})
                
                # Caja
                espacio_caja = hf - 30 
                hl = 0
                for size in [180, 150, 100]:
                    if espacio_caja >= (size + 10): hl = size; break
                
                if hl==0: err.append(f"C{i+1}: Frente {hf:.0f}mm muy chico para lateral std."); return
                
                wc = w_hueco - (descuento_guia * 2) - 36
                pz.append({"Pieza": "Lat. Cajón", "Cant": cant*2, "Largo": 500, "Ancho": hl, "Veta": "↔️", "Mat": "Blanca 18"})
                pz.append({"Pieza": "Contra-Frente", "Cant": cant, "Largo": wc, "Ancho": hl, "Veta": "↔️", "Mat": "Blanca 18"})
                pz.append({"Pieza": "Fondo Cajón", "Cant": cant, "Largo": 500, "Ancho": wc, "Veta": "-", "Mat": "Fibro 3"})
                buy.append({"Item": f"Guías {tipo_corredera} 500mm", "Cant": cant, "Unidad": "par", "Costo": costo_guia})

            # --- PUERTAS ---
            def do_puerta(nom, h, dob, din):
                h_real = h - espesor if ("Dividida" in conf["modo"] and "Baja" in nom) else h
                hojas = 2 if dob else 1; wa = (w_hueco-6)/2 if dob else (w_hueco-4)
                pz.append({"Pieza": f"{nom}", "Cant": hojas, "Largo": h_real-4, "Ancho": wa, "Veta": veta_frentes, "Mat": f"Mela {espesor}"})
                bi = 2 if h_real<900 else (3 if h_real<1600 else (4 if h_real<2100 else 5))
                buy.append({"Item": f"Bisagras {tipo_bisagra}", "Cant": bi*hojas, "Unidad": "u.", "Costo": costo_bisagra})
                
                if din:
                    pint = prof - 20
                    if din["tipo"]=="Estantes":
                        pz.append({"Pieza": "Estante Int.", "Cant": din["cant"], "Largo": w_hueco-2, "Ancho": pint, "Veta": "↔️", "Mat": f"Mela {espesor}"})
                    elif din["tipo"]=="Cubos":
                        c=din["cols"]; r=din["rows"]
                        if c>1: pz.append({"Pieza": "Div. Vert. Cubo", "Cant": c-1, "Largo": h_real-2, "Ancho": pint, "Veta": "↕️", "Mat": f"Mela {espesor}"})
                        if r>1: pz.append({"Pieza": "Estante Cubo", "Cant": r-1, "Largo": w_hueco-2, "Ancho": pint, "Veta": "↔️", "Mat": f"Mela {espesor}"})

            # EJECUCIÓN
            d_inf = conf["inf_data"]; d_sup = conf["sup_data"]
            
            if conf["inf_tipo"] == "Cajonera": do_cajon("Inf", d_inf["cant"], d_inf["alto"], False)
            elif "Puerta" in conf["inf_tipo"]: 
                h = d_inf["alto"] if "Baja" in conf["inf_tipo"] else (alto-zocalo)
                do_puerta(conf["inf_tipo"], h, d_inf.get("doble"), d_inf.get("interior"))
            
            if "Dividida" in conf["modo"]:
                h_inf = d_inf.get("alto", 0); h_rest = alto - zocalo - h_inf 
                if conf["sup_tipo"] == "Cajonera": do_cajon("Sup", d_sup["cant"], h_rest, True)
                elif conf["sup_tipo"] == "Puerta Alta": do_puerta("Puerta Alta", h_rest, d_sup.get("doble"), d_sup.get("interior"))
                elif conf["sup_tipo"] == "Estantes": pz.append({"Pieza": "Estante Móvil", "Cant": d_sup["cant"], "Largo": w_hueco-2, "Ancho": prof-20, "Veta": "↔️", "Mat": f"Mela {espesor}"})
                elif conf["sup_tipo"] == "Barral": buy.append({"Item": "Barral", "Cant": 1, "Unidad": "u.", "Costo": 3000})

        if err:
            for e in err: st.error(e)
        else:
            buy.insert(0, {"Item": "Tornillos 4x50", "Cant": len(pz)*4, "Unidad": "u.", "Costo": 10})
            m_canto = sum([(p["Largo"]+p["Ancho"])*2*p["Cant"] for p in pz if "Mela" in p["Mat"]])/1000
            buy.append({"Item": "Tapacanto", "Cant": int(m_canto*1.2), "Unidad": "m", "Costo": precio_canto})
            
            t1,t2,t3=st.tabs(["Corte","Herrajes","$$$"])
            with t1: st.dataframe(pd.DataFrame(pz), use_container_width=True)
            with t2: st.dataframe(pd.DataFrame(buy).groupby(["Item","Unidad"], as_index=False).sum(), use_container_width=True)
            with t3: 
                cost = (math.ceil(sum([p["Largo"]*p["Ancho"]*p["Cant"] for p in pz if "Mela" in p["Mat"]])/1e6*1.3/4.75)*precio_placa) + sum([c["Costo"]*c["Cant"] for c in buy])
                st.metric("Total", f"${cost:,.0f}")
