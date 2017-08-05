import serial
import threading
from Tkinter import *
from tkMessageBox import *
import json

def main():
        connector=SerialConnector()
        if (connector.connect()):
                connector.start()
        print "Bye!"

class SerialConnector:
        def connect(self):
                self.serial_port1=None
                self.serial_port2=None
                initial_window= Tk()
                initial_dialog=Port_selector(initial_window)
                print "Opening port selection dialog"
                initial_window.mainloop()
                print "Connected port 1!"
                self.serial_port1=initial_dialog.port
                
                initial_window= Tk()
                initial_dialog=Port_selector(initial_window)
                print "Opening port selection dialog"
                initial_window.mainloop()
                print "Connected port 2!"
                self.serial_port2=initial_dialog.port
                
                return True
        def start(self):
                self.finishEvent=threading.Event()
                self.communicator_thread1= commThread(1, "Reader 1",1, self.serial_port1,self.serial_port2,self.finishEvent)
                self.communicator_thread2= commThread(1, "Reader 2",1, self.serial_port2,self.serial_port1,self.finishEvent)
                self.communicator_thread1.start()
                self.communicator_thread2.start()
        def finish(self):
                 self.finishEvent.set()
                 print "waiting for the communication thread to finish"
                 self.communicator_thread1.join()
                 self.communicator_thread2.join()


class commThread (threading.Thread):
    def __init__(self, threadID, name, counter,read_port,write_port,finishEvent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.read_port=read_port
        self.write_port=write_port
        self.finished=finishEvent
    def run(self):
        print "Starting communication thread"
        while not self.finished.is_set():
                line=self.read_port.readline()
                print self.name+": "+line
                self.write_port.write(line)        
        print "Closing communication thread"
        self.read_port.close()


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
                        self.port = serial.Serial(port=self.PortList[selected_port],baudrate=115200,timeout=1)
                        self.root.destroy()
                except:
                        showerror("Error", "Could not connect to port:"+ self.PortList[selected_port])
                        
main()
