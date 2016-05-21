from Tkinter import *
from tkMessageBox import *
import serial
import threading
import json
#import time

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
                selected_port=self.port_selectBox.curselection()[0]
                print "selected port:"+self.PortList[selected_port]
                try:
                        self.port = serial.Serial(port=self.PortList[selected_port],baudrate=9600,timeout=None)
                        self.root.destroy()
                except:
                        showerror("Error", "Could not connect to port:"+ self.PortList[selected_port])


class MainInterface:                         
	def __init__(self, root,state): 
                self.root=root
                self.state=state

                self.dataNameList=["accX","accY","accZ","gyX","gyY","gyZ"]
                self.dataValueList=dict()
                self.barNameList=["accX","accY","accZ","gyX","gyY","gyZ"]
                self.barValueList=dict()
                self.angleNameList=["angleX","angleY"]
                self.angleValueList=dict()

                self.create_passiveFrame()
                self.create_actionFrame()
                self.root.after(200, self.update)

        
        def create_actionFrame(self):
                actionFrame=Frame(self.root)
                actionFrame.pack(side=TOP)
        def create_passiveFrame(self):
                passiveFrame=Frame(self.root)
                self.create_dataFrame(passiveFrame)
                self.create_graphicalFrame(passiveFrame)
                passiveFrame.pack(side=TOP)
        def create_dataFrame(self,passiveFrame):
                dataFrame=Frame(passiveFrame)
                for x in self.dataNameList:
                        self.dataValueList[x]=StringVar()
                        self.dataValueList[x].set(x+":0")
                        label = Label(dataFrame, textvariable=self.dataValueList[x])
                        label.pack(side=TOP)
                dataFrame.pack(side=LEFT)
        def create_graphicalFrame(self,passiveFrame):
                graphicalFrame=Frame(passiveFrame)
		self.create_barFrame(graphicalFrame)
                self.create_angleFrame(graphicalFrame)
                graphicalFrame.pack(side=RIGHT)

        def create_barFrame(self,graphicalFrame):
                barFrame=Frame(graphicalFrame)
                for x in self.barNameList:
                        self.barValueList[x]=barCanvas(barFrame)
                barFrame.pack(side=TOP)
        def create_angleFrame(self,graphicalFrame):
                angleFrame=Frame(graphicalFrame)
                for x in self.angleNameList:
                        self.angleValueList[x]=angleCanvas(angleFrame)
                angleFrame.pack(side=TOP)
        def update(self):
                for key in self.dataValueList:
                                self.dataValueList[key].set(key+": "+str(self.state.state_dicc[key]))
                for key in self.barValueList:
                                self.barValueList[key].setValue(self.state.state_dicc[key])
                for key in self.angleValueList:
                                self.angleValueList[key].setValue(self.state.state_dicc[key])
                self.root.after(20, self.update)

 

        
class barCanvas:
	def __init__(self,topFrame):
                self.max=300
                self.canvas=self.canvasX = Canvas(topFrame, bg="white", height=self.max, width=50)
                self.rectangle=self.canvas.create_rectangle(0, 0, 50, 50, fill="blue")
                self.canvas.pack(side=LEFT)
        def setValue(self,value):
                self.canvas.delete(self.rectangle)
                scaled_val=int(value*(self.max/2))
                if scaled_val>=0:
                        self.rectangle=self.canvas.create_rectangle(0, self.max/2-scaled_val, 50,self.max/2, fill="green")
                else:
                        self.rectangle=self.canvas.create_rectangle(0, self.max/2, 50,self.max/2-scaled_val, fill="red")

class angleCanvas:
	def __init__(self,topFrame):
                coord = 0, 0, 300, 300
                self.canvas=self.canvasX = Canvas(topFrame, bg="white", height=300, width=300)
                self.arc=self.canvas.create_arc(coord, start=0, extent=15, fill="red")
                self.canvas.pack(side=LEFT)
        def setValue(self,value):
                scaled_val=int(value)
                if scaled_val<0:
                        scaled_val=360+scaled_val
                self.canvas.itemconfig(self.arc,extent=scaled_val)
		
	                     
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
                self.state.update(state_string)
        #for now not reachable
        print "Closing communication thread"
        self.serial_port.close()

def on_closing(main_window,comm_thread,finishEvent):
        finishEvent.set()
        print "waiting for the communication thread to finish"
        comm_thread.join()
        main_window.destroy()

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

	
main()
