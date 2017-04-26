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

# The scan message
from sensor_msgs.msg import LaserScan

from geometry_msgs.msg import Twist

import pygame, sys
from pygame.locals import *
from keras.preprocessing import image
from imagenet_utils import preprocess_input


optimizer = 'adam'
thesshole = 0.001

def signal_handler(signal, frame):
	exit(0)
signal.signal(signal.SIGINT,signal_handler)

class NavigationNode:

		def __init__(self):
				self.bridge = CvBridge()
				self.image_sub = rospy.Subscriber("/robot4/camera/rgb/image_raw",Image,self.extracionImagen)
				self.laser_sub = rospy.Subscriber("/robot4/scan",LaserScan, self.laser_callback)
				self.tower = rospy.Subscriber("/central_tower/race_state",String,self.towerControl)
				self.cmd_vel = rospy.Publisher("/robot4/mobile_base/commands/velocity",Twist,queue_size=1)
				self.lastImage = None 
				self.laserScan = None
				self.state = None 

				self.model = resnet50.ResNet50()
				filename = "./weights/weightNoSuffle.hdf5"
				self.model.load_weights(filename)
				self.model.compile(loss='mse',optimizer=optimizer,metrics=['accuracy'])

		def extracionImagen(self,data):
			try:
					cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
					self.lastImage = cv_image
			except Exception as e:
				print(e)
		def laser_callback(self,laserdata):
			self.laserScan = laserdata
		def towerControl(self,data):
			self.state = data.data	

		def stop(self,move_cmd,count):
			mini = self.laserScan.angle_min
			maxi = self.laserScan.angle_max
			incr = self.laserScan.angle_increment
			total = ((maxi - mini) * incr) 
			medianpos = total/ 2
			#deteccion corner eslalon
			if self.laserScan.ranges[2] < 0.7 and self.laserScan.ranges[int(total)-2] < 0.7:
			 	#print("stop")
			 	
			 	move_cmd.linear.x = 0
			 	move_cmd.angular.z = 2
			 	count = 10
			#deteccion del callejon sin salida 

			if ((self.lastImage[231][240][0] == 45 and self.lastImage[231][430][0] == 45 
				and self.lastImage[231][0][0] == 100
				and self.lastImage[231[160]][0] == 100
				and self.lastImage[231][630][0] == 31
				and self.lastImage[231][480][0] == 31) or 
				(self.lastImage[231][0][0] == 45
				and self.lastImage[231][165][0] == 100
				and self.lastImage[231][280][0] == 100
				and self.lastImage[231][420][0] == 45
				and self.lastImage[231][630][0] == 31)):
				#print("callejon")
				move_cmd.linear.x = 0
			 	move_cmd.angular.z = 0.5
			 	count = 10

			#ajuste de la pocion del robot
			if count > 0: 
				move_cmd.linear.x = 0
			 	move_cmd.angular.z = 2
			 	count = count - 1
			 	self.cmd_vel.publish(move_cmd)
			 	return count

			self.cmd_vel.publish(move_cmd)


		#modulo principal de ejecucion
		def run(self):
			count = 0
			#while str(self.state) != "GO" :
			#	print("WAITING")

			while str(self.state) != "FINISHED":
				try:
					cv2.imshow("Image",self.lastImage)
					cv2.waitKey(3)
					batch = [cv2.resize(self.lastImage,(224,224))]
					x = np.array(batch)
					#salida de la red neuronal
					output = self.model.predict(x,batch_size=1,verbose = 0)
					move_cmd = Twist()
					move_cmd.linear.x = output[0][0]
					move_cmd.angular.z = output[0][1]
					#llamada al metodo que regula el comportamiento del robot en los casos donde da fallo
					count = self.stop(move_cmd,count)
				except Exception as e:
					print(e)
					continue

def main(args):
	ic = NavigationNode()
	rospy.init_node('NavigationNode',anonymous=True)
	ic.run()
if __name__ == '__main__':
    main(sys.argv)
