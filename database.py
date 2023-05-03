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

def eliminarBoleto(currentUser,fecha_final,apuesta,complemento,loteria):
    db.child("users").child(currentUser).child('boletos').child(fecha_final+'_'+apuesta+'_'+complemento+'_'+loteria).remove()