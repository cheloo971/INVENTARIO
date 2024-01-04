import streamlit as st
import pandas as pd
import datetime
import requests

# Función para ingresar el número de unidades utilizadas de cada utensilio
def ingresar_utilidades():
    utilidades = {}
    utensilios = [
        "Clinic", "Jabon", "Eyectores", "Vasos",
        "Baberos", "Torulas", "Jeringa 10cc", "Jeringa 20cc", "Guantes doctor",
        "Guantes asistente", "Suero", "Agua oxigenada", "Hipoclorito", "Alcohol",
        "Alcohol quemar"
    ]

    for utensilio in utensilios:
        utilidades[utensilio] = st.number_input(f"{utensilio}", min_value=0, step=1, key=utensilio)
    
    return utilidades


# Configuración de la página
st.set_page_config(
    page_title="Odontología - Inventario",
    page_icon=":tooth:",
    layout="wide"
)

# Estilos y diseño orientado a odontología
st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 3rem;
        background-color: #f5f5f5;
    }
    .stNumberInput {
        width: 150px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Load history from Nextcloud
@st.cache_data()
def load_history_from_nextcloud():
    try:
        nextcloud_url = 'https://nextcloud.espaciofulminante.uk/remote.php/dav/files/celu'
        history_response = requests.get(f'{nextcloud_url}/remote.php/dav/files/celu/inventory_history.csv', 
                                        auth=('celu', 'Eliañ6779'))
        if history_response.status_code == 200:
            history = pd.read_csv(pd.compat.StringIO(history_response.text))
        else:
            history = pd.DataFrame(columns=['Date', 'Box', 'Assistant', 'Clinic', 'Jabon', 'Eyectores', 'Vasos',
                                            'Baberos', 'Torulas', 'Jeringa 10cc', 'Jeringa 20cc', 'Guantes doctor',
                                            'Guantes asistente', 'Suero', 'Agua oxigenada', 'Hipoclorito', 'Alcohol',
                                            'Alcohol quemar'])
    except Exception as e:
        st.error(f"Error: {e}")
        history = pd.DataFrame(columns=['Date', 'Box', 'Assistant', 'Clinic', 'Jabon', 'Eyectores', 'Vasos',
                                        'Baberos', 'Torulas', 'Jeringa 10cc', 'Jeringa 20cc', 'Guantes doctor',
                                        'Guantes asistente', 'Suero', 'Agua oxigenada', 'Hipoclorito', 'Alcohol',
                                        'Alcohol quemar'])
    return history

history = load_history_from_nextcloud()

# Save to Nextcloud
def save_to_nextcloud(data):
    try:
        nextcloud_url = 'https://nextcloud.espaciofulminante.uk/remote.php/dav/files/celu'
        csv_content = data.to_csv(index=False)
        requests.put(f'{nextcloud_url}/remote.php/dav/files/celu/inventory_history.csv', 
                     data=csv_content, 
                     auth=('celu', 'Eliañ6779'))
    except Exception as e:
        st.error(f"Error: {e}")
st.title("Sistema de Inventario - Odontología")
st.markdown("---")

fecha_elegida = st.date_input("Seleccione la fecha", datetime.date.today())

box = st.text_input("Ingrese el número de box:")
asistente = st.selectbox("Seleccione el asistente", ["Asistente 1", "Asistente 2", "Asistente 3"])

utensilios_utilizados = ingresar_utilidades()

# Crear o cargar el DataFrame para el historial
if 'historial' not in st.session_state:
    st.session_state['historial'] = pd.DataFrame(columns=['Fecha', 'Box', 'Asistente'] + list(utensilios_utilizados.keys()))

# Guardar los datos en el historial
if st.button("Guardar"):
    save_to_nextcloud(history)
    st.success("Datos guardados exitosamente en Nextcloud!")
    new_entry = {
        'Fecha': fecha_elegida,
        'Box': box,
        'Asistente': asistente,
        **utensilios_utilizados
    }
    st.session_state['historial'] = pd.concat([st.session_state['historial'], pd.DataFrame([new_entry])], ignore_index=True)
    
    # Reiniciar los valores a cero después de guardar
    st.empty()

# Mostrar el historial actualizado
st.markdown("---")
st.subheader("Historial de Inventario")
st.write(st.session_state['historial'])
