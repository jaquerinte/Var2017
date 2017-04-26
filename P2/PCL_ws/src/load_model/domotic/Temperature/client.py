import sys, traceback, Ice
import Temp
import time

status = 0
ic = None
try:
  ic = Ice.initialize(sys.argv)
  base = ic.stringToProxy("Temperature:default -p 10001")
  printer = Temp.TemperaturePrx.checkedCast(base)
  if not printer:
    raise RuntimeError("Invalid proxy")

  while True:  
    print printer.getTemperature()
    time.sleep(2)
    
  print printer.checkStatus()
except:
  traceback.print_exc()
  status = 1
    

  

if ic:
  # Clean up
  try:
    ic.destroy()
  except:
    traceback.print_exc()
    status = 1

sys.exit(status)
