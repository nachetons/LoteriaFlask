from firebaseConf import *
import datetime as times
from flask import (
    flash)


def addBoleto(currentUser, fecha, fecha_formateada, apuesta, complemento, loteria):
    fecha_actual = times.datetime.now().date() 
    fecha_boleto = times.datetime.strptime(fecha, "%Y-%m-%d").date() 

    diff = fecha_actual - fecha_boleto

  
    if diff.days <= 90:
        db.child("users").child(
            currentUser).child('boletos').child(fecha+'_'+apuesta+'_'+complemento+'_'+loteria).set(
            {
            "sorteo": loteria,
            "fecha": fecha_formateada, 
            "numero": apuesta, 
            "extra": complemento,
            "premio": "premio",
            "estado": "pendiente"
            })
        flash("Boleto añadido correctamente", "success")
    else:
        flash("La fecha del boleto es mayor a 3 meses", "danger")
        return False
    
    

def getBoletos(currentUser):
    ref = db.child("users").child(currentUser).child('boletos')
    if ref.get().val() is not None:
        boletos = db.child("users").child(currentUser).child('boletos').get().val().values()
    else:
        db.child("users").child(currentUser).child('boletos').set({})
        boletos = {}
    return boletos



#function to getAllBalance
def getAllBalance(currentUser, seleccion):
    balances = db.child("users").child(currentUser).get().val()
    balance_dia = balances.get("balance_dia", {})
    balance_mes = balances.get("balance_mes", {})
    balance_anual = balances.get("balance_anual", {})
    balance_cuenta = balances.get("balance_cuenta", 0)

    balances_map = {
        'Semana': balance_dia,
        'Mes': balance_mes,
        'Año': balance_anual,
        'Cuenta': balance_cuenta
    }
    return balances_map.get(seleccion, {})


def eliminarBoleto(currentUser,fecha_final,apuesta,complemento,loteria):
    db.child("users").child(currentUser).child('boletos').child(fecha_final+'_'+apuesta+'_'+complemento+'_'+loteria).remove()


def lastResults():
    Euromillones=db.child("ultimosresultados/euromillones/resultado").get().val()
    Bonoloto=db.child("ultimosresultados/bonoloto/resultado").get().val()
    Primitiva=db.child("ultimosresultados/primitiva/resultado").get().val()
    ElGordo=db.child("ultimosresultados/elgordo/resultado").get().val()

    return Euromillones, Bonoloto, Primitiva, ElGordo