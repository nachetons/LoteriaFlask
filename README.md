## DEMO DEL PROYECTO
Esta aplicacion de Loteria esta creada en flask utiliza la libreria de bootstrap4 y se conecta a la base de datos firebase.
Este proyecto te aporta distintas utilidades:
- Poder ver en tiempo real los resultados de los ultimos sorteos
- Poder iniciar sesion y almacenar tus propios boletos
- Si no quieres introducir el boleto de forma manual, no hay problema ya que con tesseract, uno de los motores mas potentes de tecnologiaOCR de google, atraves de una simple foto te extrae los datos y te lo sube a la base de datos
- Tienes a tu disposicion unas metricas para analizar en todo momento tu balance de ganancias y perdidas

## INSTALACION

1. Tener instalado python 3.9
2. Instalar tesseractOCR para tu sistema operativo https://github.com/UB-Mannheim/tesseract/wiki (Instalar en el proceso el paquete de spanish)
3. Instalar las librerias del proyecto atraves del archivo requeriments.txt
```sh
pip install -r requirements.txt
```

4. Crear un proyecto de firebase https://firebase.google.com/ ingresar a la configuracion del proyecto y copiar la configuracion, sustituirla en firebaseConf

![image](https://user-images.githubusercontent.com/46556874/236474397-d3d4ca3e-e23c-4bae-912e-3c9e323a8b0a.png)


5. Generar la clave privada admin sdk del certificado de tu base de datos, añadirlo a la raiz del proyecto, cambiarle el nombre a admin.json

![image](https://user-images.githubusercontent.com/46556874/236477191-62dba4dc-1705-4904-9635-92e332f28fb5.png)


## ARRANCAR PROYECTO


Para arrancar el proyecto debemos ejectar el comando:
```sh
flask run
```
