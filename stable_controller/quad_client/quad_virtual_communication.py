import serial
import threading
import time
from Tkinter import *
from tkMessageBox import *
from quad_state import *

class VirtualConnector:
        def connect(self):
                return True
        def start(self,state):
                self.finishEvent=threading.Event()
                self.communicator_thread=virtualCommThread(1, "comm_Thread",1, state,self.finishEvent)
                self.communicator_thread.start()
        def finish(self):
                 self.finishEvent.set()
                 print "waiting for the communication thread to finish"
                 self.communicator_thread.join()


class virtualCommThread (threading.Thread):
    def __init__(self, threadID, name, counter,state,finishEvent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.state=state
        self.virtualState=QuadcopterState()
        self.finished=finishEvent
    def run(self):
        print "Starting simulation"
        while not self.finished.is_set():
                self.virtualState.updateModel()
                sensorValues=self.virtualState.getSensorValues()
                self.state.update_sensors(sensorValues)
                if self.state.controls_modified.is_set():
                        self.state.controls_modified.clear()
                        controlValues=self.state.getControlValues()
                        self.virtualState.update_controls(controlValues)
                        
                time.sleep(0.01)
        print "Finished simulation"


