import cv2
import numpy as np
import pytesseract
import imutils
import re

from datetime import datetime
import scripts.database as database
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


# image = cv2.imread('temp/image.jpg')
# template = cv2.imread('../static/euromillones.png')
# route rel path image


def align_images(image, template, currentUser, maxFeatures=500, keepPercent=0.2,
	debug=False):
	# transformar la imagen a escala de grises
	imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

	# usamos ORB para detectar puntos clave y extraer el(binario) local
	# características invariantes
	orb = cv2.ORB_create(maxFeatures)
	(kpsA, descsA) = orb.detectAndCompute(imageGray, None)
	(kpsB, descsB) = orb.detectAndCompute(templateGray, None)

	# coincidir con las características
	method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
	matcher = cv2.DescriptorMatcher_create(method)
	matches = matcher.match(descsA, descsB, None)

	# ordenar las coincidencias por su distancia (cuanto menor es la distancia,
	#  más "similares" sean las características)
	matches = sorted(matches, key=lambda x: x.distance)

	# mantener solo las mejores coincidencias
	keep = int(len(matches) * keepPercent)
	matches = matches[:keep]

	# comprobar para ver si debemos visualizar los puntos clave coincidentes
	if debug:
		matchedVis = cv2.drawMatches(image, kpsA, template, kpsB,
			matches, None)
		matchedVis = imutils.resize(matchedVis, width=1000)
		# cv2.imshow("Matched Keypoints", matchedVis)
		# cv2.waitKey(0)

	# asignar memoria para los puntos clave en las coordenadas x, y.De las
	# coincidencias principales: usaremos estas coordenadas para calcular nuestra
	# matriz de homografía
	ptsA = np.zeros((len(matches), 2), dtype="float")
	ptsB = np.zeros((len(matches), 2), dtype="float")

	for (i, m) in enumerate(matches):
		# indicamos los dos puntos de la perspectiva de la imagen
		ptsA[i] = kpsA[m.queryIdx].pt
		ptsB[i] = kpsB[m.trainIdx].pt

	# compute the homography matrix between the two sets of matched
	# points
	(H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)

	# usamos la homografia matrix para alinear imagenes
	(h, w) = template.shape[:2]
	aligned = cv2.warpPerspective(image, H, (w, h))
	aligned2 = cv2.resize(aligned, None, fx=0.5, fy=0.5,
	                      interpolation=cv2.INTER_CUBIC)
	readImages(aligned, currentUser)
	# cv2.imshow("Aligned", aligned2)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()


pytesseractText = []


def readImages(image, currentUser):
    pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    coordenadas = [
    ((250, 470), (1130, 550)),
    ((500, 930), (900, 990)),
    ((430, 215), (1000, 290))
]
    for coord in coordenadas:
     (x1, y1), (x2, y2) = coord
     w, h = x2 - x1, y2 - y1

    # x, y, w, h = 250, 470, 880, 80
     image2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     image2 = cv2.resize(image2, None, fx=2, fy=2,
                         interpolation=cv2.INTER_CUBIC)
     cv2.rectangle(image2, (x1, y1), (x2, y2), (0, 0, 255), 2)
     roi = cv2.getRectSubPix(image2, (w, h), (x1 + w/2, y1 + h/2))
     text = pytesseract.image_to_string(roi, lang='spa')

     pytesseractText.append(text)
    if validar(pytesseractText):
        parserText(pytesseractText, currentUser)
    else:
        pytesseractText.clear()
        print("Los datos recibidos no cumplen con el formato esperado.")
	    
	    
	    
	     
	
     
     #cv2.imshow('roi', roi) 
     #cv2.waitKey(0)
     #cv2.destroyAllWindows()

    

def parserText(pytesseractText, currentUser):
	meses = {
    'ENE': '01',
    'FEB': '02',
    'MAR': '03',
    'ABR': '04',
    'MAY': '05',
    'JUN': '06',
    'JUL': '07',
    'AGO': '08',
    'SEP': '09',
    'OCT': '10',
    'NOV': '11',
    'DIC': '12',
}
	numero_regex = r'^\s*\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\+\s+\d{2}\s+\d{2}\s*$'
	fecha_regex = r'^\d{1,2}\s\w{3}\s\d{2}$'
	fechass = pytesseractText[1].replace('\n','')



	print(pytesseractText[0],pytesseractText[1],pytesseractText[2])

	if re.match(numero_regex, pytesseractText[0]) and re.match(fecha_regex, fechass):
		fecha = pytesseractText[1].replace('\n','')
		dia, mes_abr, anio = fecha.split(' ')
		mes = meses[mes_abr]
		fecha_datetime = datetime.strptime(f'{dia} {mes} {anio}', '%d %m %y')
		fecha_nueva = fecha_datetime.strftime('%Y-%m-%d')
		fechaFormateada = fecha_datetime.strftime('%d/%m/%Y')	
	
		numeroComplemento = pytesseractText[0].replace('\n','')
		numeroSorteo, complemento = numeroComplemento.split('+')
		numeroSorteo = numeroSorteo.replace(' ','')
		complemento = complemento.replace(' ','-')
		complemento = complemento[1:]  

		sorteo = pytesseractText[2].replace('\n','').lower()
		pytesseractText.clear()

		content = fecha_nueva+'_'+numeroSorteo+'_'+complemento+'_'+sorteo
		print('Texto: ',content)
		database.addBoleto(
			currentUser,
			fecha_nueva,
			fechaFormateada,
			numeroSorteo,
			complemento,
			sorteo,

	)
		print('Boleto añadido correctamente')
	else:
		print('Los datos recibidos no cumplen con el formato esperado.')


def validar(texto):
	numero_regex = r'^\s*\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\s+\+\s+\d{2}\s+\d{2}\s*$'
	fecha_regex = r'^\d{1,2}\s\w{3}\s\d{2}$'
	fechass = texto[1].replace('\n','')

	if re.match(numero_regex, texto[0]) and re.match(fecha_regex, fechass) and len(pytesseractText) == 3:
		return True
	else:
		return False
	
	

#align_images(image, template, debug=True)
	
