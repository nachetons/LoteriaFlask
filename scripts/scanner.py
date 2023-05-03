import cv2
import numpy as np
import pytesseract
import imutils
from datetime import datetime


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'


#image = cv2.imread('temp/image.jpg')
#template = cv2.imread('../static/euromillones.png')
# route rel path image


def align_images(image, template, maxFeatures=500, keepPercent=0.2,
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
		#cv2.imshow("Matched Keypoints", matchedVis)
		#cv2.waitKey(0)

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
	readImages(aligned)
	# cv2.imshow("Aligned", aligned2)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

pytesseractText = []

def readImages(image):
    pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    coordenadas = [
    ((250, 470), (1130, 550)),
    ((475, 930), (1000, 1010)),
    ((450, 200), (1200, 280))
]
    for coord in coordenadas:
     (x1, y1), (x2, y2) = coord
     w, h = x2 - x1, y2 - y1

    # x, y, w, h = 250, 470, 880, 80
     image2 = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
     image2 = cv2.resize(image2,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
     cv2.rectangle(image2, (x1, y1), (x2, y2), (0, 0, 255), 2)
     roi = cv2.getRectSubPix(image2, (w, h), (x1 + w/2, y1 + h/2))
     text = pytesseract.image_to_string(roi,lang='spa')
     pytesseractText.append(text)
    parserText(pytesseractText)	
     
     #cv2.imshow('roi', roi) 
     #cv2.waitKey(0)
     #cv2.destroyAllWindows()

    

def parserText(pytesseractText):
	#remove all \n
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
	fecha = pytesseractText[1].replace('\n','')

	dia, mes_abr, anio = fecha.split(' ')
	mes = meses[mes_abr]
	fecha_datetime = datetime.strptime(f'{dia} {mes} {anio}', '%d %m %y')
	fecha_nueva = fecha_datetime.strftime('%Y-%m-%d')

	
	numeroComplemento = pytesseractText[0].replace('\n','')
	numeroSorteo, complemento = numeroComplemento.split('+')
	numeroSorteo = numeroSorteo.replace(' ','')
	complemento = complemento.replace(' ','-')
	complemento = complemento[1:]  



	sorteo = pytesseractText[2].replace('\n','').lower()
	pytesseractText.clear()


	


	print('Texto: ',fecha_nueva+'_'+numeroSorteo+'_'+complemento+'_'+sorteo)

#align_images(image, template, debug=True)
	
