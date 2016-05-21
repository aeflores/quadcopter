from Tkinter import *
from tkMessageBox import *
import serial


class Port_selector:                         
	def __init__(self, root): 
                self.port=None
                self.root=root
                frame= Frame(root)
                frame.pack()
                self.PortList=["/dev/ttyACM","/dev/ttyACM1","/dev/ttyACM2","/dev/ttyACM3","COM1","COM2","COM3"]
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
                        self.port = serial.Serial(port=self.PortList[selected_port],baudrate=9600,timeout=None)
                        self.root.destroy()
                except:
                        showerror("Error", "Could not connect to port:"+ self.PortList[selected_port])
