import sys
from gi.repository import Gtk
from Mod import Mod

Modus = []
Modus.append(Mod("lampara Cocina", "A1", "Lamp"))
Modus.append(Mod("lampara Salon", "A2", "Lamp"))
Modus.append(Mod("lamp3", "A3", "Lamp"))


class viewGUI:

  def __init__(self):
    self.builder = Gtk.Builder()
    self.builder.add_from_file("x10view.glade")
    self.builder.connect_signals(self)
    self.window = self.builder.get_object("window1")
    self.window.connect("delete-event", Gtk.main_quit)
    
    self.notebook = Gtk.Notebook()
    self.window.add(self.notebook)

    self.environment()
    self.notebook.append_page(self.maingrid, Gtk.Label("Environment"))
    
    self.window.show_all()
    
    
    
    
  def environment(self):
    self.maingrid = Gtk.Table(2, 1, False)  
    
    self.modtable()
    
    image = Gtk.Image(stock=Gtk.STOCK_ADD)
    add_button = Gtk.Button(label="Add Module", image=image)
    add_button.set_size_request(30,30)
    add_button.connect("clicked", self.on_addModule)
    self.maingrid.attach(add_button, 0, 1, 2, 3)
    
    
  def modtable (self):
    self.table = Gtk.Table(len(Modus), 5, True)
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
    
    for i in Modus:
      optionsbuttons = Gtk.Table(1, 2, True)
      self.table.attach(optionsbuttons, 0, 1, Modus.index(i)+2, Modus.index(i)+3)
      deletebuttonimage = Gtk.Image(stock=Gtk.STOCK_CANCEL)
      deletebutton = Gtk.Button(image=deletebuttonimage)
      deletebutton.connect("clicked", self.on_delModule, i)
      changebuttonimage = Gtk.Image(stock=Gtk.STOCK_EXECUTE)
      changebutton = Gtk.Button(image=changebuttonimage)
      optionsbuttons.attach(deletebutton, 0, 1, 0, 1)
      optionsbuttons.attach(changebutton, 1, 2, 0, 1)

      if i.active == False:
        self.table.attach(Gtk.Label(i.code), 1, 2, Modus.index(i)+2, Modus.index(i)+3)
        self.table.attach(Gtk.Label(i.name), 2, 3, Modus.index(i)+2, Modus.index(i)+3)
        self.table.attach(Gtk.Label(i.mtype), 3, 4, Modus.index(i)+2, Modus.index(i)+3)
        l4 = Gtk.Switch()
        l4.set_active(False)
        self.table.attach(l4, 4, 5, Modus.index(i)+2, Modus.index(i)+3)
      else:
        l1 = Gtk.Label()
        l1.set_markup('<span color="#347C2C">' + i.code + '</span>')
        self.table.attach(l1, 1, 2, Modus.index(i)+2, Modus.index(i)+3)
        
        l2 = Gtk.Label()
        l2.set_markup('<span color="#347C2C">' + i.name + '</span>')
        self.table.attach(l2, 2, 3, Modus.index(i)+2, Modus.index(i)+3)
        
        l3 = Gtk.Label()
        l3.set_markup('<span color="#347C2C">' + i.mtype + '</span>')
        self.table.attach(l3, 3, 4, Modus.index(i)+2, Modus.index(i)+3)
        
        l4 = Gtk.Switch()
        l4.set_active(True)
        #l4.set_markup('<span color="#347C2C">' + str(i.active) + '</span>')
        self.table.attach(l4, 4, 5, Modus.index(i)+2, Modus.index(i)+3)
    self.window.show_all()
        
        
  def on_delModule(self, button, mod):
    #Eliminar modulo
    Modus.remove(mod)
    self.table.destroy()
    self.modtable()
        
  def on_addModule(self, button):
    self.window2 = self.builder.get_object("dialog2")
    self.window2.connect("delete_event", self.on_del)
    self.window2.show_all()
    
  def on_button7_clicked(self, button):
    code = self.builder.get_object("comboboxtext1").get_active_text()
    mtype = self.builder.get_object("comboboxtext2").get_active_text()
    name = self.builder.get_object("entry2").get_text()
    Modus.append(Mod(name, code, mtype))
    #anadir modulo
    self.table.destroy()
    self.modtable()
    
    self.builder.get_object("entry2").set_text("")
    self.window2.hide()
    
  def on_button6_clicked(self, button):
    self.window2.hide()
    
  def on_del(self, button, other):
    self.window2.hide()
    return True

        

if __name__ == "__main__":
  settings = Gtk.Settings.get_default()
  settings.props.gtk_button_images = True
  
  GUI = viewGUI()
  Gtk.main()

