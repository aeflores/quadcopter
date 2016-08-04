from Tkinter import *
import math


class MainInterface:                         
	def __init__(self, root,state): 
                self.root=root
                self.state=state
                self.dataNameList=["accX","accY","accZ","gyX","gyY","gyZ","angleX","angleY","eng1","eng2","eng3","eng4"]
                self.dataValueList=dict()
 
                self.barNameList=["accX","accY","accZ","gyX","gyY","gyZ","eng1","eng2","eng3","eng4"]
                self.barValueList=dict()

                self.angleNameList=["angleX","angleY"]
                self.angleValueList=dict()
                
                self.create_passiveFrame()
                self.create_actionFrame()
                self.root.after(200, self.update)

        
        def create_passiveFrame(self):
                passiveFrame=Frame(self.root)
                self.create_dataFrame(passiveFrame)
                self.create_graphicalFrame(passiveFrame)
                passiveFrame.pack(side=LEFT)
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
                controlFrame=Frame(self.root)
                #self.abortButton=Button(controlFrame,lambda update_map:self.updateControl(update_map))
                self.updownControl=touchControl(controlFrame,"vertical","power","",False,{"Y":1000},{"minY":1000,"maxY":2000},lambda update_map:self.updateControl(update_map))
                self.rotateControl=touchControl(controlFrame,"horizontal","rotateZ","",True,{"X":0.0},{"minX":-1.0,"maxX":1.0},lambda update_map:self.updateControl(update_map))
                self.moveControl=touchControl(controlFrame,"2D","aX", "aY",True,{"X":0.0,"Y":0.0},{"minX":-90.0,"maxX":90.0,"minY":-90.0,"maxY":90.0},lambda update_map:self.updateControl(update_map))
                controlFrame.pack(side=LEFT)
                
        def create_engineFrame(self,actionFrame):
                engineFrame=Frame(actionFrame)
                for x in self.controlsNameList:
                        print x
                        self.controlsValueList[x]=Scale(engineFrame, orient=VERTICAL, length=200, from_=2000, to=1000,command=lambda val,whichControl=x:self.updateControl(whichControl,val))
                        self.controlsValueList[x].pack(side=LEFT)
                engineFrame.pack(side=TOP)
                
        def updateControl(self,update_map):
                print " control update "
                print update_map
                self.state.update_controls(update_map)

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

 
class touchControl:
    def __init__(self,topFrame,Orientation,control_name,control_name2,with_reset,default_val,range,function):
        if Orientation=="vertical":
            self.maxX=20
            self.maxY=300
            self.rangeYmin=range["minY"]
            self.rangeYmax=range["maxY"]
            self.rangeXmin=-10.0
            self.rangeXmax=10.0
            self.defaultY=default_val["Y"]
            self.defaultX=0.0
        elif Orientation=="horizontal":
            self.maxX=300
            self.maxY=20
            self.rangeXmin=range["minX"]
            self.rangeXmax=range["maxX"]
            self.rangeYmin=-10.0
            self.rangeYmax=10.0
            self.defaultX=default_val["X"]
            self.defaultY=0.0
        else:
            self.maxX=300
            self.maxY=300
            self.rangeYmin=range["minY"]
            self.rangeYmax=range["maxY"]
            self.rangeXmin=range["minX"]
            self.rangeXmax=range["maxX"]
            self.defaultY=default_val["Y"]
            self.defaultX=default_val["X"]
        self.x=self.defaultX
        self.y=self.defaultY
        self.pressed=False
        self.function=function
        self.control_name=control_name
        self.control_name2=control_name2
        self.orientation=Orientation
        self.with_reset=with_reset
        self.canvas= Canvas(topFrame, bg="white", height=self.maxY, width=self.maxX)
        self.canvas.create_line(0, self.screenY(), self.maxX,self.screenY())
        self.canvas.create_line(self.screenX(), 0, self.screenX(),self.maxY)
        self.draw_pointer("blue")
        self.canvas.bind('<Button>',self.press)
        self.canvas.bind('<Motion>',self.move)
        self.canvas.bind('<ButtonRelease>',self.release)
        self.canvas.pack(side=LEFT)

    def screenX(self):
        return int(((self.x-self.rangeXmin)/(self.rangeXmax-self.rangeXmin))*self.maxX)
    def screenY(self):
        return int(((self.y-self.rangeYmin)/(self.rangeYmax-self.rangeYmin))*self.maxY)	
        
    def internalX(self,val):
        internal=(float(val)/self.maxX)*(self.rangeXmax-self.rangeXmin)+self.rangeXmin
        return min(max(internal,self.rangeXmin),self.rangeXmax)
    def internalY(self,val):
        internal=(float(val)/self.maxY)*(self.rangeYmax-self.rangeYmin)+self.rangeYmin
        return min(max(internal,self.rangeYmin),self.rangeYmax)
        
    def draw_pointer(self,color):
        if self.orientation=="vertical":
            self.pointer=self.canvas.create_rectangle(0,self.screenY()-5, self.maxX,self.screenY()+5, fill=color)	
        elif self.orientation=="horizontal":
            self.pointer=self.canvas.create_rectangle(self.screenX()-5,0, self.screenX()+5,self.maxY, fill=color)	
        else:
            self.pointer=self.canvas.create_rectangle(self.screenX()-5,self.screenY()-5, self.screenX()+5,self.screenY()+5, fill=color)
    def press(self,event):
        self.pressed=True
        self.x=self.internalX(event.x)
        self.y=self.internalY(event.y)
        self.canvas.delete(self.pointer)
        self.draw_pointer("red")
        self.update_control()
    def release(self,event):
        self.pressed=False
        if self.with_reset:
        	self.x=self.defaultX
        	self.y=self.defaultY
        	self.canvas.delete(self.pointer)
        	self.draw_pointer("blue")
        	self.update_control()
    def move(self,event):
        if self.pressed:
            self.x=self.internalX(event.x)
            self.y=self.internalY(event.y)
            self.canvas.delete(self.pointer)
            self.draw_pointer("red")
            self.update_control()
    def update_control(self):
    	update_map={}
    	if self.orientation=="2D":
    		update_map={self.control_name:self.x,self.control_name2:self.y}
    	elif self.orientation=="horizontal":
    		update_map={self.control_name:self.x}
    	elif self.orientation=="vertical":
    		update_map={self.control_name:self.y}
    	self.function(update_map)
class barCanvas:
	def __init__(self,topFrame):
                self.max=300
                self.max_observed=1.0
                self.canvas = Canvas(topFrame, bg="white", height=self.max, width=50)
                self.rectangle=self.canvas.create_rectangle(0, 0, 50, 50, fill="blue")
                self.canvas.pack(side=LEFT)
        def setValue(self,value):
            self.canvas.delete(self.rectangle)
            self.max_observed=max(abs(value),self.max_observed)
            scaled_val=int((value/self.max_observed)*(self.max/2))
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
                
