#!/usr/bin/python

import sys, traceback, Ice
import Temp
import time
import random
import subprocess
from threading import Thread
from Colors import Colors

class TemperatureI(Temp.Temperature):  
  def getTemperature(self, n, current=None):
    if n == 1:
      return T
    elif n == 2:
      return T2
    


if __name__ == "__main__":
  status = 0
  ic = None
  T = 0
  TF = 0
  T2 = 0
  TF2 = 0
  txt = Colors()
  try:
    ic = Ice.initialize(sys.argv)
    adapter = ic.createObjectAdapterWithEndpoints("TemperatureAdapter", ic.getProperties().getProperty("TemperatureServer.Endpoints"))
    object = TemperatureI()
    adapter.add(object, ic.stringToIdentity("Temperature"))
    adapter.activate()
  except:
    status = 1
    traceback.print_exc()

  sys.stdout.write(txt.warning("Monitoring sensor...\t"))
  sys.stdout.flush()
  p = subprocess.Popen("sudo pcsensor", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
  out = p.stdout.readline()
  if out.find("Couldn't find the USB device, Exiting") == -1:
    print txt.bold(txt.green("Running"))
  else:
    print txt.bold(txt.fail("Failed --> " + out ))
    sys.exit()
  while True:
    p = subprocess.Popen("sudo pcsensor", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    p.stdout.readline()
    internal = p.stdout.readline()
    ipieces = internal.split(" ")
    T = float(ipieces[3][:-2])
    TF = float(ipieces[2][:-2])
    external = p.stdout.readline()
    epieces = external.split(" ")
    T2 = float(epieces[3][:-2])
    TF2 = float(epieces[2][:-2])
    time.sleep(1)
  ic.waitForShutdown()

  
    

  if ic:
    # Clean up
    try:
      ic.destroy()
    except:
      traceback.print_exc()
      status = 1

  sys.exit(status)
