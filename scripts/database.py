from firebaseConf import *
import datetime


def addBoleto(currentUser, fecha, fecha_formateada, apuesta, complemento, loteria):
    db.child("users").child(
        currentUser).child('boletos').child(fecha+'_'+apuesta+'_'+complemento+'_'+loteria).set(
        {"sorteo": loteria,
        "fecha": fecha_formateada, 
        "numero": apuesta, 
        "extra": complemento,
        "premio": "premio",
        "estado": "pendiente"})
    
    

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
    balance_dia = db.child("users").child(currentUser).child("balance_dia").get().val()
    balance_mes = db.child("users").child(currentUser).child("balance_mes").get().val()
    balance_anual = db.child("users").child(currentUser).child("balance_anual").get().val()
    balance_cuenta = db.child("users").child(currentUser).child("balance_cuenta").get().val()
    if balance_dia is None:
        balance_dia = {}
    if balance_mes is None:
        balance_mes = {}
    if balance_anual is None:
        balance_anual = {}
    if balance_cuenta is None:
        balance_cuenta = 0
    

    if seleccion == 'Semana':
        return balance_dia
    elif seleccion == 'Mes':
        return balance_mes
    elif seleccion == 'Año':
        return balance_anual
    elif seleccion == 'Cuenta':
        return balance_cuenta


def eliminarBoleto(currentUser,fecha_final,apuesta,complemento,loteria):
    db.child("users").child(currentUser).child('boletos').child(fecha_final+'_'+apuesta+'_'+complemento+'_'+loteria).remove()


def lastResults():
    Euromillones=db.child("ultimosresultados/euromillones/resultado").get().val()
    Bonoloto=db.child("ultimosresultados/bonoloto/resultado").get().val()
    Primitiva=db.child("ultimosresultados/primitiva/resultado").get().val()
    ElGordo=db.child("ultimosresultados/elgordo/resultado").get().val()

    return Euromillones, Bonoloto, Primitiva, ElGordo