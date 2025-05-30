import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# Establecer tema oscuro (esto es solo para Streamlit Cloud o config local)
st.set_page_config(page_title="Reporte de Visitas", page_icon="📅", layout="centered")

st.markdown(
    """
    <style>
    body {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Reporte de Visitas - SimpliRoute")

# Inputs de usuario
token = st.text_input("🔐 Token de autenticación")
correo = st.text_input("📧 Correo de usuario")

col1, col2 = st.columns(2)
with col1:
    inicio = st.date_input("📅 Fecha de inicio", value=datetime.today() - timedelta(days=7))
with col2:
    final = st.date_input("📅 Fecha final", value=datetime.today())

opcion = st.radio("📆 ¿Cómo quieres dividir el rango?", ("Semanal", "Quincenal", "Mensual"))

# Botón de ejecución
if st.button("🚀 Ejecutar solicitudes"):
    if not token or not correo:
        st.warning("⚠️ Debes ingresar el token y el correo.")
        st.stop()

    # Funciones para dividir rangos
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
            ultimo_dia_mes = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            fin_mes = min(ultimo_dia_mes, final)
            rangos.append((inicio.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")))
            inicio = fin_mes + timedelta(days=1)
        return rangos

    # Determinar rangos
    if opcion == "Semanal":
        rangos = dividir_rango_por_dias(inicio, final, 7)
    elif opcion == "Quincenal":
        rangos = dividir_rango_por_dias(inicio, final, 15)
    elif opcion == "Mensual":
        rangos = dividir_rango_por_mes(inicio, final)

    # Encabezados con token del usuario
    headers = {
        "authorization": f"Token {token}",
        "origin": "https://app2.simpliroute.com",
        "user-agent": "Mozilla/5.0",
        "accept": "application/json",
        "referer": "https://app2.simpliroute.com/",
    }

    for inicio_rango, final_rango in rangos:
        st.write(f"🔍 Consultando del **{inicio_rango}** al **{final_rango}**")
        url = f"https://api.simpliroute.com/v1/reports/visits/from/{inicio_rango}/to/{final_rango}/?email={correo}"
        response = requests.get(url, headers=headers)

        try:
            data = response.json()
            if isinstance(data, list):
                st.success(f"✅ {len(data)} registros recibidos.")
            else:
                st.warning("⚠️ Formato inesperado en la respuesta.")
        except:
            st.error(f"❌ Error al decodificar respuesta: {response.text}")

        time.sleep(3)

    st.success("✅ Todas las solicitudes han sido procesadas.")
