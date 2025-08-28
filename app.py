import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Configuración de la página
st.set_page_config(page_title="Reportes SimpliRoute", page_icon="📊", layout="centered")

# Estilos (opcional)
st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Reportes SimpliRoute")

# --- NUEVO: Selector para el tipo de reporte ---
tipo_reporte = st.selectbox(
    "Selecciona el tipo de reporte que deseas generar",
    ("Visitas", "Rutas")
)

# Inputs de usuario
token = st.text_input("🔐 Token de autenticación")
correo = st.text_input("📧 Correo de usuario (para recibir el reporte)")

col1, col2 = st.columns(2)
with col1:
    inicio = st.date_input("📅 Fecha de inicio", value=datetime.today() - timedelta(days=7))
with col2:
    final = st.date_input("📅 Fecha final", value=datetime.today())

opcion = st.radio("📆 ¿Cómo quieres dividir el rango de fechas?", ("Semanal", "Quincenal", "Mensual"))

# Botón de ejecución
if st.button("🚀 Generar Reporte"):
    if not token or not correo:
        st.warning("⚠️ Debes ingresar el token y el correo.")
        st.stop()

    # Funciones para dividir rangos (sin cambios)
    def dividir_rango_por_dias(inicio, final, dias):
        rangos = []
        while inicio <= final:
            fin_intervalo = inicio + timedelta(days=dias - 1)
            if fin_intervalo > final:
                fin_intervalo = final
            rangos.append((inicio.strftime("%Y-%m-%d"), fin_intervalo.strftime("%Y-%m-%d")))
            inicio = fin_intervalo + timedelta(days=1)
        return rangos

    def dividir_rango_por_mes(inicio, final):
        rangos = []
        while inicio <= final:
            # Lógica para obtener el último día del mes actual
            siguiente_mes = inicio.replace(day=28) + timedelta(days=4)
            ultimo_dia_mes = siguiente_mes - timedelta(days=siguiente_mes.day)
            fin_mes = min(ultimo_dia_mes.date(), final)
            rangos.append((inicio.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")))
            inicio = fin_mes + timedelta(days=1)
        return rangos

    # Determinar rangos (sin cambios)
    if opcion == "Semanal":
        rangos = dividir_rango_por_dias(inicio, final, 7)
    elif opcion == "Quincenal":
        rangos = dividir_rango_por_dias(inicio, final, 15)
    elif opcion == "Mensual":
        rangos = dividir_rango_por_mes(inicio, final)

    # --- LÓGICA MODIFICADA: Definir URL y headers según la selección ---
    base_url = ""
    headers = {}

    if tipo_reporte == "Visitas":
        st.info("Preparando para generar reporte de **Visitas**...")
        base_url = "https://api.simpliroute.com/v1/reports/visits"
        headers = {
            "authorization": f"Token {token}",
            "origin": "https://app2.simpliroute.com",
            "referer": "https://app2.simpliroute.com/",
            "accept": "application/json",
            "user-agent": "Mozilla/5.0",
        }
    elif tipo_reporte == "Rutas":
        st.info("Preparando para generar reporte de **Rutas**...")
        base_url = "https://api-gateway.simpliroute.com/v1/reports/routes"
        headers = {
            "authorization": f"Token {token}",
            "origin": "https://app3.simpliroute.com", # Dato del curl
            "referer": "https://app3.simpliroute.com/", # Dato del curl
            "accept": "application/json",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }

    # Barra de progreso
    progress_bar = st.progress(0)
    total_rangos = len(rangos)
    
    # Bucle para ejecutar las solicitudes
    with st.spinner('Procesando solicitudes...'):
        for i, (inicio_rango, final_rango) in enumerate(rangos):
            st.write(f"🔍 Consultando del **{inicio_rango}** al **{final_rango}**")
            
            # Construcción de la URL final
            url = f"{base_url}/from/{inicio_rango}/to/{final_rango}/?email={correo}"
            
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status() # Lanza un error para respuestas 4xx o 5xx

                st.success(f"✅ Solicitud para el rango {inicio_rango} a {final_rango} enviada correctamente. El reporte llegará a tu correo.")

            except requests.exceptions.HTTPError as err:
                st.error(f"❌ Error HTTP en la solicitud: {err.response.status_code} - {err.response.text}")
            except requests.exceptions.RequestException as err:
                st.error(f"❌ Error de conexión: {err}")
            
            # Actualizar barra de progreso
            progress_bar.progress((i + 1) / total_rangos)
            
            # Esperar antes de la siguiente solicitud para no saturar la API
            time.sleep(3)

    st.success("✅ ¡Proceso finalizado! Revisa tu correo electrónico para los reportes.")