from datetime import datetime
import scripts.database as database
from flask import (
    flash)


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
