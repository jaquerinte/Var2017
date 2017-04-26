from gi.repository import Gtk,GObject,Gdk,GLib
from Mod import Mod
import sys, traceback, Ice
import x10
from Colors import Colors
from threading import Thread, Timer
import threading
import time




class viewGUI:

  asktime = 5
  Modus = []
  Alarms = []
  Rules = []

  def __init__(self):
    self.builder = Gtk.Builder()
    self.builder.add_from_file("x10view.glade")
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

    self.environment()

    self.notebook.append_page(self.maingrid, Gtk.Label("Environment"))
    threading.Thread(target=self.askdformods).start()
    
    self.window.show_all()
    
  def askdformods (self):
    while True:
      newmod = self.parseMod(net.getEnvironment())
      if len(self.Modus) != len(newmod):
        Gdk.threads_enter()
        self.table.destroy()
        self.modtable()
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
            Gdk.threads_leave()
            break

    
  def changename (self, button, mod):
    self.window3 = self.builder.get_object("dialog1")
    self.builder.get_object("entry1").set_text(mod.name)
    self.window3.connect("delete_event", self.on_button4_clicked)
    self.window3.show_all()
    self.change = self.builder.get_object("button5")
    self.lastsignal = self.change.connect("clicked", self.on_button5_clicked, mod)

    

    
  def on_button4_clicked(self, button, event=None):
    self.builder.get_object("entry1").set_text("")
    self.window3.hide()
    self.change.disconnect(self.lastsignal)
    return True

    
  def on_button5_clicked(self, button, mod):
    name = self.builder.get_object("entry1").get_text()
    if mod.name != name:
      net.changeNamebyCode(name, mod.code)
    self.table.destroy()
    self.modtable()
    self.builder.get_object("entry1").set_text("")
    self.window3.hide()
    self.change.disconnect(self.lastsignal)

    
  def environment(self):
    self.maingrid = Gtk.Table(2, 1, False)  
    
    self.modtable()
    
    image = Gtk.Image(stock=Gtk.STOCK_ADD)
    add_button = Gtk.Button(label="Add Module", image=image)
    add_button.set_size_request(30,30)
    add_button.connect("clicked", self.on_addModule)
    self.maingrid.attach(add_button, 0, 1, 2, 3)
    
    
  def modtable (self):
    self.Modus = self.parseMod(net.getEnvironment())
    if len(self.Modus) == 0:
      self.table = Gtk.Table(1, 5, True)
    else:
      self.table = Gtk.Table(len(self.Modus), 5, True)
    self.maingrid.attach(self.table, 0, 1, 1, 2)
    
    houseLabel = Gtk.Label()
    houseLabel.set_markup("<b><big>House A</big></b>")
    self.table.attach(houseLabel, 2, 3, 0, 1)
    
    optionsLabel = Gtk.Label()
    optionsLabel.set_markup("<b>Options</b>")
    self.table.attach(optionsLabel, 0, 1, 1, 2)
    
    codeLabel = Gtk.Label()
    codeLabel.set_markup("<b>Code</b>")
    self.table.attach(codeLabel, 1, 2, 1, 2)
    
    nameLabel = Gtk.Label()
    nameLabel.set_markup("<b>Name</b>")
    self.table.attach(nameLabel, 2, 3, 1, 2)
    
    typeLabel = Gtk.Label()
    typeLabel.set_markup("<b>Type</b>")
    self.table.attach(typeLabel, 3, 4, 1, 2)
    
    activeLabel = Gtk.Label()
    activeLabel.set_markup("<b>Active</b>")
    self.table.attach(activeLabel, 4, 5, 1, 2)
    
    if len(self.Modus) == 0:
      self.window.show_all()
      return
    
    for i in self.Modus:
      optionsbuttons = Gtk.Table(1, 2, True)
      self.table.attach(optionsbuttons, 0, 1, self.Modus.index(i)+2, self.Modus.index(i)+3)
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_delModule, i)
      changebuttonimage = Gtk.Image(stock=Gtk.STOCK_EXECUTE)
      changebutton = Gtk.Button(image=changebuttonimage)
      changebutton.connect("clicked", self.changename, i)
      optionsbuttons.attach(deletebutton, 0, 1, 0, 1)
      optionsbuttons.attach(changebutton, 1, 2, 0, 1)

      if i.active == False:
        
        self.table.attach(Gtk.Label(i.code), 1, 2, self.Modus.index(i)+2, self.Modus.index(i)+3)
        self.table.attach(Gtk.Label(i.name), 2, 3, self.Modus.index(i)+2, self.Modus.index(i)+3)
        self.table.attach(Gtk.Label(i.mtype), 3, 4, self.Modus.index(i)+2, self.Modus.index(i)+3)
        if net.isSensor(i.name):
          l4 = Gtk.Button()
          l4.set_name('NoActive')
        else:
          l4 = Gtk.Switch()
          l4.set_active(False)
          l4.connect("button-press-event", self.on_actModule, i)
        self.table.attach(l4, 4, 5, self.Modus.index(i)+2, self.Modus.index(i)+3)

      else:
        l1 = Gtk.Label()
        l1.set_markup('<span color="#347C2C">' + i.code + '</span>')
        self.table.attach(l1, 1, 2, self.Modus.index(i)+2, self.Modus.index(i)+3)
        
        l2 = Gtk.Label()
        l2.set_markup('<span color="#347C2C">' + i.name + '</span>')
        self.table.attach(l2, 2, 3, self.Modus.index(i)+2, self.Modus.index(i)+3)
        
        l3 = Gtk.Label()
        l3.set_markup('<span color="#347C2C">' + i.mtype + '</span>')
        self.table.attach(l3, 3, 4, self.Modus.index(i)+2, self.Modus.index(i)+3)
        
       
        if net.isSensor(i.name):
          l4 = Gtk.Button()
          l4.set_name('Active')
        else:
          l4 = Gtk.Switch()
          l4.set_active(True)
          l4.connect("button-press-event", self.on_actModule, i)
        self.table.attach(l4, 4, 5, self.Modus.index(i)+2, self.Modus.index(i)+3)

    self.window.show_all()
        

  def on_delModule(self, button, mod):
    net.delModulebyCode(mod.code)
    self.table.destroy()
    self.modtable()
  
  def on_actModule(self, button, event, mod):
    
    if mod.active:
      net.setInactive(mod.name)
    else:
      net.setActive(mod.name)
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
    net.addModule(name, code, mtype)
    self.table.destroy()
    self.modtable()
    
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
    #self.modtable()
    
    

        

if __name__ == "__main__":
  settings = Gtk.Settings.get_default()
  settings.props.gtk_button_images = True
  #GObject.threads_init()

  status = 0
  ic = None
  try:
    ic = Ice.initialize(sys.argv)
    base = ic.stringToProxy(ic.getProperties().getProperty("x10view.Proxy"))
    net = x10.NetPrx.checkedCast(base)
    if not net:
        raise RuntimeError("Invalid proxy")
    

    GUI = viewGUI()

    GLib.threads_init()
    Gdk.threads_init()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()
    
    #Gtk.main()

      
    
  except:
    traceback.print_exc()
    status = 1
    sys.exit(status)

  if ic:
    # Clean up
    try:
        ic.destroy()
    except:
        traceback.print_exc()
        status = 1
  
  
  
  sys.exit(status)

