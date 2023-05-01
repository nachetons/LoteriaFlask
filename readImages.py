import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
image = cv2.imread('static/euromillones.png')
#read numbers delete background image add blur and scales white and black
image2 = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
image2 = cv2.threshold(image2,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
image2 = cv2.medianBlur(image2,3)
image2 = cv2.resize(image2,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)

text = pytesseract.image_to_string(image2,lang='spa')
print('Texto: ',text)
      
cv2.imshow('Image',image2)
cv2.waitKey(0)
cv2.destroyAllWindows()