import Ice, traceback
import cv2
import sys
import jderobot
import numpy
import Image

def data_to_image (data):
  img= Image.fromstring('RGB', (data.description.width,data.description.height), data.pixelData, 'raw', "BGR")
  pix = numpy.array(img)
  return pix

if __name__ == "__main__":

  status = 0
  ic = None
  try:
    ic = Ice.initialize()    
    obj = ic.stringToProxy('cameraA:default -h localhost -p 9999')
    cv2.namedWindow("My CameraView (Python)")


    while(1):
      cam = jderobot.CameraPrx.checkedCast(obj)
      data = cam.getImageData("RGB8")
      imagen = data_to_image (data)
      cv2.imshow('My CameraView (Python)',imagen)
      cv2.waitKey(30)
      
        
    cv2.destroyAllWindows()

    
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
 

