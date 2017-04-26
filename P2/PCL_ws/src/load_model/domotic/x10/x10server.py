import sys, traceback, Ice, os
import x10
from Mod import Mod
from Colors import Colors
import subprocess
from threading import Thread
import time, datetime


Modules = []


class NetI(x10.Net):
  def sendMsg(self, s, current=None):
    print s
    
  def showEnvironment(self, current=None):
    response = ""
    response += txt.underline(txt.bold("House " + props["x10server.HouseCode"] + " Environment\n"))
    response += "Name\t\tCode\t\tType\t\tActive\n"
    for i in Modules:
      if i.active:
        response += txt.green(str(i)+"\n")
      else:
        response += txt.gray(str(i)+"\n")
    print response
    
  def isCode(self, code, current=None):
    for i in Modules:
      if (i.code == code):
        return True
    return False
        
    
  def getEnvironment(self, current=None):
    response = ""
    for i in Modules:
      response += i.code + "|" + i.name + "|" + i.mtype + "|" + str(i.active) + "|"
    return response
  
  def setActive(self, name, current=None):
    found = False
    for i in Modules:
      if (i.name == name) and i.isSensor() != True:
        if i.active == False:
          print txt.warning("  Activating module " + i.name + "...")
        i.setActive()
        found = True
        break
      if (i.name == name) and i.isSensor() == True:
        print txt.warning("  Impossible to activate " + i.name + "...")
        found = True
        break
    if found == False:
      print txt.warning("  Module " + name + " not found.")
   
  def setInactive(self, name, current=None):
    found = False
    for i in Modules:
      if (i.name == name) and i.isSensor() != True:
        if i.active == True:
          print txt.warning("  Desactivating module " + i.name + "...")
        i.setInactive()
        found = True
        break
      if (i.name == name) and i.isSensor() == True:
        print txt.warning("  Impossible to desactivate " + i.name + "...")
        found = True
        break
    if found == False:
      print txt.warning("  Module " + name + " not found.")
      
      
  def isSensor(self, name, current=None):
    for i in Modules:
      if (i.name == name) and i.isSensor() != True:
        return False
      if (i.name == name) and i.isSensor() == True:
        return True

   
  def addModule (self, name, code, mtype, current=None):
    if mtype == "Lamp":
      Modules.append(Mod(name, code, mtype))
    else:
      Modules.append(Mod(name, code, mtype, False))
    print txt.warning("  Module " + name + " (" + code + ") added.")
    
  def delModule (self, name, current=None):
    for i in Modules:
      if i.name == name:
        print txt.warning("  Deleting " + i.code + " with name " + i.name)
        Modules.remove(i)
        break
        
  def delModulebyCode (self, code, current=None):
    for i in Modules:
      if i.code == code:
        print txt.warning("  Deleting " + i.code + " with name " + i.name)
        Modules.remove(i)
        break
    
  def changeNamebyCode(self, name, code, current=None):
    for i in Modules:
      if i.code == code:
        print txt.warning("  Changing " + i.code + " name to " + name)
        i.setName(name)
        break
  
  def changeName(self, newname, name, current=None):
    for i in Modules:
      if i.name == name:
        i.setName(newname)
        break
  
  def isActivebyCode(self, code, current=None):
    for i in Modules:
      if i.code == code:
        return i.active
  
  def isActive(self, name, current=None):
    for i in Modules:
      if i.name == name:
        return i.active
  
   

  def checkSensor (self, current=None):
    sys.stdout.write(txt.warning("Monitoring sensor modules...\t"))
    sys.stdout.flush()
    p = subprocess.Popen("sudo heyu monitor", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    print txt.bold(txt.green("Running"))
    while True:
      if status == 1:
        break
      out = p.stdout.readline()
      if out.find("rcvi addr unit") != -1:
        mcode = out[44:46]
        out = p.stdout.readline()
        for i in Modules:
          found = False
          if i.code == mcode and i.isSensor:
            found = True
            if out.find("rcvi func           On : hc") != -1:
              print txt.warning("  Module '" + txt.bold(i.name)) + txt.warning("' has been activated.")
              i.setActive()
              break
            if out.find("rcvi func          Off : hc") != -1:
              print txt.warning("  Module '" + txt.bold(i.name)) + txt.warning("' has been deactivated.")
              i.setInactive()
              break
        if found == False:
          print txt.warning("  Recognised module not added before. Now added as noName.")
          if out.find("rcvi func           On : hc") != -1:
            self.addModule("noName", mcode, "Unknown", True)  
          if out.find("rcvi func          Off : hc") != -1:
            self.addModule("noName", mcode, "Unknown", False)  
          for i in Modules:
            if i.code == mcode and i.isSensor:
              if out.find("rcvi func           On : hc") != -1:
                print txt.warning("  Module '" + txt.bold(i.name)) + txt.warning("' has been activated.")
                i.setActive()
                break
              if out.find("rcvi func          Off : hc") != -1:
                print txt.warning("  Module '" + txt.bold(i.name)) + txt.warning("' has been deactivated.")
                i.setInactive()
                break
    
    

        
        
def checkModules(props):
  sys.stdout.write(txt.warning("Loading environment...\t\t"))
  sys.stdout.flush()
  for i in range(1,17):
    if "x10server.HouseModule." + str(i) + ".name" in props:
      if props["x10server.HouseModule." + str(i) + ".type"] == "Lamp":
        Modules.append(Mod(props["x10server.HouseModule." + str(i) + ".name"], props["x10server.HouseCode"] + str(i) , props["x10server.HouseModule." + str(i) + ".type"]))
      else:
        Modules.append(Mod(props["x10server.HouseModule." + str(i) + ".name"], props["x10server.HouseCode"] + str(i) , props["x10server.HouseModule." + str(i) + ".type"], False))
  print txt.bold(txt.green("Done"))

txt = Colors()
status = -1
ic = None

## Initialize HEYU system
sys.stdout.write(txt.warning("Initializing x10 system...\t"))
sys.stdout.flush()
proc = subprocess.Popen("sudo heyu start", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
(out, err) = proc.communicate()

try:
    ic = Ice.initialize(sys.argv)
    adapter = ic.createObjectAdapterWithEndpoints("NetAdapter", ic.getProperties().getProperty("x10server.Endpoints"))
    if err != "":
      print txt.bold(txt.fail("Failed"))
      print txt.fail("Can't open tty line.  Check the permissions.")
      status = 1
      sys.exit(status)
    else:
      print txt.bold(txt.green("Done"))
    status = 0
    
    props = ic.getProperties().getPropertiesForPrefix("x10server")
    checkModules(props)
    
    object = NetI()
    adapter.add(object, ic.stringToIdentity("Net"))
    adapter.activate()
    
    sys.stdout.write(txt.warning("Listening client request...\t"))
    sys.stdout.flush()
    print txt.bold(txt.green("Running"))
    
    thread = Thread(target = object.checkSensor)
    thread.start()
    
    ic.waitForShutdown()
except:
    if status == -1:
      print txt.bold(txt.fail("Failed"))
      print txt.fail("Address already in use")
      sys.exit(status = 1)
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
