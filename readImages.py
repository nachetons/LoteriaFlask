import cv2
import pytesseract


def readImages():
    pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    image = cv2.imread('static/euromillones2.png')
    x, y, w, h = 250, 470, 880, 80


    #read numbers delete background image add blur and scales white and black
    image2 = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    image2 = cv2.resize(image2,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)


    cv2.rectangle(image2, (x, y), (x + w, y + h), (0, 0, 255), 2)
    roi = cv2.getRectSubPix(image2, (w, h), (x + w/2, y + h/2))
    text = pytesseract.image_to_string(roi,lang='spa')
    print('Texto: ',text)
      
    #cv2.imshow('Image',image2)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

readImages()