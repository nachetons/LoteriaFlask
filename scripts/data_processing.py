from datetime import datetime
from scripts.database import *
import scripts.database as database
from flask import (
    flash,
    jsonify)


def procesar_datos_formulario(datos_formulario, currentUser):
    # Aquí procesas los datos del formulario
    loteria = datos_formulario['loteria']
    fecha = datos_formulario['fecha']
    apuesta = datos_formulario['apuesta']
    complemento = datos_formulario['complemento']

    fecha2=fecha.replace("-","/")
    fecha_datetime = datetime.strptime(fecha2, "%Y/%m/%d")
    fecha_formateada = fecha_datetime.strftime("%d/%m/%Y")
    database.addBoleto(currentUser, fecha, fecha_formateada, apuesta, complemento, loteria)
    flash("Boleto añadido correctamente", "success")

    print(loteria, fecha, apuesta, complemento)


def procesar_datos_formulario2(datos_formulario, currentUser):
    # Aquí procesas los datos del formulario
    datos_formulario_parser = datos_formulario.split(",")
    loteria = datos_formulario_parser[0].strip().strip("(").strip("'")
    fecha = datos_formulario_parser[1].strip()
    apuesta = datos_formulario_parser[2].strip().strip("'")
    complemento = datos_formulario_parser[3].strip().strip(")").strip("'")

    fecha_sin_comillas = fecha.strip("'")
    
    fecha_datetime = datetime.strptime(fecha_sin_comillas, "%d/%m/%Y")
    fecha_formateada = fecha_datetime.strftime("%Y/%m/%d")
    fecha_final = fecha_formateada.replace("/","-")
    database.eliminarBoleto(currentUser,fecha_final,apuesta,complemento,loteria)



def procesar_datos_grafico(seleccion, currentUser):
    dias = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    años = ['2016', '2017', '2018', '2019', '2020', '2021','2022', '2023'];
    
    duracion=[]
    balance=[]
    fechas=[]
    
    duracion.clear()
    balance.clear()
    fechas.clear()
    if seleccion == 'Semana':
        print("semana")
        resultados = getAllBalance(currentUser, seleccion)
        balance.append(resultados.values())
        fechas.append(resultados.keys())
        date="semana"
        for i in range(7):
            duracion.append(dias[i])
    elif seleccion == 'Mes':
        print("mes")
        resultados = getAllBalance(currentUser, seleccion)
        balance.append(resultados.values())
        fechas.append(resultados.keys())
        date="mes"
        for i in range(12):
            duracion.append(meses[i])
    elif seleccion == 'Año':
        resultados = getAllBalance(currentUser, seleccion)
        balance.append(resultados.values())
        fechas.append(resultados.keys())
        date="año"
        print("año")
        for i in range(8):
            duracion.append(años[i])
    return duracion, balance, fechas, date



def graph(duration, balance, fechas, date):
#    y = [50, 200, 100, 230, 900, 0, 500,900, 200, 500, 0, 900, 0, 500]
    fechas = list(fechas[0])
    balance = list(balance[0])
    dias = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
    meses_idx = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun':5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec':11}
    años_idx = {'2016': 0, '2017': 1, '2018': 2, '2019': 3, '2020': 4, '2021':5, '2022': 6, '2023': 7}
    

    if date == "semana":
        ultimo_lunes = obtener_ultimo_lunes(fechas)
        indice_inicio = fechas.index(ultimo_lunes)
        fechas_seleccionadas = fechas[indice_inicio:]
        balance_seleccionadas = balance[indice_inicio:]
        balance.clear()
        fechas.clear()
        for i in range(len(fechas_seleccionadas)):
            balance.append(balance_seleccionadas[i])
            fechas.append(dias[i])
        for i in range(len(fechas)):
            duration.append(fechas[i])


    

    print(balance)
    print(fechas)
   
    x = duration
    y = balance
    trace = {
        'x': fechas,
        'y': y,
        'mode': 'lines+markers',
        'line': {
            'color': 'rgb(0, 123, 255)',
            'width': 4,
            'shape': 'spline'
        }
    }
    data = [trace]
    layout = {
        'xaxis': {
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
            'tickvals': list(range(len(x))), # Ajusta el número de ticks en el eje x
            'ticktext': x
        },
        'yaxis': {
            'range': [0, 2000],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 400
        }
    }
    return {'data': data, 'layout': layout}

    
def obtener_ultimo_lunes(fechas):
    ultimo_lunes = None
    for fecha in reversed(fechas):
        fecha_dt = datetime.strptime(fecha, "%d-%m-%Y")
        if fecha_dt.weekday() == 0:  # 0 es lunes
            ultimo_lunes = fecha
            break
    if not ultimo_lunes:
        ultimo_lunes = fechas[0]
    return ultimo_lunes

