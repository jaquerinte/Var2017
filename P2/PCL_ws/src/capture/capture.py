#!/usr/bin/env python
from __future__ import print_function
import roslib
#roslib.load_manifest('deep_navigation')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge, CvBridgeError

from geometry_msgs.msg import Twist

import pygame, sys
from pygame.locals import *



class NavigationNode:

  def __init__(self):

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/camera/rgb/image_raw",Image,self.imageCallback)
    self.odom_sub = rospy.Subscriber("/odom",Odometry,self.odomCallback)

    self.cmd_vel = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1)
    
    self.lastLinearVelocityX = None
    self.lastAngularVelocityZ = None
    self.lastImage = None

  def odomCallback(self, data):
    #print("Linear:",data.twist.twist.linear)
    self.lastLinearVelocityX = data.twist.twist.linear.x
    #print("Angular",data.twist.twist.angular)
    self.lastAngularVelocityZ = data.twist.twist.angular.z

  def imageCallback(self,data):
    try:
      cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
      self.lastImage = cv_image
    except CvBridgeError as e:
      print(e)

  def run(self):

    f = open('manifest.txt','w')
    
    move_cmd = Twist()
    move_cmd.linear.x = 0
    move_cmd.angular.z = 0
    try:
      i=0
      while True:
        #rospy.spin()
        for event in pygame.event.get():
          if event.type == QUIT: sys.exit()
          if event.type == KEYDOWN and event.key == K_a: # left
			move_cmd.linear.x = 0.0
			move_cmd.angular.z = 0.2
          if event.type == KEYDOWN and event.key == K_d: # right
			move_cmd.linear.x = 0.0
			move_cmd.angular.z = -0.2
          if event.type == KEYDOWN and event.key == K_w: # straight
			move_cmd.angular.z = 0.0
			move_cmd.linear.x = 0.3
          if event.type == KEYDOWN and event.key == K_s: # stop
			move_cmd.linear.x = 0.0
			move_cmd.angular.z = 0.0
          

        pygame.event.pump()
        cv2.imshow("Image window", self.lastImage)
        cv2.waitKey(3)

        # Save Velocities and Image
      	if move_cmd.linear.x != 0.0 or move_cmd.angular.z != 0.0:
          print("Vel Lin:",move_cmd.linear.x, "Vel Ang:",move_cmd.angular.z)
        #  fileName = 'dataset-circuit/'+str(i)+'.jpg'
        #  cv2.imwrite(fileName, self.lastImage)
        #  f.write(fileName+ ' '+str(move_cmd.linear.x)+' '+str(move_cmd.angular.z)+'\n')


        self.cmd_vel.publish(move_cmd)
        i+=1
    except KeyboardInterrupt:
      print("Shutting down")
    cv2.destroyAllWindows()


def main(args):

  pygame.init()
  pygame.display.set_mode((100,100))

  ic = NavigationNode()
  rospy.init_node('NavigationNode', anonymous=True)
  ic.run()
  

if __name__ == '__main__':
    main(sys.argv)
