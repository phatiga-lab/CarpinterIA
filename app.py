import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CarpinterIA: Visual", page_icon="📐", layout="wide")
st.title("📐 CarpinterIA: Diseñador Visual en Tiempo Real")

# --- FUNCION GRAFICA (EL MOTOR DE DIBUJO) ---
def dibujar_mueble(ancho, alto, prof, zocalo, cant_cajones, cant_puertas, cant_estantes, columnas):
    fig = go.Figure()

    # 1. Configurar el Lienzo (Canvas)
    fig.update_layout(
        title=f"Vista Frontal: {ancho}x{alto} mm",
        xaxis=dict(range=[-100, ancho+100], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-100, alto+100], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=500
    )

    # 2. Dibujar Zócalo (Base Oscura)
    if zocalo > 0:
        fig.add_shape(type="rect",
            x0=0, y0=0, x1=ancho, y1=zocalo,
            line=dict(color="black", width=2),
            fillcolor="#2c3e50", # Gris oscuro
        )
        fig.add_annotation(x=ancho/2, y=zocalo/2, text=f"Zócalo {zocalo}mm", showarrow=False, font=dict(color="white"))

    # 3. Dibujar Estructura Externa (Casco)
    alto_util = alto - zocalo
    fig.add_shape(type="rect",
        x0=0, y0=zocalo, x1=ancho, y1=alto,
        line=dict(color="#8B4513", width=4), # Marrón borde
        fillcolor="rgba(0,0,0,0)" # Transparente al centro
    )

    # 4. Dibujar Columnas (Divisores Verticales)
    ancho_columna = ancho / columnas
    for i in range(1, columnas):
        x_pos = ancho_columna * i
        fig.add_shape(type="line",
            x0=x_pos, y0=zocalo, x1=x_pos, y1=alto,
            line=dict(color="#8B4513", width=3, dash="dot")
        )

    # 5. Dibujar CAJONES (Asumimos que van en la primera columna o distribuidos)
    # Lógica Visual: Si hay cajones, los dibujamos apilados desde abajo (sobre el zócalo)
    if cant_cajones > 0:
        # Definimos dónde van los cajones. Para simplificar visualmente:
        # Si hay columnas, ponemos los cajones en la Columna 1.
        ancho_cajon = ancho_columna
        alto_frente = 180 # Estimado visual
        
        # Limitamos visualmente para que no se salgan del mueble
        cajones_visibles = min(cant_cajones, int(alto_util / alto_frente))
        
        for i in range(cajones_visibles):
            y_base = zocalo + (i * alto_frente)
            fig.add_shape(type="rect",
                x0=5, y0=y_base + 2, x1=ancho_cajon - 5, y1=y_base + alto_frente - 2,
                line=dict(color="#2980b9", width=2),
                fillcolor="#d6eaf8" # Azul clarito
            )
            fig.add_annotation(x=ancho_cajon/2, y=y_base + (alto_frente/2), text="Cajón", showarrow=False, font=dict(size=10, color="#2980b9"))

    # 6. Dibujar PUERTAS
    # Las puertas ocupan el resto del espacio o otras columnas
    if cant_puertas > 0:
        # Si hay cajones en col 1, las puertas van en col 2? 
        # Lógica visual simple: Si hay cajones, las puertas van AL LADO (si hay columnas) o ARRIBA.
        
        start_x = 0
        width_p = ancho
        
        if columnas > 1 and cant_cajones > 0:
            start_x = ancho_columna # Empiezan después de la col de cajones
            width_p = ancho - ancho_columna
        
        # Dibujamos las puertas en el espacio restante
        ancho_individual = width_p / cant_puertas
        
        for p in range(cant_puertas):
            x_p = start_x + (p * ancho_individual)
            fig.add_shape(type="rect",
                x0=x_p + 5, y0=zocalo + 5, x1=x_p + ancho_individual - 5, y1=alto - 5,
                line=dict(color="#27ae60", width=2), # Verde
                fillcolor="rgba(46, 204, 113, 0.2)" # Verde transparente
            )
            # Manija
            fig.add_shape(type="circle",
                x0=x_p + ancho_individual - 30, y0=zocalo + (alto_util/2), 
                x1=x_p + ancho_individual - 20, y1=zocalo + (alto_util/2) + 10,
                fillcolor="black"
            )
            fig.add_annotation(x=x_p + (ancho_individual/2), y=zocalo + (alto_util/2), text="Puerta", showarrow=False, font=dict(color="#27ae60"))

    # 7. Cotas (Medidas)
    fig.add_annotation(x=ancho/2, y=alto + 40, text=f"{ancho} mm", showarrow=False, font=dict(size=14, color="black"))
    fig.add_annotation(x=-40, y=alto/2, text=f"{alto} mm", showarrow=False, textangle=-90, font=dict(size=14, color="black"))

    return fig

# --- INTERFAZ DE USUARIO ---

col_inputs, col_grafico = st.columns([1, 1.5])

with col_inputs:
    st.header("1. Medidas")
    ancho = st.number_input("Ancho (mm)", 400, 3000, 1200, step=50)
    alto = st.number_input("Alto (mm)", 400, 2600, 1800, step=50)
    prof = st.number_input("Profundidad (mm)", 300, 900, 550, step=50)
    zocalo = st.number_input("Zócalo (mm)", 0, 150, 70)
    
    st.divider()
    st.header("2. Distribución")
    columnas = st.slider("Columnas Verticales", 1, 4, 2)
    st.caption("Divide el mueble en secciones verticales.")
    
    c1, c2 = st.columns(2)
    with c1:
        cant_cajones = st.number_input("Cajones", 0, 10, 4)
    with c2:
        cant_puertas = st.number_input("Puertas", 0, 4, 1)

with col_grafico:
    st.write("### 👁️ Vista Previa (Plano)")
    # Llamamos a la función de dibujo EN TIEMPO REAL
    # Cada vez que tocas un input a la izquierda, esto se redibuja solo.
    figura = dibujar_mueble(ancho, alto, prof, zocalo, cant_cajones, cant_puertas, 0, columnas)
    st.plotly_chart(figura, use_container_width=True)
    st.info("💡 El gráfico es esquemático. Los cajones se muestran en la primera columna por defecto.")

# --- SECCIÓN DE CÁLCULO (ABAJO) ---
st.markdown("---")
if st.button("🚀 CALCULAR MATERIALES Y COSTOS (Basado en este diseño)", type="primary"):
    st.write("### 📋 Resultados Técnicos")
    
    # Cálculos rápidos para confirmar que funciona
    area_mela = ((ancho*alto*2) + (ancho*prof*2)) / 1000000 # Estimación burda para test
    placas = 1 if area_mela < 4 else 2
    
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.success(f"**Diseño:** {ancho}x{alto}x{prof} mm")
        st.info(f"**Estructura:** {columnas} cuerpos")
    with c_res2:
        st.warning(f"**Herrajes:** {cant_cajones} pares de guías, {cant_puertas * 3} bisagras.")
        st.error(f"**Material:** Aprox {placas} placa(s) de melamina.")
        
    st.table(pd.DataFrame([
        {"Pieza": "Lateral", "Medida": f"{alto} x {prof}", "Cant": 2},
        {"Pieza": "Techo/Piso", "Medida": f"{ancho-(18*2)} x {prof}", "Cant": 2},
        {"Pieza": "Frentes Cajón", "Medida": "Según hueco", "Cant": cant_cajones},
    ]))
