import streamlit as st
import google.generativeai as genai

st.title("🛠️ Diagnóstico de Conexión CarpinterIA")

# Configuración
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.success("✅ API Key detectada en Secrets")
except Exception as e:
    st.error(f"❌ Error configurando API Key: {e}")

if st.button("🔍 Ver Modelos Disponibles para mi Clave"):
    try:
        st.info("Consultando a los servidores de Google...")
        
        # Esta función pide la lista oficial a Google
        modelos = genai.list_models()
        
        encontrados = []
        for m in modelos:
            # Filtramos solo los que sirven para generar texto/imagen
            if 'generateContent' in m.supported_generation_methods:
                st.code(f"Modelo válido: {m.name}")
                encontrados.append(m.name)
        
        if not encontrados:
            st.warning("⚠️ La conexión funciona, pero tu clave no tiene modelos asignados (posible restricción regional).")
        else:
            st.success(f"¡Conexión exitosa! Se encontraron {len(encontrados)} modelos.")

    except Exception as e:
        st.error(f"❌ Error fatal de conexión: {e}")
