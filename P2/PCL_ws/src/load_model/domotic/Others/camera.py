import Ice
import cv2


if __name__ == "__main__":
  print "working"
  cap = cv2.VideoCapture(0)
  cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 360)
  cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
  cv2.namedWindow("cam")
  

  while(cap.isOpened()):
    ret, frame = cap.read()

    

    cv2.imshow('cam',frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

  cap.release()
  cv2.destroyAllWindows()
