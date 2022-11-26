from easyocr import Reader
import argparse 
import cv2
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-i","--image",default="text_image_03.jpeg")
parser.add_argument("--langs",type=str,default="en",help="en")
parser.add_argument("-g","--gpu",type=int,default=-1,help="whether or not gpu should be used")

args = vars(parser.parse_args())

langs = args["langs"].split(",")
print("[INFO]Using the following languages : {}".format(langs))

#load input image from the disk
image = cv2.imread(args["image"])

#OCR the input using EasyOCR
print("[INFO] Performing OCR on input image...")
reader = Reader(langs,gpu=args["gpu"] > 0)
results = reader.readtext(image)

whole_text = ""
for(bbox,text,prob) in  results:
    whole_text += text + ' '

print(whole_text)































# from PIL import Image
# from pytesseract import pytesseract

# #Define path to tessaract.exe
# path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# #Define path to image
# path_to_image = './textImage.png'

# #Point tessaract_cmd to tessaract.exe
# pytesseract.tesseract_cmd = path_to_tesseract

# #Open image with PIL
# img = Image.open(path_to_image)

# #Extract text from image
# text = pytesseract.image_to_string(img)

# print(text)