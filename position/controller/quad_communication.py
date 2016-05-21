import serial
import threading


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
