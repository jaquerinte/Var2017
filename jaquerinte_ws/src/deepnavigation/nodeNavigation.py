#!/usr/bin/env python
from __future__ import print_function
import roslib
import signal, os
roslib.load_manifest('deepnavigation')
import sys
import rospy
import cv2
from resnet50 import ResNet50
import resnet50
import numpy as np
from keras.models import load_model
import keras.backend as K
from std_msgs.msg import String
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge, CvBridgeError

from geometry_msgs.msg import Twist

import pygame, sys
from pygame.locals import *

optimizer = 'rmsprop'

def signal_handler(signal, frame):
	exit(0)
signal.signal(signal.SIGINT,signal_handler)

class NavigationNode:

		def __init__(self):
				self.bridge = CvBridge()
				self.image_sub = rospy.Subscriber("/robot1/camera/rgb/image_raw",Image,self.extracionImagen)
				self.cmd_vel = rospy.Publisher("/robot1/mobile_base/commands/velocity",Twist,queue_size=1)
				self.lastImage = None 

				self.model = resnet50.ResNet50()
				filename = "./weights/turteblotNew.h5"
				self.model.load_weights(filename)
				self.model.compile(loss='mse',optimizer=optimizer,metrics=['accuracy'])

		def extracionImagen(self,data):
			try:
					cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
					self.lastImage = cv_image
			except CvBridgeError as e:
				print(e)

		def run(self):
			while True:
				try:
						cv2.imshow("Image",self.lastImage)
						cv2.waitKey(3)
				except Exception as e:
						print(e)
				batch = [cv2.resize(self.lastImage,(224,224))]
				output = self.model.predict(np.array(batch),batch_size=1,verbose = 0)
				print(output)
				move_cmd = Twist()
				move_cmd.linear.x = output[0][0]
				move_cmd.angular.z = output[0][1]
				print("velocidad lineal :"+str(move_cmd.linear.x))
				print("velocidad angular :"+str(move_cmd.angular.z))
				self.cmd_vel.publish(move_cmd)

def main(args):
	ic = NavigationNode()
	rospy.init_node('NavigationNode',anonymous=True)
	ic.run()
if __name__ == '__main__':
    main(sys.argv)