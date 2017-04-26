#!/usr/bin/python

from gi.repository import Gtk,GObject,Gdk,GLib,GdkPixbuf
from Mod import Mod
import sys, traceback, Ice
import x10
from Colors import Colors
from threading import Thread, Timer
import threading
import cv2
import cv
import sys
import cairo
import jderobot
import numpy
import Image
import Temp
import time, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import cStringIO




class viewGUI:

  Modus = []
  x10 = ["", ""]
  Camera = [["",""]]
  Kinect = [["",""]]
  nCam = 0
  nKinect = 0
  KinectRun = False
  Temperature = ["",""]
  CameraRun = False
  motion = False
  motionKin = False
  record_rdy1 = False
  record_rdy2 = False
  record = False
  temprun = False
  temp_celsius = True
  temp_rules = []
  x10_on = False


  def __init__(self, propsx10 = None, propscam= None, propstmp= None, propskin= None, propsoth=None):
    self.builder = Gtk.Builder()
    self.builder.add_from_file("HomeGuardian.glade")
    self.builder.connect_signals(self)
    self.window = self.builder.get_object("window1")
    self.window.connect("delete-event", Gtk.main_quit)
    style_provider = Gtk.CssProvider()

    css = """#Active {background: #04B404;}#NoActive {background: #B40404;}"""

    style_provider.load_from_data(css)

    Gtk.StyleContext.add_provider_for_screen(
      Gdk.Screen.get_default(), 
      style_provider,     
      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    

      
    self.notebook = Gtk.Notebook()
    self.window.add(self.notebook)
    
    self.load_other()    
    if propsoth:
      self.checkOthers(propsoth)
    
    
      
    self.cameratab()
    
    if propscam:
      self.checkCamera(propscam)
    
    self.kinecttab()
    
    if propskin:
      self.checkKinect(propskin)

    
    
    
      
    
    
    if propsx10:
      self.checkModules(propsx10)
             
      self.environment()
      self.notebook.append_page(self.maingrid, Gtk.Label("Environment"))
      
      threading.Thread(target=self.askdformods).start()
      threading.Thread(target=self.checkAlarm).start()
      
      #self.maingrid.show_all()
    else: 
      self.load_environment()
      self.notebook.append_page(self.vbox2, Gtk.Label("Environment"))
    
    
    if propstmp:
      self.checkTempcfg(propstmp)
    

    self.notebook.append_page(self.vbox, Gtk.Label("Camera"))
    self.notebook.append_page(self.vboxkinect, Gtk.Label("Kinect"))
    self.notebook.append_page(self.vbox3, Gtk.Label("Configuration"))
    
    #threading.Thread(target=self.askdformods).start()
    #threading.Thread(target=self.checkAlarm).start()
    
    #self.send_mail() #continuar por aqui
    self.window.show_all()
    self.on_camrun()
    self.on_kinrun()
    
  def do_tmprule (self, tin, tout):
    partes = self.parseRules("|".join(self.temp_rules))
    for n in range(len(partes)/4):
      if partes[4*n] == "T int <":
        if tin < float(partes[4*n+1]):
          if partes[4*n+3] == "Activate":
            if not self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setActive(partes[4*n+2].split(" ")[1])
          else: 
            if self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setInactive(partes[4*n+2].split(" ")[1])
      elif partes[4*n] == "T int >":
        if tin > float(partes[4*n+1]): 
          if partes[4*n+3] == "Activate":
            if not self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setActive(partes[4*n+2].split(" ")[1])
          else: 
            if self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setInactive(partes[4*n+2].split(" ")[1])
      elif partes[4*n] == "T ext <":
        if tout < float(partes[4*n+1]):
          if partes[4*n+3] == "Activate":
            if not self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setActive(partes[4*n+2].split(" ")[1])
          else: 
            if self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setInactive(partes[4*n+2].split(" ")[1])
      elif partes[4*n] == "T ext >":
        if tout > float(partes[4*n+1]):
          if partes[4*n+3] == "Activate":
            if not self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setActive(partes[4*n+2].split(" ")[1])
          else: 
            if self.net.isActive(partes[4*n+2].split(" ")[1]):
              self.net.setInactive(partes[4*n+2].split(" ")[1])
          
    
  
  def del_tmprule (self, rule):
    del self.temp_rules[rule]
    
  def add_tmprule (self, moreless, t, act, do):
    self.temp_rules.append(moreless + "|" + "{0:.2f}".format(t) + "|" + act + "|" + do)
    
  def send_mail(self, sensor, imagen=None):
    
    msg = MIMEMultipart()
    msg['Subject'] = 'Security Alarm System'
    msg['From'] = 'Security@AlarmSystem.com'
    msg['To'] = self.mailother.get_text()

    text = MIMEText("Alert Information \n Sensor: " + sensor + "\n Time: " + str(datetime.now()))
    msg.attach(text)
    if imagen != None:
      no = 0
      for img in imagen:
        no += 1
        img.add_header('Content-ID', '<image'+str(no)+'>')
        msg.attach(img)

    s = smtplib.SMTP("smtpcorp.com", 2525)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("javiolo91@hotmail.com", "prueba")
    s.sendmail(msg['From'], msg['To'].split(","), msg.as_string())
    s.quit()
    
  def load_other(self):
    self.vbox3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
    self.vbox3.pack_start(Gtk.Label("Save cfg to file:"), False, False, 0)
    self.hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
    self.vbox3.pack_start(self.hbox2, False, False, 0)
    
    
    self.fileother = Gtk.Entry()
    self.fileother.set_text("security.cfg")
    image = Gtk.Image(stock=Gtk.STOCK_SAVE_AS)
    self.otheropt = Gtk.Button(label=" Save", image=image)
    self.otheropt.connect("clicked", self.save_config)
    self.hbox2.pack_start(self.fileother, True, False, 0)
    self.hbox2.pack_start(self.otheropt, True, False, 0)
    
    self.vbox3.pack_start(Gtk.Separator(), False, False, 5)
    
    self.hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
    self.vbox3.pack_start(self.hbox3, False, False, 0)
    mailtip = Gtk.Label()
    mailtip.set_markup("<small>Separate mails using ','</small>")
    self.vbox3.pack_start(mailtip, False, False, 0)
    
    self.mailother = Gtk.Entry()
    self.mailother.set_text("javiolo91@hotmail.com")
    self.hbox3.pack_start(Gtk.Label("E-mail: "), True, False, 0)
    self.hbox3.pack_start(self.mailother, True, False, 0)
    
    self.hbox4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
    self.vbox3.pack_start(self.hbox4, False, False, 0)
    self.mailtime = Gtk.Entry()
    self.mailtime.set_text("300")
    self.hbox4.pack_start(Gtk.Label("E-Mail interval (s): "), True, False, 0)
    self.hbox4.pack_start(self.mailtime, True, False, 0)
    
    self.hbox5 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
    self.vbox3.pack_start(self.hbox5, False, False, 0)
    self.resolution = Gtk.ComboBoxText()
    self.resolution.remove_all()
    self.resolution.append_text("160x120")
    self.resolution.append_text("320x240")
    self.resolution.append_text("640x480")
    self.resolution.set_active(1)
    self.hbox5.pack_start(Gtk.Label("Image Resolution: "), True, False, 0)
    self.hbox5.pack_start(self.resolution, True, False, 0)
    
  def save_config (self, button):
    f = open (self.fileother.get_text(), "w")
    if self.x10[0] != "" and self.x10[1] != 0:
      f.write("# X10 Environment configuration \n")
      f.write("x10.Proxy=Net:default -h "+self.x10[0]+" -p " + self.x10[1] +"\n")
      f.write("\n")
      for i in self.Modus:
        f.write("x10.Module."+i.code+".name="+  i.name +"\n")
        f.write("x10.Module."+i.code+".type="+  i.mtype +"\n")
        f.write("x10.Module."+i.code+".active="+  str(i.active) +"\n")
        f.write("x10.Module."+i.code+".alarm_act="+  str(i.alarm_act) +"\n")
        f.write("x10.Module."+i.code+".alarm_start="+  i.alarm_start +"\n")
        f.write("x10.Module."+i.code+".alarm_end="+  i.alarm_end +"\n")
        f.write("x10.Module."+i.code+".mail_alert="+  str(i.mail_alert) +"\n")
        a = 0
        first = True
        for n in i.rules:
          if first == True:
            f.write("x10.Module."+i.code+".rules="+ str(len(i.rules))+"\n")
            first = False
          f.write("x10.Module."+i.code+".rules."+str(a)+"="+ n+"\n")
          a += 1
        f.write("\n")
    if len(self.Camera) > 1:
      f.write("# Camera configuration \n")
      f.write("cam.sensors="+str(len(self.Camera)-1)+"\n")
      c = 0 
      for n in self.Camera:
        if c != 0:
          f.write("cam."+ str(c)+".Proxy=CameraA:default -h "+n[0]+" -p " + n[1] +"\n")
        c = c + 1
        
      f.write("\n")
    if self.Temperature[0] != "" and self.Temperature[1] != 0:
      f.write("# Temperature configuration \n")
      f.write("tmp.Proxy=Temperature:default -h "+self.Temperature[0]+" -p " + self.Temperature[1] +"\n")
      f.write("tmp.use_Celsius=" + str(self.temp_celsius) +"\n")
      b=0
      first = True
      for y in self.temp_rules:
        if first == True:
            f.write("tmp.rules="+ str(len(self.temp_rules))+"\n")
            first = False
        f.write("tmp.rules."+ str(b) +"=" + y +"\n")
        b+=1
      f.write("\n")
      
    if len(self.Kinect) > 1:
      f.write("# Kinect configuration \n")
      f.write("kin.sensors="+str(len(self.Kinect)-1)+"\n")
      c = 0 
      for n in self.Kinect:
        if c != 0:
          f.write("kin."+ str(c)+".Proxy=default -h "+n[0]+" -p " + n[1] +"\n")
        c = c + 1
        
      f.write("\n")
      
    if len(self.Kinect) > 1:
      f.write("# Other configuration \n")
      f.write("oth.mailadress="+self.mailother.get_text()+"\n")
      f.write("oth.secondsint="+self.mailtime.get_text()+"\n")
      f.write("oth.resolution="+self.resolution.get_active_text()+"\n")  
      f.write("\n")
    f.close()


  def load_environment (self):
    self.vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.vboxenv = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    
    image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
    self.envopt = Gtk.Button(label=" x10 Properties", image=image)
    self.envopt.connect("clicked", self.cameracfg, "env")
    image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
    self.tmpopt = Gtk.Button(label=" Tmp Properties", image=image)
    self.tmpopt.connect("clicked", self.cameracfg, "tmp")
    self.vbox2.pack_start(self.tmpopt, True, False, 0)
    self.vbox2.pack_start(self.envopt, True, False, 0)
    self.vbox2.pack_start(self.vboxenv, True, False, 0)
    
  def on_camrun (self):
    if self.CameraRun == False or self.nCam == 0:
      self.motiontable.hide()
      self.motiontable2.hide() 
      self.labelmt.hide()
      self.ad.hide()
      self.motion = False
      self.radbut3.set_active(True)
      self.ad.set_active(False)
    else:
      self.motiontable2.show() 
      self.labelmt.show()
      self.ad.show()
      self.radbut3.set_active(True)
      if self.motion == False:
        self.motiontable.hide()
      
  def on_kinrun (self):
    if self.KinectRun == False or self.nKinect == 0:
      self.motiontablekinect.hide()
      #self.motiontable2.hide() 
      self.labelmtkin.hide()
      self.adkinect.hide()
      self.motionKin = False
      #self.radbut3.set_active(True)
      self.adkinect.set_active(False)
    else:
      self.labelmtkin.show()
      self.adkinect.show()
      if self.motionKin == False:
        self.motiontablekinect.hide()
      #self.radbut3.set_active(True)

  def kinecttab (self):
    self.vboxkinect = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.vboxkinectcams = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
    self.vboxkinect.pack_start(self.vboxkinectcams, True, False, 0)

    image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
    self.kinectopt = Gtk.Button(label=" Add Kinect Sensor", image=image)
    self.kinectopt.connect("clicked", self.cameracfg, "kin")
    self.vboxkinect.pack_start(self.kinectopt, True, False, 0)
    
    self.hboxkinect = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    self.vboxkinect.pack_start(self.hboxkinect, True, False, 0)
    
    
    self.labelmtkin = Gtk.Label("Motion detection ")
    self.hboxkinect.pack_start(self.labelmtkin, True, True, 0)
    self.adkinect = Gtk.Switch()
    self.adkinect.connect("button-press-event", self.on_motionkinect)
    self.adkinect.set_active(False)
    self.hboxkinect.pack_start(self.adkinect, True, True, 0)
    
    self.motiontablekinect = Gtk.Table(6, 3, True)
    self.motiontablekinect.attach(Gtk.Label(""), 0, 1, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontablekinect.attach(Gtk.Label(""), 0, 1, 2, 3,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontablekinect.attach(Gtk.Label("Objects in motion:"), 0, 1, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    self.kinpeoplecounter = Gtk.Label("0")
    self.motiontablekinect.attach(self.kinpeoplecounter, 1, 2, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    self.checkbutkin = Gtk.CheckButton(label="Send Mail when motion")
    self.motiontablekinect.attach(self.checkbutkin, 0, 1, 5, 6,yoptions=Gtk.AttachOptions.SHRINK)
    
    self.combomotionkinect = Gtk.ComboBoxText()
    self.load_actuator_combotext(self.combomotionkinect)
    self.checkbutkinAct = Gtk.CheckButton(label="When motion")
    self.combomotionkinectAct = Gtk.ComboBoxText()
    self.combomotionkinectAct.append_text("Activate")
    self.combomotionkinectAct.append_text("Deactivate")
    self.combomotionkinectAct.set_active(0)
    self.motiontablekinect.attach(self.checkbutkinAct, 0, 1, 3, 4,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontablekinect.attach(self.combomotionkinectAct, 1, 2, 3, 4,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontablekinect.attach(self.combomotionkinect, 2, 3, 3, 4,yoptions=Gtk.AttachOptions.SHRINK) 
    
    self.combomotionkinect2 = Gtk.ComboBoxText()
    self.load_actuator_combotext(self.combomotionkinect2)
    self.checkbutkinAct2 = Gtk.CheckButton(label="When motion")
    self.combomotionkinectAct2 = Gtk.ComboBoxText()
    self.combomotionkinectAct2.append_text("Activate")
    self.combomotionkinectAct2.append_text("Deactivate")
    self.combomotionkinectAct2.set_active(0)
    self.motiontablekinect.attach(self.checkbutkinAct2, 0, 1, 4, 5,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontablekinect.attach(self.combomotionkinectAct2, 1, 2, 4, 5,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontablekinect.attach(self.combomotionkinect2, 2, 3, 4, 5,yoptions=Gtk.AttachOptions.SHRINK) 
    
    self.vboxkinect.pack_start(self.motiontablekinect, True, True, 0)
    
  def cameratab (self):
    self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    self.hboxcams = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
    self.vbox.pack_start(self.hboxcams, True, False, 0)
    

    image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
    self.camopt = Gtk.Button(label=" Add Camera Sensor", image=image)
    self.camopt.connect("clicked", self.cameracfg, "cam")
    self.vbox.pack_start(self.camopt, True, False, 0)
    
    
    
    self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    self.vbox.pack_start(self.hbox, True, False, 0)
    
    
    self.labelmt = Gtk.Label("Motion detection ")
    self.hbox.pack_start(self.labelmt, True, True, 0)
    self.ad = Gtk.Switch()
    self.ad.connect("button-press-event", self.on_motion)
    self.ad.set_active(False)
    self.hbox.pack_start(self.ad, True, True, 0)
    
    self.radbut3 = Gtk.RadioButton(group=None,label="No record")
    
    
    #self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    self.motiontable = Gtk.Table(6, 3, True)
    self.motiontable.attach(Gtk.Label(""), 0, 1, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(Gtk.Label(""), 0, 1, 2, 3,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(Gtk.Label("Objects in motion:"), 0, 1, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    self.campeoplecounter = Gtk.Label("0")
    self.motiontable.attach(self.campeoplecounter, 1, 2, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    self.checkbut = Gtk.CheckButton(label="Send Mail when motion")
    self.motiontable.attach(self.checkbut, 0, 1, 3, 4,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(Gtk.Label("Record options"), 0, 1, 4, 5,yoptions=Gtk.AttachOptions.SHRINK)
    self.radbut1 = Gtk.RadioButton(group=self.radbut3,label="Record when motion of")
    self.motiontable.attach(self.radbut1, 0, 1, 5, 6,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(Gtk.Label("Camera"), 1, 2, 5, 6,yoptions=Gtk.AttachOptions.SHRINK)
    self.vbox.pack_start(self.motiontable, True, True, 0)
    
    
    self.combomotioncam = Gtk.ComboBoxText()
    self.load_actuator_combotext(self.combomotioncam)
    self.checkbutcamAct = Gtk.CheckButton(label="When motion")
    self.combomotioncamAct = Gtk.ComboBoxText()
    self.combomotioncamAct.append_text("Activate")
    self.combomotioncamAct.append_text("Deactivate")
    self.combomotioncamAct.set_active(0)
    self.motiontable.attach(self.checkbutcamAct, 0, 1, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(self.combomotioncamAct, 1, 2, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(self.combomotioncam, 2, 3, 1, 2,yoptions=Gtk.AttachOptions.SHRINK) 
    
    self.combomotioncam2 = Gtk.ComboBoxText()
    self.load_actuator_combotext(self.combomotioncam2)
    self.checkbutcamAct2 = Gtk.CheckButton(label="When motion")
    self.combomotioncamAct2 = Gtk.ComboBoxText()
    self.combomotioncamAct2.append_text("Activate")
    self.combomotioncamAct2.append_text("Deactivate")
    self.combomotioncamAct2.set_active(0)
    self.motiontable.attach(self.checkbutcamAct2, 0, 1, 2, 3,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(self.combomotioncamAct2, 1, 2, 2, 3,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable.attach(self.combomotioncam2, 2, 3, 2, 3,yoptions=Gtk.AttachOptions.SHRINK) 
    
    
    
    self.motiontable2 = Gtk.Table(2, 2, False)
    self.radbut2 = Gtk.RadioButton(group=self.radbut3, label="Record when activation of")
    self.motiontable2.attach(self.radbut2, 0, 1, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    self.motiontable2.attach(self.radbut3, 0, 1, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    self.combomotion = Gtk.ComboBoxText()
    self.load_sensors_combotext(self.combomotion)
    self.motiontable2.attach(self.combomotion, 1, 2, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)  
    self.vbox.pack_start(self.motiontable2, True, True, 0)
   
    self.radbut1.connect("toggled", self.motionrec_tog, 1)
    self.radbut2.connect("toggled", self.motionrec_tog, 2)
    self.radbut3.connect("toggled", self.motionrec_tog, 3)
    
  def load_sensors_combotext(self, widget):
    actual = widget.get_active_text()
    widget.remove_all()
    n = 0
    m = -1
    for i in self.Modus:
      if i.isSensor():
        widget.append_text("("+i.code+") "+i.name)
        if actual == "("+i.code+") "+i.name:
          m = n
        n += 1
    if m == -1:
      widget.set_active(0)
    else:
      widget.set_active(m)
    
  def load_actuator_combotext(self, widget):
    actual = widget.get_active_text()
    widget.remove_all()
    n = 0
    m = -1
    for i in self.Modus:
      if not i.isSensor():
        widget.append_text("("+i.code+") "+i.name)
        if actual == "("+i.code+") "+i.name:
          m = n
        n += 1
    if m == -1:
      widget.set_active(0)
    else:
      widget.set_active(m)
  
  def motionrec_tog (self, button, n):
    if n == 1:
      self.record_rdy1 = True
      self.record_rdy2 = False
    if n == 2:
      self.record_rdy2 = True
      self.record_rdy1 = False
    if n == 3:
      self.record_rdy1 = False
      self.record_rdy2 = False
      self.record = False
    

  def on_motion (self, button, event):
    if self.motion == False:
      self.motion = True
      self.load_actuator_combotext(self.combomotioncam)
      self.load_actuator_combotext(self.combomotioncam2)
      self.motiontable.show() 
    else:
      self.motion = False
      self.motiontable.hide() 
      self.radbut3.set_active(True)
      
  def on_motionkinect (self, button, event):
    if self.motionKin == False:
      self.motionKin = True
      self.load_actuator_combotext(self.combomotionkinect)
      self.load_actuator_combotext(self.combomotionkinect2)
      self.motiontablekinect.show() 
    else:
      self.motionKin = False
      self.motiontablekinect.hide() 
      #self.radbut3.set_active(True)
    
  def cameracfg (self, button, tab):
    self.window6 = self.builder.get_object("dialog5")
    self.window6.connect("delete_event", self.on_button10_clicked)
    if tab == "cam":
      self.builder.get_object("entry4").set_text(self.Camera[0][0])
      self.builder.get_object("entry5").set_text(self.Camera[0][1])
    elif tab == "kin":
      self.builder.get_object("entry4").set_text(self.Kinect[0][0])
      self.builder.get_object("entry5").set_text(self.Kinect[0][1])
    elif tab == "env":
      self.builder.get_object("entry4").set_text(self.x10[0])
      self.builder.get_object("entry5").set_text(self.x10[1])
    elif tab == "tmp" or tab == "tmp2":
      self.builder.get_object("entry4").set_text(self.Temperature[0])
      self.builder.get_object("entry5").set_text(self.Temperature[1])
    self.lastsignal0 = self.builder.get_object("button11").connect("clicked", self.on_button11_clicked, tab)
    self.window6.show_all()
 


  def play_kinectRGB (self, kinectRGB, hboxkinectcams):  
    def resolution (n = None):
      if self.resolution.get_active_text() == "160x120":
        if n == None:
          return (160,120)
        elif n == 0:
          return 160
        else:
          return 120
      elif self.resolution.get_active_text() == "320x240":
        if n == None:
          return (320,240)
        elif n == 0:
          return 320
        else:
          return 240
      else: 
        if n == None:
          return (640,480)
        elif n == 0:
          return 640
        else:
          return 480
    try:
      obj2 = ic.stringToProxy('cameraRGB:default -h '+self.Kinect[self.nKinect][0]+' -p ' + self.Kinect[self.nKinect][1])
      kin = jderobot.CameraPrx.checkedCast(obj2)
    except:
      print "KinectRGB: Connection Failed"
      return
    
    formatRGB = kin.getImageFormat()[0]
    while True:
      if threads == False or self.KinectRun == False or not hboxkinectcams in self.vboxkinectcams:
        break
      data = kin.getImageData(formatRGB)
      pixbuf = GdkPixbuf.Pixbuf.new_from_data(data.pixelData, GdkPixbuf.Colorspace.RGB, False, 8, data.description.width,data.description.height, data.description.width*3,None, None)
      
      
      
      if resolution(0) != data.description.width:
        pixbuf = pixbuf.scale_simple(resolution(0), resolution(1), GdkPixbuf.InterpType.BILINEAR);
      Gdk.threads_enter()
      kinectRGB.clear()
      kinectRGB.set_from_pixbuf(pixbuf)
      Gdk.threads_leave()
        
        
        
  def play_kinectDepth (self, kinectDepth,hboxkinectcams, kinectRGB):
    def resolution (n = None):
      if self.resolution.get_active_text() == "160x120":
        if n == None:
          return (160,120)
        elif n == 0:
          return 160
        else:
          return 120
      elif self.resolution.get_active_text() == "320x240":
        if n == None:
          return (320,240)
        elif n == 0:
          return 320
        else:
          return 240
      else: 
        if n == None:
          return (640,480)
        elif n == 0:
          return 640
        else:
          return 480
    def RGB_to_depth (data, rgbObgr):
      img= Image.fromstring('RGB', (data.description.width,data.description.height), data.pixelData, 'raw', rgbObgr)
      pix = numpy.array(img)
      red = pix[:,:,2]
      green = pix[:,:,1]
      blue = pix[:,:,0]
      img = numpy.zeros((red.shape[0], red.shape[1], 3), dtype = red.dtype) 
      for n in range(3):
        img[:,:,n] = red
      return img
      
    try:
      obj2 = ic.stringToProxy('cameraDepth:default -h '+self.Kinect[self.nKinect][0]+' -p ' + self.Kinect[self.nKinect][1])
      kin = jderobot.CameraPrx.checkedCast(obj2)
    except:
      print "KinectDepth: Connection Failed"
      self.Kinect.pop()
      self.on_del_kinect(None, hboxkinectcams, None)
      return
    
    t_start_pic = time.time() - int(self.mailtime.get_text())
    formatDepth= kin.getImageFormat()[0]
    data = kin.getImageData(formatDepth)
      
    frame_size = (data.description.width,data.description.height)
    color_image = cv.CreateImage(frame_size, 8, 3)
    grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
    moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)
      
    ult_suma = 0
    first = True
    while True:
      if threads == False or self.KinectRun == False or not hboxkinectcams in self.vboxkinectcams:
        if self.motionKin == True:
          Gdk.threads_enter()
          self.kinpeoplecounter.set_markup("<b>"+str(int(self.kinpeoplecounter.get_text())-ult_suma)+"</b>")
          Gdk.threads_leave()
        break
        
      data = kin.getImageData(formatDepth)
      
      if self.motionKin == True:
        # motion
        datos = RGB_to_depth(data, "BGR")
        color_image = cv.fromarray(datos)
      
        # Smooth to get rid of false positives
        cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)

        if first:
          difference = color_image
          temp = color_image
          cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
          first = False
        else:
          cv.RunningAvg(color_image, moving_average, 0.030, None)

        # Convert the scale of the moving average.
        cv.ConvertScale(moving_average, temp, 1.0, 0.0)

        # Minus the current frame from the moving average.
        cv.AbsDiff(color_image, temp, difference)

        # Convert the image to grayscale.
        cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)

        # Convert the image to black and white.
        cv.Threshold(grey_image, grey_image, 70, 255, cv.CV_THRESH_BINARY)

        # Dilate and erode to get people blobs
        cv.Dilate(grey_image, grey_image, None, 18)
        cv.Erode(grey_image, grey_image, None, 10)

        storage = cv.CreateMemStorage(0)
        contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
        points = []
        
        n = 0
        while contour:
          n = n +1
          bound_rect = cv.BoundingRect(list(contour))
          contour = contour.h_next()

          pt1 = (bound_rect[0], bound_rect[1])
          pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
          points.append(pt1)
          points.append(pt2)
          if bound_rect[2] < 50 or bound_rect[3] <50:
            n = n -1
          else:
            cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(0,255,0), 1)
          
        color_image = cv2.resize(numpy.array(color_image), resolution())
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(Image.fromarray(color_image).tostring('raw'), GdkPixbuf.Colorspace.RGB, False, 8, resolution(0),resolution(1), resolution(0)*3,None, None)
        Gdk.threads_enter()
        self.kinpeoplecounter.set_markup("<b>"+str(int(self.kinpeoplecounter.get_text())+n-ult_suma)+"</b>")
        ult_suma = n
        kinectDepth.clear()
        kinectDepth.set_from_pixbuf(pixbuf)
        Gdk.threads_leave()
        
        Gdk.threads_enter()
        if self.checkbutkin.get_active() and n > 0:
          if time.time() - t_start_pic > int(self.mailtime.get_text()):
            t_start_pic = time.time()
            ima = Image.fromstring('RGB', (data.description.width,data.description.height), Image.fromarray(RGB_to_depth(data, "BGR")).tostring('raw'), 'raw', "RGB")
            outbuf = cStringIO.StringIO()
            ima.save(outbuf, format="PNG")
            my_mime_image = MIMEImage(outbuf.getvalue(), name="CaptureDepth_"+str(datetime.now()))
            
            ima2 = Image.fromstring('RGB', (data.description.width,data.description.height),kinectRGB.get_pixbuf().get_pixels(), 'raw', "RGB")
            outbuf2 = cStringIO.StringIO()
            ima2.save(outbuf2, format="PNG")
            my_mime_image2 = MIMEImage(outbuf2.getvalue(), name="CaptureRGB_"+str(datetime.now()))
            
            self.send_mail("Kinect", [my_mime_image,my_mime_image2])
        
        if n == 0:
          fir = True
            
        if n > 0 and fir == True:
          if self.checkbutkinAct.get_active():
            self.camera_act(self.combomotionkinectAct.get_active_text(), self.combomotionkinect.get_active_text())
          if self.checkbutkinAct2.get_active():
            self.camera_act(self.combomotionkinectAct2.get_active_text(), self.combomotionkinect2.get_active_text())
          fir = False
        Gdk.threads_leave()
        
      else:
        datos = Image.fromarray(RGB_to_depth(data, "BGR")).tostring('raw')
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(datos, GdkPixbuf.Colorspace.RGB, False, 8, data.description.width,data.description.height, data.description.width*3,None, None)
        if resolution(0) != data.description.width:
          pixbuf = pixbuf.scale_simple(resolution(0), resolution(1), GdkPixbuf.InterpType.BILINEAR);
        Gdk.threads_enter()
        kinectDepth.clear()
        kinectDepth.set_from_pixbuf(pixbuf)
        Gdk.threads_leave()
        

    
  def camera (self, camera, widget):
    def resolution (n = None):
      if self.resolution.get_active_text() == "160x120":
        if n == None:
          return (160,120)
        elif n == 0:
          return 160
        else:
          return 120
      elif self.resolution.get_active_text() == "320x240":
        if n == None:
          return (320,240)
        elif n == 0:
          return 320
        else:
          return 240
      else: 
        if n == None:
          return (640,480)
        elif n == 0:
          return 640
        else:
          return 480
    def data_to_image (data, rgbObgr):
      img= Image.fromstring('RGB', (data.description.width,data.description.height), data.pixelData, 'raw', rgbObgr)
      pix = numpy.array(img)
      return pix
    
    t_start_pic = time.time() - int(self.mailtime.get_text())
    
    try:
      #ic2 = Ice.initialize()    
      #obj2 = ic2.stringToProxy('cameraA:default -h '+self.Camera[0]+' -p ' + self.Camera[1])
      obj2 = ic.stringToProxy('cameraA:default -h '+self.Camera[self.nCam][0]+' -p ' + self.Camera[self.nCam][1])
      cam = jderobot.CameraPrx.checkedCast(obj2)
    except:
      print "Camera: Connection Failed"
      Gdk.threads_enter()
      self.Camera.pop()
      self.on_del_cam(None, widget, None)
      Gdk.threads_leave()
      return
    
    # motion
    hostport= self.Camera[self.nCam][0]+':' + self.Camera[self.nCam][1]
    formatcam= cam.getImageFormat()[0]
    data = cam.getImageData(formatcam)
      
    frame_size = (data.description.width,data.description.height)
    color_image = cv.CreateImage(frame_size, 8, 3)
    grey_image = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
    moving_average = cv.CreateImage(frame_size, cv.IPL_DEPTH_32F, 3)
    
    first = True
    first_rec = True
    first_zero = False
    ult_suma = 0
    
    
    while True:
      if threads == False or self.CameraRun == False or not widget in self.hboxcams:
        Gdk.threads_enter()
        self.kinpeoplecounter.set_markup("<b>"+str(int(self.kinpeoplecounter.get_text())-ult_suma)+"</b>")
        Gdk.threads_leave()
        break
      
      data = cam.getImageData(formatcam)
      if self.record == False:
        first_rec = True
      
      if first_rec == True and self.record == True:
        out = cv2.VideoWriter("Camera_" +hostport+"_"+datetime.now().ctime() + '.avi',cv2.cv.CV_FOURCC('X','V','I','D'), 10.0, frame_size)
        first_rec = False
        
      if self.motion == True:
        # motion
        imagen = data_to_image (data, "RGB")
        color_image = cv.fromarray(imagen)
      
        # Smooth to get rid of false positives
        cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)

        if first:
          difference = color_image
          temp = color_image
          cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
          first = False
        else:
          cv.RunningAvg(color_image, moving_average, 0.030, None)

        # Convert the scale of the moving average.
        cv.ConvertScale(moving_average, temp, 1.0, 0.0)

        # Minus the current frame from the moving average.
        cv.AbsDiff(color_image, temp, difference)

        # Convert the image to grayscale.
        cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)

        # Convert the image to black and white.
        cv.Threshold(grey_image, grey_image, 70, 255, cv.CV_THRESH_BINARY)

        # Dilate and erode to get people blobs
        cv.Dilate(grey_image, grey_image, None, 18)
        cv.Erode(grey_image, grey_image, None, 10)

        storage = cv.CreateMemStorage(0)
        contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
        points = []
        
        n = 0
        while contour:
          n = n +1
          bound_rect = cv.BoundingRect(list(contour))
          contour = contour.h_next()

          pt1 = (bound_rect[0], bound_rect[1])
          pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
          points.append(pt1)
          points.append(pt2)
          if bound_rect[2] < 50 or bound_rect[3] <50:
            n = n -1
          else:
            cv.Rectangle(color_image, pt1, pt2, cv.CV_RGB(0,255,0), 1)
          
        Gdk.threads_enter()
        if self.checkbut.get_active() and n > 0:
          if time.time() - t_start_pic > int(self.mailtime.get_text()):
            t_start_pic = time.time()
            ima = Image.fromstring('RGB', (data.description.width,data.description.height), data.pixelData, 'raw', "RGB")
            outbuf = cStringIO.StringIO()
            ima.save(outbuf, format="PNG")
            my_mime_image = MIMEImage(outbuf.getvalue(), name="Capture_"+str(datetime.now()))
            self.send_mail("Camera", [my_mime_image])
            
        if n == 0:
          fir = True
            
        if n > 0 and fir == True:
          if self.checkbutcamAct.get_active():
            self.camera_act(self.combomotioncamAct.get_active_text(), self.combomotioncam.get_active_text())
          if self.checkbutcamAct2.get_active():
            self.camera_act(self.combomotioncamAct2.get_active_text(), self.combomotioncam2.get_active_text())
          fir = False
        Gdk.threads_leave()

    
        
          

        if self.record_rdy1 and n > 0:
          self.record = True
          first_zero = True
          
        if first_rec == True and self.record == True:
          out = cv2.VideoWriter("Camera_" +hostport+"_"+datetime.now().ctime() + '.avi',cv2.cv.CV_FOURCC('X','V','I','D'), 10.0, frame_size)
          first_rec = False
          
        
        
          
        if self.record and n == 0 and first_zero:
          first_zero = False
          t_start = time.time()
        elif self.record and n == 0 and time.time() - t_start > 10:
          self.record = False
      
        if self.record:
          imagen2 = data_to_image (data, "BGR")
          out.write(imagen2)
        Gdk.threads_enter()
        self.campeoplecounter.set_markup("<b>"+str(int(self.campeoplecounter.get_text())+n-ult_suma)+"</b>")
        ult_suma = n
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(Image.fromarray(numpy.array(color_image)).tostring('raw'), GdkPixbuf.Colorspace.RGB, False, 8, data.description.width,data.description.height, data.description.width*3,None, None)
        if resolution(0) != data.description.width:
          pixbuf = pixbuf.scale_simple(resolution(0), resolution(1), GdkPixbuf.InterpType.BILINEAR);
        camera.clear()
        camera.set_from_pixbuf(pixbuf)
        Gdk.threads_leave()
        
        
      
      else:
        if self.record:
          imagen = data_to_image (data, "BGR")
          out.write(imagen)
        Gdk.threads_enter()
        pixbuf = GdkPixbuf.Pixbuf.new_from_data(data.pixelData, GdkPixbuf.Colorspace.RGB, False, 8, data.description.width,data.description.height, data.description.width*3,None, None)
        if resolution(0) != data.description.width:
          pixbuf = pixbuf.scale_simple(resolution(0), resolution(1), GdkPixbuf.InterpType.BILINEAR);
        camera.clear()
        camera.set_from_pixbuf(pixbuf)
        Gdk.threads_leave()
        
        

          
      
      
    #ic2.destroy()
  
  def setAlarm(self, name, sh, sm, eh, em, act):
    for i in self.Modus:
      if i.name == name:
        i.setcfgAlarm(sh,sm,eh,em,act)
        break
  
  
  def getAlarm(self, name):
    for i in self.Modus:
      if i.name == name:
        alarm = i.getcfgAlarm()
        return [alarm[0], int(alarm[1]), int(alarm[2])/5, int(alarm[3]),int(alarm[4])/5]



  def checkAlarm (self):
    while True:
      if threads == False:
        break
      now = datetime.now()
      t = str(now.hour).zfill(2)  + ":" + str(now.minute).zfill(2)
      for i in self.Modus:
        if i.alarm_act:
          if t == i.alarm_start:
            self.net.setActive(i.name)
          if t == i.alarm_end:
            self.net.setInactive(i.name)
      time.sleep(1) 
      
      
  def askdformods (self):
    while True:
      if threads == False:
        break
      newmod = self.parseMod(self.net.getEnvironment())
      if len(self.Modus) != len(newmod):
        Gdk.threads_enter()
        self.table.destroy()
        self.modtable()
        self.load_sensors_combotext(self.combomotion)
        self.load_actuator_combotext(self.combomotionkinect)
        self.load_actuator_combotext(self.combomotionkinect2)
        self.load_actuator_combotext(self.combomotioncam)
        self.load_actuator_combotext(self.combomotioncam2)
        Gdk.threads_leave()
      else:
        for i in self.Modus:
          for n in newmod:
            found = False
            if i.compare(n):
              found = True
              break
          if found == False:
            Gdk.threads_enter()
            self.table.destroy()
            self.modtable()
            self.load_sensors_combotext(self.combomotion)
            self.load_actuator_combotext(self.combomotionkinect)
            self.load_actuator_combotext(self.combomotionkinect2)
            self.load_actuator_combotext(self.combomotioncam)
            self.load_actuator_combotext(self.combomotioncam2)
            Gdk.threads_leave()
            break
              


  def parsemymods (self):
    rdymods = []
    for i in self.Modus:
      if i.isSensor() == False:
        rdymods.append("("+i.code+") "+i.name)

    return rdymods

  def parseRules (self, s): 
    pieces = []
    if s != "":
      pieces = s.split("|")
    return pieces
    
    
  def getRule(self, name):
    for i in self.Modus:
      if i.name == name:
        alarm = i.getRules()
        return "|".join(alarm)

  def setRule(self, name, SenState, selectMod, Action):
    for i in self.Modus:
      if i.name == name:
        i.setRules(SenState,selectMod,Action)
        break


  def delRule(self, name, rule):
    for i in self.Modus:
      if i.name == name:
        i.delRules(rule)
        break

  def doRules(self,name, state):
    for i in self.Modus:
      if i.name == name:
        rules = i.getRules()
        for r in rules:
          pieces = r.split("|")
          if pieces[0] == "On" and state == True:
            if pieces[2] == "Activate":
              for m in self.Modus:
                if m.name == pieces[1].split(")")[1][1:]:
                  self.net.setActive(m.name)
            else:
              for m in self.Modus:
                if m.name == pieces[1].split(")")[1][1:]:
                  self.net.setInactive(m.name)
          elif pieces[0] == "Off" and state == False:
            if pieces[2] == "Activate":
              for m in self.Modus:
                if m.name == pieces[1].split(")")[1][1:]:
                  self.net.setActive(m.name)
            else:
              for m in self.Modus:
                if m.name == pieces[1].split(")")[1][1:]:
                  self.net.setInactive(m.name)
                  
  def camera_act (self, do, to):
    if to != "":
      for n in self.Modus:
        if n.name == to.split(")")[1][1:]:
          if do == "Activate":
            if n.active == False:
              threading.Thread(target=self.net.setActive, args=[n.name]).start()
              
          else:
            if n.active == True:
              threading.Thread(target=self.net.setInactive, args=[n.name]).start()
          break
        
        


  def on_button9_clicked (self, button, mod):
    self.setRule(mod.name,self.builder.get_object("comboboxtext10").get_active_text(),self.combotextmodus.get_active_text(), self.builder.get_object("comboboxtext12").get_active_text())
    self.builder.get_object("label13").set_label("")
    self.window5.hide()
    self.change3.disconnect(self.lastsignal3)
    self.table2.destroy()
    self.rultable(mod)
    return True

  def on_delrul (self, button, mod, rule):
    self.delRule(mod.name, rule)
    self.table2.destroy()
    self.rultable(mod)
		

  def changerule (self, button, mod):
    self.window5 = self.builder.get_object("dialog4")
    self.builder.get_object("label21").set_label(mod.name)
    self.window5.connect("delete_event", self.on_button8_clicked)
    self.window5.show_all()
    self.change3 = self.builder.get_object("button9")
    self.lastsignal3 = self.change3.connect("clicked", self.on_button9_clicked, mod)
    self.combotextmodus = self.builder.get_object("comboboxtext11")
    self.builder.get_object("comboboxtext10").set_active(0)
    self.builder.get_object("comboboxtext11").set_active(0)
    self.builder.get_object("comboboxtext12").set_active(0)
    rdymods = self.parsemymods()
    self.combotextmodus.remove_all()
    for i in rdymods:
      self.combotextmodus.append_text(i)
    self.combotextmodus.set_active(0)


  def rultable (self, mod):
    rules = self.parseRules(self.getRule(mod.name))

    if len(rules) == 0:
      self.table2 = Gtk.Table(2, 4, False)
    else:
      self.table2 = Gtk.Table(len(rules)/3, 4, False)
    self.box5.pack_start(self.table2, True, True, 0)
    
    optionsLabel = Gtk.Label()
    optionsLabel.set_markup("<b>Del</b>")
    self.table2.attach(optionsLabel, 0, 1, 0, 1)
    
    codeLabel = Gtk.Label()
    codeLabel.set_markup("<b>State</b>")
    self.table2.attach(codeLabel, 1, 2, 0, 1)
    
    nameLabel = Gtk.Label()
    nameLabel.set_markup("<b>Module</b>")
    self.table2.attach(nameLabel, 2, 3, 0, 1)
    
    typeLabel = Gtk.Label()
    typeLabel.set_markup("<b>Action</b>")
    self.table2.attach(typeLabel, 3, 4, 0, 1)
    
    
    if len(rules) == 0:
      self.window3.show_all()
      return
    
    for i in range(len(rules)/3):
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_delrul, mod, i) 
      self.table2.attach(deletebutton, 0, 1, 3*i+1, 3*i+2)
      self.table2.attach(Gtk.Label(rules[3*i]), 1, 2, 3*i+1, 3*i+2)
      self.table2.attach(Gtk.Label(rules[3*i+1]), 2, 3, 3*i+1, 3*i+2)
      self.table2.attach(Gtk.Label(rules[3*i+2]), 3, 4, 3*i+1, 3*i+2)

    self.window3.show_all()

    
  def changename (self, button, mod):
    self.window3 = self.builder.get_object("dialog1")
    self.builder.get_object("entry1").set_text(mod.name)
    self.window3.connect("delete_event", self.on_button4_clicked)
    self.window3.show_all()
    self.change = self.builder.get_object("button5")
    self.box5 = self.builder.get_object("box5")
    self.lastsignal = self.change.connect("clicked", self.on_button5_clicked, mod)
    self.senalarm = self.builder.get_object("switch1")
    self.senalarm.set_active(mod.mail_alert)
    self.alertsignal = self.senalarm.connect("button-press-event", self.on_actAlert, mod)
    self.addrule = self.builder.get_object("button3")
    self.lastsignal4 = self.addrule.connect("clicked", self.changerule, mod)
    self.rultable(mod)
    
    
  def on_actAlert(self, button, mod):
    mod.mail_alert = self.senalarm.get_active()



  def changenamepro (self, button, mod):
    self.window4 = self.builder.get_object("dialog3")
    self.window4.show_all()
    self.builder.get_object("entry3").set_text(mod.name)
    self.window4.connect("delete_event", self.on_button1_clicked)
    self.change2 = self.builder.get_object("button2")
    self.lastsignal2 = self.change2.connect("clicked", self.on_button2_clicked, mod)
    self.toff = self.builder.get_object("radiobutton1")
    self.ton = self.builder.get_object("radiobutton2")
    self.starth = self.builder.get_object("comboboxtext3")
    self.startm = self.builder.get_object("comboboxtext4")
    self.endh = self.builder.get_object("comboboxtext5")
    self.endm = self.builder.get_object("comboboxtext6")
    # if no estaba programado antes
    alarm = self.getAlarm(mod.name)
    self.starth.set_active(alarm[1])
    self.startm.set_active(alarm[2])
    self.endh.set_active(alarm[3])
    self.endm.set_active(alarm[4])
    if alarm[0]:
      self.ton.set_active(True)
    else:
      self.toff.set_active(True)
    # else si lo estaba, valor dado
    
    
  def on_button1_clicked(self, button, event=None):
    self.builder.get_object("entry3").set_text("")
    self.window4.hide()
    self.change2.disconnect(self.lastsignal2)
    return True
    
  def on_button2_clicked(self, button, mod):
    name = self.builder.get_object("entry3").get_text()
    if mod.name != name:
      self.net.changeNamebyCode(name, mod.code)
    self.setAlarm(mod.name, self.starth.get_active_text(), self.startm.get_active_text(),self.endh.get_active_text(),self.endm.get_active_text(),self.ton.get_active())
    self.table.destroy()
    self.modtable()
    self.builder.get_object("entry3").set_text("")
    self.window4.hide()
    self.change2.disconnect(self.lastsignal2)
    
  def on_button4_clicked(self, button, event=None):
    self.builder.get_object("entry1").set_text("")
    self.window3.hide()
    self.change.disconnect(self.lastsignal)
    self.addrule.disconnect(self.lastsignal4)
    self.senalarm.disconnect(self.alertsignal)
    self.table2.destroy()
    return True

  def on_button8_clicked(self, button, event=None):
    self.builder.get_object("label13").set_label("")
    self.window5.hide()
    self.change3.disconnect(self.lastsignal3)
    return True
    
  def on_button10_clicked(self, button, event=None):
    self.builder.get_object("button11").disconnect(self.lastsignal0)
    self.radbut3.set_active(True)
    #self.CameraRun = False
    #self.KinectRun = False
    #self.motion = False
    self.window6.hide()
    self.on_camrun()
    self.on_kinrun()
    return True  
    
  def on_del_kinect (self, button, kinect, n): 
    if n != None:
      del self.Kinect[self.Kinect.index(n)]
    self.nKinect -= 1 
    self.on_kinrun()
    kinect.destroy()
  
  def on_del_cam (self, button, cam, n):
    if n != None:
      del self.Camera[self.Camera.index(n)] 
    self.nCam -= 1 
    self.on_camrun()
    cam.destroy()


  def on_button11_clicked(self, button, tab):
    self.builder.get_object("button11").disconnect(self.lastsignal0)
    if tab == "cam":
      self.CameraRun = False
      self.window6.hide()
      host = self.builder.get_object("entry4").get_text()
      port = self.builder.get_object("entry5").get_text()
      self.Camera.append([host,port])
      
      
      hboxcams = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
      self.hboxcams.pack_start(hboxcams, True, False, 0)
      cam=Gtk.Image()
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_del_cam, hboxcams, [host,port])
      hboxcams.pack_start(cam, True, False, 0)
      hboxcams.pack_start(deletebutton, True, False, 0)
      hboxcams.show_all()
      
      if self.CameraRun == False:
        self.CameraRun = True
        self.nCam += 1
        self.on_camrun()
        self.radbut3.set_active(True)
        threading.Thread(target=self.camera, args=[cam,hboxcams]).start()
    elif tab == "kin":
          
      self.KinectRun = False
      self.window6.hide()
      host = self.builder.get_object("entry4").get_text()
      port = self.builder.get_object("entry5").get_text()
      self.Kinect.append([host,port])
      
      
      hboxkinectcams = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
      self.vboxkinectcams.pack_start(hboxkinectcams, True, False, 0)
      kinectRGB=Gtk.Image()
      kinectDepth=Gtk.Image()
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_del_kinect, hboxkinectcams, [host,port])
      hboxkinectcams.pack_start(deletebutton, True, False, 0)
      hboxkinectcams.pack_start(kinectRGB, True, False, 0)
      hboxkinectcams.pack_start(kinectDepth, True, False, 0)
      hboxkinectcams.show_all()
      
      if self.KinectRun == False:
        self.KinectRun = True
        self.nKinect += 1
        self.on_kinrun()
        #self.radbut3.set_active(True)
        threading.Thread(target=self.play_kinectRGB, args=[kinectRGB,hboxkinectcams]).start()
        threading.Thread(target=self.play_kinectDepth, args=[kinectDepth,hboxkinectcams,kinectRGB]).start()
        

    elif tab == "tmp" or tab == "tmp2":
      self.window6.hide()
      self.Temperature[0] = self.builder.get_object("entry4").get_text()
      self.Temperature[1] = self.builder.get_object("entry5").get_text()
      try:
        basetmp = ic.stringToProxy('Temperature:default -h '+self.Temperature[0]+' -p ' + self.Temperature[1])
        self.tmp = Temp.TemperaturePrx.checkedCast(basetmp)
      except:
        print "Temperature: Connection Failed"
        #ic.destroy()
        return
      self.temprun = True
      self.tmpopt.destroy()
      self.tmpShow = Gtk.Label()
      if tab == "tmp":
        
        image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
        self.tmpcfg = Gtk.Button(label=" Temp Properties", image=image)
        self.tmpcfg.connect("clicked", self.temperaturecfg)
        self.vboxenv.pack_end(self.tmpcfg, True, False, 0)
        self.vboxenv.pack_end(self.tmpShow, True, False, 0)
        self.vboxenv.show_all()
      else:
        self.maingrid.attach(self.tmpShow, 0, 1, 2, 3,yoptions=Gtk.AttachOptions.SHRINK)
        image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
        self.tmpcfg = Gtk.Button(label=" Temp Properties", image=image)
        self.tmpcfg.connect("clicked", self.temperaturecfg)
        self.maingrid.attach(self.tmpcfg, 0, 1, 3, 4,yoptions=Gtk.AttachOptions.SHRINK)
        self.maingrid.show_all()
      threading.Thread(target=self.checkTemperature).start()
      # continuar
        

    elif tab == "env":
      self.window6.hide()
      self.x10[0] = self.builder.get_object("entry4").get_text()
      self.x10[1] = self.builder.get_object("entry5").get_text()
      try:
        #ic = Ice.initialize()
        #base = ic.stringToProxy(ic.getProperties().getProperty("x10view.Proxy"))
        base = ic.stringToProxy('Net:default -h '+self.x10[0]+' -p ' + self.x10[1])
        self.net = x10.NetPrx.checkedCast(base)
      except:
        print "X10: Connection Failed"
        #ic.destroy()
        return
        
      self.envopt.destroy()
      self.x10_on = True
      self.environment()
      self.vboxenv.pack_start(self.maingrid, False, False, 0)
      self.vboxenv.show_all()
      
      threading.Thread(target=self.askdformods).start()
      threading.Thread(target=self.checkAlarm).start()
      self.maingrid.show_all()
  
  def temperaturecfg (self, button):
    self.window7 = self.builder.get_object("dialog6")
    self.window7.connect("delete_event", self.on_button12_clicked)
    self.window7.show_all()
    self.tmpchange = self.builder.get_object("button13")
    self.lastsignaltmp = self.tmpchange.connect("clicked", self.on_button13_clicked)
    self.box9 = self.builder.get_object("box9")
    
    self.celsius = self.builder.get_object("switch2")
    self.celsius.set_active(self.temp_celsius)
    self.tmpsignal = self.celsius.connect("button-press-event", self.on_actCelsius)
    self.addrule_tmp = self.builder.get_object("button14")
    if self.x10_on:
      self.lastsignaltmp2 = self.addrule_tmp.connect("clicked", self.changerule_tmp)
    self.rultable_tmp()
    
  def on_button12_clicked(self, button, event= None):
    self.window7.hide()
    self.tmpchange.disconnect(self.lastsignaltmp)
    if self.x10_on:
      self.addrule_tmp.disconnect(self.lastsignaltmp2)
    self.celsius.disconnect(self.tmpsignal)
    self.tabletmp.destroy()
    return True
  
  def on_button13_clicked(self, button):
    self.window7.hide()
    self.tmpchange.disconnect(self.lastsignaltmp)
    if self.x10_on:
      self.addrule_tmp.disconnect(self.lastsignaltmp2)
    self.celsius.disconnect(self.tmpsignal)
    self.tabletmp.destroy()
    
  def on_actCelsius (self, button, event):
    self.temp_celsius = not self.celsius.get_active()
    
  def on_button15_clicked (self, button, event=None):
    self.window8.hide()
    #self.tabletmp.destroy()
    self.changetmp3.disconnect(self.lastsignaltmp3)
    return True
  
  def on_button16_clicked (self, button):
    self.add_tmprule(self.builder.get_object("comboboxtext13").get_active_text(),self.builder.get_object("spinbutton1").get_value(), self.builder.get_object("comboboxtext8").get_active_text(),self.builder.get_object("comboboxtext9").get_active_text())
    self.window8.hide()
    self.changetmp3.disconnect(self.lastsignaltmp3)
    self.tabletmp.destroy()
    self.rultable_tmp()
    return True
    
  def changerule_tmp (self, button):
    self.window8 = self.builder.get_object("dialog7")
    self.window8.connect("delete_event", self.on_button15_clicked)
    self.window8.show_all()
    adj = Gtk.Adjustment(1, 0, 99, 1, 1, 1)
    spinBtn = self.builder.get_object("spinbutton1")
    spinBtn.configure(adj, 1, 0)
    self.changetmp3 = self.builder.get_object("button16")
    self.lastsignaltmp3 = self.changetmp3.connect("clicked", self.on_button16_clicked)
    
    self.combotextmodus2 = self.builder.get_object("comboboxtext8")
    self.builder.get_object("comboboxtext13").set_active(0)
    self.builder.get_object("comboboxtext8").set_active(0)
    self.builder.get_object("comboboxtext9").set_active(0)
    rdymods = self.parsemymods()
    self.combotextmodus2.remove_all()
    for i in rdymods:
      self.combotextmodus2.append_text(i)
    self.combotextmodus2.set_active(0)
    
  def rultable_tmp (self):
    rules = self.parseRules("|".join(self.temp_rules))

    if len(rules) == 0:
      self.tabletmp = Gtk.Table(2, 4, False)
    else:
      self.tabletmp = Gtk.Table(len(rules)/4, 4, False)
    self.box9.pack_start(self.tabletmp, True, True, 0)
    
    optionsLabel = Gtk.Label()
    optionsLabel.set_markup("<b>Del</b>")
    self.tabletmp.attach(optionsLabel, 0, 1, 0, 1)
    
    codeLabel = Gtk.Label()
    codeLabel.set_markup("<b>State</b>")
    self.tabletmp.attach(codeLabel, 1, 2, 0, 1)
    
    nameLabel = Gtk.Label()
    nameLabel.set_markup("<b>Module</b>")
    self.tabletmp.attach(nameLabel, 2, 3, 0, 1)
    
    typeLabel = Gtk.Label()
    typeLabel.set_markup("<b>Action</b>")
    self.tabletmp.attach(typeLabel, 3, 4, 0, 1)
    
    
    if len(rules) == 0:
      self.window7.show_all()
      return
    
    for i in range(len(rules)/4):
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_delrul_tmp, i) 
      self.tabletmp.attach(deletebutton, 0, 1, 4*i+1, 4*i+2)
      self.tabletmp.attach(Gtk.Label(rules[4*i] + " " + rules[4*i+1]), 1, 2, 4*i+1, 4*i+2)
      self.tabletmp.attach(Gtk.Label(rules[4*i+2]), 2, 3, 4*i+1, 4*i+2)
      self.tabletmp.attach(Gtk.Label(rules[4*i+3]), 3, 4, 4*i+1, 4*i+2)

    self.window7.show_all()
    
  def on_delrul_tmp (self, button, rule):
    self.del_tmprule(rule)
    self.tabletmp.destroy()
    self.rultable_tmp()
    
    
  def on_button5_clicked(self, button, mod):
    name = self.builder.get_object("entry1").get_text()
    if mod.name != name:
      self.net.changeNamebyCode(name, mod.code)
    self.table.destroy()
    self.modtable()
    self.builder.get_object("entry1").set_text("")
    self.window3.hide()
    self.change.disconnect(self.lastsignal)
    self.addrule.disconnect(self.lastsignal4)
    self.senalarm.disconnect(self.alertsignal)
    self.table2.destroy()
    
  def checkTemperature (self):
    while True:
      if threads == False:
        break
      if self.temp_celsius:
        t = self.tmp.getTemperature(1)
        t2 = self.tmp.getTemperature(2)
        Gdk.threads_enter()
        self.tmpShow.set_markup("Temperature: int " + "<b>" + "{0:.2f}".format(t) + "</b> "+ u'\N{DEGREE SIGN}'+ "C | ext " + "<b>" + "{0:.2f}".format(t2) + "</b> "+ u'\N{DEGREE SIGN}'+ "C")
        Gdk.threads_leave()
        self.do_tmprule(t,t2)
      else:
        t = self.tmp.getTemperature(1) * 1.8 +32
        t2 = self.tmp.getTemperature(2) * 1.8 +32
        Gdk.threads_enter()
        self.tmpShow.set_markup("Temperature: int " + "<b>" + "{0:.2f}".format(t) + "</b> "+ u'\N{DEGREE SIGN}'+ "F | ext " + "<b>" + "{0:.2f}".format(t2) + "</b> "+ u'\N{DEGREE SIGN}'+ "F")
        Gdk.threads_leave()
        self.do_tmprule(t,t2)
      time.sleep(1)
      
    
    
  def environment(self):
    self.maingrid = Gtk.Table(3, 1, False)  
    
    self.modtable()
    
    image = Gtk.Image(stock=Gtk.STOCK_ADD)
    add_button = Gtk.Button(label="Add Module", image=image)
    add_button.connect("clicked", self.on_addModule)
    self.maingrid.attach(add_button, 0, 1, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    image = Gtk.Image(stock=Gtk.STOCK_PROPERTIES)
    
    if hasattr(self, 'tmpopt'):
      self.tmpopt.destroy()

    if self.temprun == False:
      self.tmpopt = Gtk.Button(label=" Tmp Properties", image=image)
      self.tmpopt.connect("clicked", self.cameracfg, "tmp2")
      self.maingrid.attach(self.tmpopt, 0, 1, 2, 3,yoptions=Gtk.AttachOptions.SHRINK)
    
    
  def modtable (self):
    self.Modus = self.assingmod(self.parseMod(self.net.getEnvironment()))
    if len(self.Modus) == 0:
      self.table = Gtk.Table(1, 5, True)
    else:
      self.table = Gtk.Table(len(self.Modus), 5, True)
    self.maingrid.attach(self.table, 0, 1, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    
    houseLabel = Gtk.Label()
    houseLabel.set_markup("<b><big>House A</big></b>")
    self.table.attach(houseLabel, 2, 3, 0, 1,yoptions=Gtk.AttachOptions.SHRINK)
    
    optionsLabel = Gtk.Label()
    optionsLabel.set_markup("<b>Options</b>")
    self.table.attach(optionsLabel, 0, 1, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    
    codeLabel = Gtk.Label()
    codeLabel.set_markup("<b>Code</b>")
    self.table.attach(codeLabel, 1, 2, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    
    nameLabel = Gtk.Label()
    nameLabel.set_markup("<b>Name</b>")
    self.table.attach(nameLabel, 2, 3, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    
    typeLabel = Gtk.Label()
    typeLabel.set_markup("<b>Type</b>")
    self.table.attach(typeLabel, 3, 4, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    
    activeLabel = Gtk.Label()
    activeLabel.set_markup("<b>Active</b>")
    self.table.attach(activeLabel, 4, 5, 1, 2,yoptions=Gtk.AttachOptions.SHRINK)
    
    if len(self.Modus) == 0:
      self.window.show_all()
      self.on_camrun()
      self.on_kinrun()
      return
    
    for i in self.Modus:
      optionsbuttons = Gtk.Table(1, 2, True)
      self.table.attach(optionsbuttons, 0, 1, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_delModule, i)
      changebuttonimage = Gtk.Image(stock=Gtk.STOCK_EXECUTE)
      changebutton = Gtk.Button(image=changebuttonimage)
      if (self.net.isSensor(i.name)):
        changebutton.connect("clicked", self.changename, i)
      else:
        changebutton.connect("clicked", self.changenamepro, i)
      optionsbuttons.attach(deletebutton, 0, 1, 0, 1)
      optionsbuttons.attach(changebutton, 1, 2, 0, 1)

      if i.active == False:
        
        self.table.attach(Gtk.Label(i.code), 1, 2, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
        self.table.attach(Gtk.Label(i.name), 2, 3, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
        self.table.attach(Gtk.Label(i.mtype), 3, 4, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
        if self.net.isSensor(i.name):
          l4 = Gtk.Button(" ")
          l4.set_name('NoActive')
        else:
          l4 = Gtk.Switch()
          l4.set_active(False)
          l4.connect("button-press-event", self.on_actModule, i)
        self.table.attach(l4, 4, 5, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)

      else:
        l1 = Gtk.Label()
        l1.set_markup('<span color="#347C2C">' + i.code + '</span>')
        self.table.attach(l1, 1, 2, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
        
        l2 = Gtk.Label()
        l2.set_markup('<span color="#347C2C">' + i.name + '</span>')
        self.table.attach(l2, 2, 3, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
        
        l3 = Gtk.Label()
        l3.set_markup('<span color="#347C2C">' + i.mtype + '</span>')
        self.table.attach(l3, 3, 4, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)
        
       
        if self.net.isSensor(i.name):
          l4 = Gtk.Button(label=" ")
          l4.set_name('Active')
        else:
          l4 = Gtk.Switch()
          l4.set_active(True)
          l4.connect("button-press-event", self.on_actModule, i)
        self.table.attach(l4, 4, 5, self.Modus.index(i)+2, self.Modus.index(i)+3,yoptions=Gtk.AttachOptions.SHRINK)

    self.window.show_all()
    self.on_camrun()
    self.on_kinrun()
        

  def on_delModule(self, button, mod):
    self.net.delModulebyCode(mod.code)
    self.table.destroy()
    self.modtable()
  
  def on_actModule(self, button, event, mod):
    
    if mod.active:
      threading.Thread(target=self.net.setInactive, args=[mod.name]).start()
    else:
      threading.Thread(target=self.net.setActive, args=[mod.name]).start()
    self.table.destroy()
    self.modtable()

    


        
  def on_addModule(self, button):
    self.window2 = self.builder.get_object("dialog2")
    self.window2.connect("delete_event", self.on_del)
    self.window2.show_all()
    self.codex = self.builder.get_object("comboboxtext1")
    self.typex = self.builder.get_object("comboboxtext2")
    self.codex.remove_all()
    wombocode = ["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12","A13","A14","A15","A16"]  
    for i in self.Modus:
      wombocode.remove(i.code)
    for n in wombocode:
      self.codex.append_text(n)
    self.codex.set_active(0)
    self.typex.set_active(0)
    
  def on_button7_clicked(self, button):
    code = self.builder.get_object("comboboxtext1").get_active_text()
    mtype = self.builder.get_object("comboboxtext2").get_active_text()
    name = self.builder.get_object("entry2").get_text()
    if name == "":
      name = self.builder.get_object("comboboxtext1").get_active_text()
    #Modus.append(Mod(name, code, mtype))
    #anadir modulo
    if len(self.Modus) <= 16:
      self.net.addModule(name, code, mtype)
    self.table.destroy()
    self.modtable()
    
    self.load_sensors_combotext(self.combomotion)
    
    self.builder.get_object("entry2").set_text("")
    self.window2.hide()
    
  def on_button6_clicked(self, button):
    self.builder.get_object("entry2").set_text("")
    self.window2.hide()
    
  def on_del(self, button, other):
    self.window2.hide()
    return True
    
      
      
  def parseMod (self,s):
    def str_to_bool(s):
      if s == 'True':
         return True
      else:
         return False
             
    pieces = []
    if s != "":
      mo = []
      pieces = s.split("|")
      for i in range(0,len(pieces)/4):
        newmod = Mod(pieces[i*4+1], pieces[i*4], pieces[i*4+2], str_to_bool(pieces[i*4+3]))
        mo.append(newmod)
      return mo
    return pieces
    
  def assingmod (self, mo):
    mo2 = list(self.Modus)
    if len(mo2) == 0:
      mo2 = mo[:]
      return mo2
    if len(mo) > len(mo2):
      mo2.append(mo[-1])
      return mo2
    for n in mo2:
      found = False
      for i in mo:
        if i.code == n.code:
          if i.isSensor() and i.active != n.active:
            self.doRules(n.name, i.active)
            if i.mail_alert and i.active:
              self.send_mail(i.name)
            if self.record_rdy2 and self.combomotion.get_active_text() == "("+n.code+") "+n.name:
              if i.active:
                self.record = True
              else:
                self.record = False
              
          found = True
          n.name = i.name
          n.active = i.active
          n.mtype = i.mtype
          break
      if found == False:
        #elemento n borrado
        del mo2[mo2.index(n)]
    return mo2
    
  def checkOthers (self, props):
      
    self.mailother.set_text(props["oth.mailadress"])
    self.mailtime.set_text(props["oth.secondsint"])
    if props["oth.resolution"] == "160x120":
      self.resolution.set_active(0)
    elif props["oth.resolution"] == "320x240":
      self.resolution.set_active(1)
    elif props["oth.resolution"] == "640x480":
      self.resolution.set_active(2)
      
      
  def checkCamera (self, props):
    nsensores = props["cam.sensors"]
    for n in range(1,int(nsensores)+1):
      host = props["cam."+str(n)+".Proxy"].split("CameraA:default -h ")[1].split(" -p ")[0]
      port = props["cam."+str(n)+".Proxy"].split(" -p ")[1]
      self.Camera.append([host,port])
      self.CameraRun = False
      
      hboxcams = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
      self.hboxcams.pack_start(hboxcams, True, False, 0)
      cam=Gtk.Image()
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_del_cam, hboxcams, [host,port])
      hboxcams.pack_start(cam, True, False, 0)
      hboxcams.pack_start(deletebutton, True, False, 0)
      hboxcams.show_all()
      
      if self.CameraRun == False:
        self.CameraRun = True
        self.nCam += 1
        self.on_camrun()
        self.radbut3.set_active(True)
        threading.Thread(target=self.camera, args=[cam,hboxcams]).start()

    
  def checkKinect (self, props):
    
    nsensores = props["kin.sensors"]
    for n in range(1,int(nsensores)+1):
      host = props["kin."+str(n)+".Proxy"].split("default -h ")[1].split(" -p ")[0]
      port = props["kin."+str(n)+".Proxy"].split(" -p ")[1]
      self.Kinect.append([host,port])
      
      self.KinectRun = False
      
      
      hboxkinectcams = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
      self.vboxkinectcams.pack_start(hboxkinectcams, True, False, 0)
      kinectRGB=Gtk.Image()
      kinectDepth=Gtk.Image()
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_del_kinect, hboxkinectcams, [host,port])
      hboxkinectcams.pack_start(deletebutton, True, False, 0)
      hboxkinectcams.pack_start(kinectRGB, True, False, 0)
      hboxkinectcams.pack_start(kinectDepth, True, False, 0)
      hboxkinectcams.show_all()
      
      if self.KinectRun == False:
        self.KinectRun = True
        self.nKinect += 1
        self.on_kinrun()
        #self.radbut3.set_active(True)
        threading.Thread(target=self.play_kinectRGB, args=[kinectRGB,hboxkinectcams]).start()
        threading.Thread(target=self.play_kinectDepth, args=[kinectDepth,hboxkinectcams,kinectRGB]).start()
      
      
     
    
  def checkTempcfg (self, props):
    def str_to_bool(s):
      if s == 'True':
         return True
      else:
         return False
         
    self.Temperature[0] = props["tmp.Proxy"].split("Temperature:default -h ")[1].split(" -p ")[0]
    self.Temperature[1] = props["tmp.Proxy"].split(" -p ")[1]
    self.temp_celsius = str_to_bool(props["tmp.use_Celsius"])
    if "tmp.rules" in props:
      for m in range(0,int(props["tmp.rules"])):
        self.add_tmprule(props["tmp.rules."+str(m)].split("|")[0],float(props["tmp.rules."+str(m)].split("|")[1]),props["tmp.rules."+str(m)].split("|")[2],props["tmp.rules."+str(m)].split("|")[3])

    

    
    
  def checkModules(self, props):
    def str_to_bool(s):
      if s == 'True':
         return True
      else:
         return False
         
    if "x10.Proxy" in props:
      self.x10[0] = props["x10.Proxy"].split("Net:default -h ")[1].split(" -p ")[0]
      self.x10[1] = props["x10.Proxy"].split(" -p ")[1]
      
      try:
        base = ic.stringToProxy('Net:default -h '+self.x10[0]+' -p ' + self.x10[1])
        self.net = x10.NetPrx.checkedCast(base)
        self.Modus = self.assingmod(self.parseMod(self.net.getEnvironment()))
      except:
        print "x10: Connection Failed"
    self.x10_on = True
    for i in range(1,17):
      if "x10.Module.A" + str(i) + ".name" in props:
        if self.net.isCode("A"+str(i)):
          self.net.delModulebyCode("A"+str(i))
          self.Modus = self.assingmod(self.parseMod(self.net.getEnvironment()))
        if props["x10.Module.A" + str(i) + ".type"] == "Lamp":
          mod = Mod(props["x10.Module.A" + str(i) + ".name"], "A" + str(i) , props["x10.Module.A" + str(i) + ".type"], str_to_bool(props["x10.Module.A" + str(i) + ".active"]))
          mod.setcfgAlarm(int(props["x10.Module.A" + str(i) + ".alarm_start"][0:2]),int(props["x10.Module.A" + str(i) + ".alarm_start"][3:5]),
                            int(props["x10.Module.A" + str(i) + ".alarm_end"][0:2]),int(props["x10.Module.A" + str(i) + ".alarm_end"][3:5]), 
                            str_to_bool(props["x10.Module.A" + str(i) + ".alarm_act"]))       
          self.Modus.append(mod)
          self.net.addModule(mod.name, mod.code, mod.mtype)
        else:
          mod = Mod(props["x10.Module.A" + str(i) + ".name"], "A" + str(i) , props["x10.Module.A" + str(i) + ".type"], str_to_bool(props["x10.Module.A" + str(i) + ".active"]))
          if "x10.Module.A" + str(i) + ".rules" in props:
            for m in range(0,int(props["x10.Module.A" + str(i) + ".rules"])):
              mod.setRules(props["x10.Module.A" + str(i) + ".rules."+str(m)].split("|")[0],props["x10.Module.A" + str(i) + ".rules."+str(m)].split("|")[1],props["x10.Module.A" + str(i) + ".rules."+str(m)].split("|")[2])
          mod.mail_alert = str_to_bool(props["x10.Module.A" + str(i) + ".mail_alert"])
          self.Modus.append(mod)
          self.net.addModule(mod.name, mod.code, mod.mtype)



            
     
        

if __name__ == "__main__":
  settings = Gtk.Settings.get_default()
  settings.props.gtk_button_images = True
  #GObject.threads_init()
  threads =True
  
  ic = Ice.initialize(sys.argv)
  if (sys.argv):
    propsx10 = ic.getProperties().getPropertiesForPrefix("x10")
    propscam = ic.getProperties().getPropertiesForPrefix("cam")
    propstmp = ic.getProperties().getPropertiesForPrefix("tmp")
    propskin = ic.getProperties().getPropertiesForPrefix("kin")
    propsoth = ic.getProperties().getPropertiesForPrefix("oth")
    GUI = viewGUI(propsx10, propscam, propstmp, propskin, propsoth)
  else:
    GUI = viewGUI()
    
  GLib.threads_init()
  Gdk.threads_init()
  Gdk.threads_enter()
  Gtk.main()
  Gdk.threads_leave()
    
  threads =False
    
         
    
  
  sys.exit()

