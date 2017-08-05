import threading
import time
from quad_state import *
import sys
import json

class FileConnector:
        def connect(self):
                return True
        def start(self,state):
                self.finishEvent=threading.Event()
                self.communicator_thread=fileCommThread(1, "comm_Thread", state,self.finishEvent)
                self.communicator_thread.start()
        def finish(self):
                 self.finishEvent.set()
                 print "waiting for the communication thread to finish"
                 self.communicator_thread.join()


class fileCommThread (threading.Thread):
    def __init__(self, threadID, name,state,finishEvent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.state=state
        self.finished=finishEvent
        self.file = open(sys.argv[2], 'r')
    
    def run(self):
        print "Starting simulation"
        for line in self.file:
            if self.finished.is_set():
                break
            sensorValues=json.loads(line)
            self.state.update_sensors(sensorValues)
            if self.state.controls_modified.is_set():
                self.state.controls_modified.clear()
            time.sleep(0.1)
        self.file.close()
        print "Finished simulation"


