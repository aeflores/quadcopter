import serial
import threading
from Tkinter import *
from tkMessageBox import *
import json

class SerialConnector:
        def connect(self):
                self.serial_port=None
                initial_window= Tk()
                initial_dialog=Port_selector(initial_window)
                print "Opening port selection dialog"
                initial_window.mainloop()
                print "Connected!"
                self.serial_port=initial_dialog.port
                return self.serial_port!=None
        def start(self,state):
                self.finishEvent=threading.Event()
                self.communicator_thread= commThread(1, "comm_Thread",1, state,self.serial_port,self.finishEvent)
                self.communicator_thread.start()
        def finish(self):
                 self.finishEvent.set()
                 print "waiting for the communication thread to finish"
                 self.communicator_thread.join()


class commThread (threading.Thread):
    def __init__(self, threadID, name, counter,state,serial_port,finishEvent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.state=state
        self.serial_port=serial_port
        self.finished=finishEvent
    def run(self):
        print "Starting communication thread"
        while not self.finished.is_set():
                state_string=self.serial_port.readline()
                print "read "+state_string
                try:
                        json_data = json.loads(state_string)
                        self.state.update_sensors(json_data)
                except ValueError:
                        print("invalid json term")

                if self.state.controls_modified.is_set():
                        self.state.controls_modified.clear()
                        control_dicc=self.state.getControlValues()
                        for key in control_dicc:
                                self.serial_port.write(key+"="+str(control_dicc[key])+"\n")
                        
        print "Closing communication thread"
        self.serial_port.close()


class Port_selector:                         
	def __init__(self, root): 
                self.port=None
                self.root=root
                frame= Frame(root)
                frame.pack()
                self.PortList=["/dev/ttyACM","/dev/ttyACM1","/dev/ttyACM2","/dev/ttyACM3","/dev/ttyACM4","COM1","COM2","COM3","/dev/ttyUSB0","/dev/ttyUSB1","/dev/ttyUSB2"]
                #self.PortList=serial.tools.list_ports()
                self.port_selectBox=Listbox(frame,selectmode=BROWSE)
                i=1
                for x in self.PortList:
                        self.port_selectBox.insert(i,x)
                        i=i+1
                self.port_selectBox.pack()
		self.buttonInit=Button(frame,text="Ok",command=self.buttonConfirm)
		self.buttonInit.pack()
		
	def buttonConfirm(self):
                selected_port=int(self.port_selectBox.curselection()[0])
                print "selected port:"+self.PortList[selected_port]
                try:
                        self.port = serial.Serial(port=self.PortList[selected_port],baudrate=9600,timeout=1)
                        self.root.destroy()
                except:
                        showerror("Error", "Could not connect to port:"+ self.PortList[selected_port])
