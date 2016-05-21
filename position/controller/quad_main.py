from Tkinter import *
from tkMessageBox import *
import serial
import threading
import json

from quad_port_selector import *
from quad_graphical_interface import *
from quad_communication import *
                     
class QuadcopterState:
        def __init__(self):
                self.state_dicc={"accX":0,"accY":0,"accZ":0,"gyX":0,"gyY":0,"gyZ":0,"angleX":0,"angleY":0}
        
               
        #Update the values of the state
        def update(self,state_string):
                try:
                        json_data = json.loads(state_string)
                        for key in json_data:
                                self.state_dicc[key]=json_data[key]
                except ValueError:
                        print("invalid json term")
        



def main():
        initial_window= Tk()
        initial_dialog=Port_selector(initial_window)
        print "Opening port selection dialog"
        initial_window.mainloop()
        print "Connected!"
        serial_port=initial_dialog.port
        if serial_port!=None:
                state=QuadcopterState()
                finishEvent=threading.Event()
                communicator_thread= commThread(1, "comm_Thread",1, state,serial_port,finishEvent)
                communicator_thread.start()
                main_window = Tk()
                print "Creating graphical interface"
                main_dialog = MainInterface(main_window,state)  
                main_window.protocol("WM_DELETE_WINDOW",lambda:on_closing(main_window,communicator_thread,finishEvent))
                main_window.mainloop()
        print "Bye!"

def on_closing(main_window,comm_thread,finishEvent):
        finishEvent.set()
        print "waiting for the communication thread to finish"
        comm_thread.join()
        main_window.destroy()
	
main()
