import os

class Mod:
  name = ""
  code = ""
  mtype = ""
  active = True
  alarm_act = False
  alarm_start = "00:00"
  alarm_end = "23:55"
  mail_alert = False
  rules = list()
  
  def __init__(self, name, code, mtype, active=True):
    self.name = name
    self.code = code
    self.mtype = mtype
    self.active = active
    self.rules = list()
    #if self.isSensor():
    #  self.active = False
  
  def __str__(self):
    return self.name + "\t\t" + self.code + "\t\t" + self.mtype + "\t\t" + str(self.active)
    
  def setName (self, name):
    self.name = name
    
  def setActive (self):
    self.active = True
    os.system("sudo heyu on " + self.code)
  
  def setInactive (self):
    self.active = False
    os.system("sudo heyu off " + self.code)
    
  def isSensor (self):
    if self.mtype == "Motion" or self.mtype == "Unknown":
      return True
    else:
      return False
      
  def compare (self, mod):
    if mod.name == self.name and mod.code == self.code and mod.mtype == self.mtype and mod.active == self.active:
      return True
    else:
      return False
      
  def setcfgAlarm(self, sh,sm,eh,em, act):
    self.alarm_act = act
    self.alarm_start = str(sh).zfill(2) + ":" + str(sm).zfill(2)
    self.alarm_end = str(eh).zfill(2) + ":" + str(em).zfill(2)
    
  def getcfgAlarm(self):
    return [self.alarm_act, self.alarm_start[0:2], self.alarm_start[3:5], self.alarm_end[0:2], self.alarm_end[3:5]]
    

  def setRules(self,mystate,yourstate,action): 
    self.rules.append(mystate +"|"+yourstate+"|"+action)

  def getRules(self):
    return self.rules

  def delRules(self, i):
    del self.rules[i]
