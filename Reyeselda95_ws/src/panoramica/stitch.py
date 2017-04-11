#!/usr/bin/env python

# USAGE
# python stitch.py --first images/bryce_left_01.png --second images/bryce_right_01.png 
# python stitch.py -f imagenizq.jpg -s imagender.png

# import the necessary packages
from pyimagesearch.panorama import Stitcher
import argparse
import imutils
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rospy
import sys
import time

class Panorama:

	def __init__(self):
		# Inicializamos el puente para utilizar OpenCV y obtener las imagenes a partir de los topicos de ROS
	    self.bridge = CvBridge()
	    # Obtenemos la imagen de la camara trasera izquierda
	    self.image_sub = rospy.Subscriber("/robot4/trasera2/trasera2/rgb/image_raw",Image,self.imageCallbackIzq)
	    # Obtenemos la imagen de la camara trasera derecha
	    self.image_sub = rospy.Subscriber("/robot4/trasera1/trasera1/rgb/image_raw",Image,self.imageCallbackDer)

	    # Inicializamos las imagenes a None
	    self.ImageIzq = None
	    self.ImageDer = None

	def imageCallbackIzq(self,data):
		try:
			# Obetenemos la imagen del topico y la transformamos a un formato entendible para OpenCV
			cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
			self.ImageIzq = cv_image
		except CvBridgeError as e:
			print(e) # Si se produce algun error se imprime

	def imageCallbackDer(self,data):
		try:
			# Obetenemos la imagen del topico y la transformamos a un formato entendible para OpenCV
			cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
			self.ImageDer = cv_image
		except CvBridgeError as e:
			print(e) # Si se produce algun error se imprime

	# Llama al algoritmo de stitch
	def run(self):
		while True:
			try:
				# Transformamos las imagenes para que tengan un ancho de 400 pixeles
				#imageA = imutils.resize(self.ImageIzq, width=400) 
				#imageB = imutils.resize(self.ImageDer, width=400)

				imageA = self.ImageIzq
				imageB = self.ImageDer

				# Junta las imagenes para crear una panoramica
				stitcher = Stitcher()
								
				# Muestra las imagenes
				#cv2.imshow("Image A", imageA) # Muestra la imagen de la izquierda
				#cv2.imshow("Image B", imageB) # Muestra la imagen de la derecha
				#cv2.waitKey(3) # Necesario para que se muestren las imagenes antes de que se ejecute el algoritmo, en caso de error en el mismo
				#result= stitcher.stitch([imageA, imageB], showMatches=False) # Devuelve unicamente la transformacion de la imagen.
				(result, vis) = stitcher.stitch([imageA, imageB], showMatches=True) # Devuelve la imagen transformada y la visualizacion de sus puntos comunes

				cv2.imshow("Keypoint Matches", vis)
				cv2.imshow("Result", result)
				cv2.imwrite("panorama.png",result) # Guardamos la panoramica en el archivo "panorama.jpg"
				time.sleep(.300) # Esperamos 300 milisegundos antes de ejecutar la siguiente panoramica
				cv2.waitKey(3) # Debemos poner un waitkey para que muestre las imagenes
			except Exception as e:
				#print(e) #imprime la excepcion en caso de ser necesaria
				continue

def main(args):
	# Creaamos una instancia de la clase panorama
	ic = Panorama()
	# Iniciamos el nodo panorama llamando a __init__ de su clase
	rospy.init_node('Panorama', anonymous=True)
	# Llamamos al algoritmo
	ic.run()
  

if __name__ == '__main__':
    main(sys.argv)
