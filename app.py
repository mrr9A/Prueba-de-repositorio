import pandas as pd
from flask import Flask, render_template, request
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import io
import base64

# Configuración de la conexión a la base de datos
host = 'localhost'
usuario = 'root'
password = ''
base_de_datos = 'accidentes'

# Crear la conexión a la base de datos
conec = create_engine(f'mysql+mysqlconnector://{usuario}:{password}@{host}/{base_de_datos}')

app = Flask(__name__)

# Consulta a la base de datos para obtener los datos agrupados por REF_AREA y TIME_PERIOD
query = '''
SELECT REF_AREA, TIME_PERIOD, OBS_VALUE
FROM accidentes
'''

# Ejecutar la consulta y cargar los datos en un DataFrame de pandas
datos = pd.read_sql_query(query, conec)

@app.route('/')
def index():
    ref_areas = sorted(datos['REF_AREA'].unique())  # Ordenar alfabéticamente
    time_periods = datos['TIME_PERIOD'].unique()
    return render_template('index.html', ref_areas=ref_areas, time_periods=time_periods)

@app.route('/results', methods=['POST'])
def results():
    selected_ref_area = request.form['ref_area']
    selected_time_period = request.form['time_period']
    
    filtered_data = datos[(datos['REF_AREA'] == selected_ref_area)]

    # Asegurarse de que los valores en OBS_VALUE sean numéricos
    filtered_data['OBS_VALUE'] = pd.to_numeric(filtered_data['OBS_VALUE'], errors='coerce')

    # Generar colores para la gráfica
    colors = ['#4CAF50' if period == selected_time_period else '#FFC107' for period in filtered_data['TIME_PERIOD']]

    plt.figure(figsize=(10, 5))
    plt.bar(filtered_data['TIME_PERIOD'], filtered_data['OBS_VALUE'], color=colors)
    plt.xlabel('Time Period')
    plt.ylabel('Observations')
    plt.title(f'Accidents in {selected_ref_area} for {selected_time_period}')
    plt.ylim(0, filtered_data['OBS_VALUE'].max() + 10)  # Ajustar para que comience desde 0

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # Resaltar el periodo seleccionado en la tabla
    filtered_data['highlight'] = filtered_data['TIME_PERIOD'] == selected_time_period

    # Convertir el DataFrame a una lista de diccionarios para pasarlo a la plantilla
    data_list = filtered_data.to_dict(orient='records')

    return render_template('results.html', plot_url=plot_url, data=data_list)

if __name__ == '__main__':
    app.run(debug=True)
