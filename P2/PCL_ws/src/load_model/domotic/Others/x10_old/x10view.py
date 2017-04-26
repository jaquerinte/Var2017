import sys, traceback, Ice
import x10
from Colors import Colors

txt = Colors()
status = 0
ic = None
try:
    sys.stdout.write(txt.warning("Connecting to x10server...\t"))
    sys.stdout.flush()
    ic = Ice.initialize(sys.argv)
    base = ic.stringToProxy(ic.getProperties().getProperty("x10view.Proxy"))
    net = x10.NetPrx.checkedCast(base)
    if not net:
        raise RuntimeError("Invalid proxy")

    print txt.green(txt.bold("Done"))
    while True:
      entry = raw_input(">> ")
      if entry == "show environment":
        print net.showEnvironment()
      elif entry.find("deactivate") != -1:
        words = entry.split(" ")
        net.setInactive(words[1])
      elif entry.find("activate") != -1:
        words = entry.split(" ")
        net.setActive(words[1])
      
    
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
