from firebaseConf import *
 

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
    boletos = db.child("users").child(currentUser).child('boletos').get().val().values()
    return boletos

def eliminarBoleto(currentUser,fecha_final,apuesta,complemento,loteria):
    db.child("users").child(currentUser).child('boletos').child(fecha_final+'_'+apuesta+'_'+complemento+'_'+loteria).remove()


def lastResults():
    Euromillones=db.child("ultimosresultados/euromillones/resultado").get().val()
    Bonoloto=db.child("ultimosresultados/bonoloto/resultado").get().val()
    Primitiva=db.child("ultimosresultados/primitiva/resultado").get().val()
    ElGordo=db.child("ultimosresultados/elgordo/resultado").get().val()

    return Euromillones, Bonoloto, Primitiva, ElGordo