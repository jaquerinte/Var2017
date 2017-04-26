import Ice, traceback
import cv2
import sys
import jderobot
import numpy
import Image
import subprocess
import os





if __name__ == "__main__":
  p = subprocess.Popen("heyu monitor", stdout=subprocess.PIPE, shell=True)
  #log = os.system("heyu monitor")
  while True:
    out = p.stdout.readline()
    if out.find("hu A1") != -1:
      print "Movimiento detectado! Grabando video.."
      os.system("python camerarecorder.py")
    sys.stdout.write(out)

  
