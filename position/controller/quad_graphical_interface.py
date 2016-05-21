from Tkinter import *




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
