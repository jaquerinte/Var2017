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

class Panorama:

	def __init__(self):

	    self.bridge = CvBridge()
	    self.image_sub = rospy.Subscriber("/robot4/trasera1/trasera1/rgb/image_raw",Image,self.imageCallbackIzq)
	    self.image_sub = rospy.Subscriber("/robot4/trasera2/trasera2/rgb/image_raw",Image,self.imageCallbackDer)


	    self.ImageIzq = None
	    self.ImageDer = None

	def imageCallbackIzq(self,data):
		try:
			cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
			self.ImageIzq = cv_image
		except CvBridgeError as e:
			print(e)

	def imageCallbackDer(self,data):
		try:
			cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
			self.ImageDer = cv_image
		except CvBridgeError as e:
			print(e)

	def run(self):
		
		while True:
			# construct the argument parse and parse the arguments
			#ap = argparse.ArgumentParser()
			#ap.add_argument("-f", "--first", required=True,
			#	help="path to the first image")
			#ap.add_argument("-s", "--second", required=True,
			#	help="path to the second image")
			#args = vars(ap.parse_args())

			# load the two images and resize them to have a width of 400 pixels
			# (for faster processing)
			#imageA = cv2.imread(args["first"])
			#imageB = cv2.imread(args["second"])
			try:
				imageA = imutils.resize(self.ImageIzq, width=400)
				imageB = imutils.resize(self.ImageDer, width=400)

				# stitch the images together to create a panorama
				stitcher = Stitcher()
				(result, vis) = stitcher.stitch([imageA, imageB], showMatches=True)

				# show the images
				cv2.imshow("Image A", imageA)
				cv2.imshow("Image B", imageB)
				cv2.imshow("Keypoint Matches", vis)
				cv2.imshow("Result", result)
				cv2.imwrite("panorama.png",result)
			except Exception:
				continue

def main(args):
	ic = Panorama()
	rospy.init_node('Panorama', anonymous=True)
	ic.run()
  

if __name__ == '__main__':
    main(sys.argv)
