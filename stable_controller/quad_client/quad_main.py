from Tkinter import *
from tkMessageBox import *
import serial
import threading
import sys


from quad_graphical_interface import *
from quad_serial_communication import *
from quad_web_communication import *
from quad_virtual_communication import *
from quad_state import *

def main():
        possibleConnectors={"serial":SerialConnector,"virtual":VirtualConnector,"wifi":WebConnector}
        if len(sys.argv)>1 and sys.argv[1] in possibleConnectors.keys():
                connectorClass=possibleConnectors[sys.argv[1]]
        else:
                connectorClass=possibleConnectors["serial"]
        
        connector=connectorClass()
        if connector.connect():
                state=QuadcopterState()
                connector.start(state)
                main_window = Tk()
                print "Creating graphical interface"
                main_dialog = MainInterface(main_window,state)  
                main_window.protocol("WM_DELETE_WINDOW",lambda:on_closing(main_window,connector))
                main_window.mainloop()
        print "Bye!"

def on_closing(main_window,connector):
        connector.finish()
        main_window.destroy()
	
main()
