import Ice, traceback
import cv2
import sys
import jderobot
import numpy
import Image
from datetime import datetime
import time

def data_to_image (data):
  img= Image.fromstring('RGB', (data.description.width,data.description.height), data.pixelData, 'raw', "BGR")
  pix = numpy.array(img)
  return pix

if __name__ == "__main__":

  status = 0
  ic = None
  try:

    out = cv2.VideoWriter(datetime.now().ctime() + '.avi',cv2.cv.CV_FOURCC('X','V','I','D'), 15.0, (320,240))
    ic = Ice.initialize()    
    obj = ic.stringToProxy('cameraA:default -h localhost -p 9999')


    timeout = time.time() + 10   # 5 minutes from now
    while True:
      cam = jderobot.CameraPrx.checkedCast(obj)
      data = cam.getImageData()
      imagen = data_to_image (data)
      out.write(imagen)
      
      if time.time() > timeout:
        break
      
      

    
  except:
    traceback.print_exc()
    status = 1

    
  if ic:
    try:
      ic.destroy()
    except:
      traceback.print_exc()
      status = 1

  sys.exit(status)
 

