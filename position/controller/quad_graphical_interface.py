from Tkinter import *
import math



class MainInterface:                         
	def __init__(self, root,state): 
                self.root=root
                self.state=state

                self.dataNameList=["accX","accY","accZ","gyX","gyY","gyZ","angleX","angleY"]
                self.dataValueList=dict()
 
                self.barNameList=["accX","accY","accZ","gyX","gyY","gyZ"]
                self.barValueList=dict()

                self.angleNameList=["angleX","angleY"]
                self.angleValueList=dict()

                self.controlsNameList=["eng1","eng2","eng3","eng4"]
                self.controlsValueList=dict()
                

                self.create_passiveFrame()
                self.create_actionFrame()
                self.root.after(200, self.update)

        
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
                        label = Label(dataFrame, textvariable=self.dataValueList[x],width=15)
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
        def create_actionFrame(self):
                actionFrame=Frame(self.root)
                for x in self.controlsNameList:
                        print x
                        self.controlsValueList[x]=Scale(actionFrame, orient=VERTICAL, length=200, from_=2000, to=1000,command=lambda val,whichControl=x:self.updateControl(whichControl,val))
                        self.controlsValueList[x].pack(side=LEFT)
                actionFrame.pack(side=TOP)
        def updateControl(self,controlName,value):
                print controlName+" updated to "+value
                self.state.update_controls({controlName: value})

        def update(self):
                if self.state.sensors_modified.is_set():
                        self.state.sensors_modified.clear()
                        sensor_dicc=self.state.getSensorValues()
                        for key in self.dataValueList:
                                self.dataValueList[key].set(key+": "+str(sensor_dicc[key]))
                        for key in self.barValueList:
                                self.barValueList[key].setValue(sensor_dicc[key])
                        for key in self.angleValueList:
                                self.angleValueList[key].setValue(sensor_dicc[key])
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
                self.maxHeight=200
                self.maxWidth=200
                coord = 0, 0,self.maxWidth, self.maxHeight
                self.canvas=Canvas(topFrame, bg="white", height=self.maxHeight, width=self.maxWidth)
                self.canvas.create_oval(coord,fill="gray90")
                self.canvas.create_line(0, self.maxHeight/2, self.maxWidth,self.maxHeight/2)
                self.canvas.create_line(self.maxWidth/2, 0, self.maxWidth/2,self.maxHeight)
                #self.canvas.create_line(0, self.maxWidth/2, self.maxHeight,self.maxWidth/2)
                self.arc=self.canvas.create_line(0, self.maxHeight/2, self.maxWidth,self.maxHeight/2)
                self.canvas.pack(side=LEFT)
        def setValue(self,value):
                angle=math.radians(value)
                h=self.maxWidth/2
                x=int(math.cos(angle)*h)
                y=int(math.sin(angle)*h)
                self.canvas.delete(self.arc)
                self.arc=self.canvas.create_line( h+x,self.maxHeight/2-y,h-x,self.maxHeight/2+y)
                
