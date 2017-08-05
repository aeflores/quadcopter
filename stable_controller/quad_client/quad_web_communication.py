import socket
import threading
import json

class WebConnector:
        def connect(self):
            HOST = "192.168.4.2"   # Symbolic name, meaning all available interfaces
            PORT = 8888 # Arbitrary non-privileged port
            #create an INET, STREAMing socket
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind((HOST, PORT))
            #become a server socket
            print "Waiting for connection"+socket.gethostname()
            serversocket.listen(5)
            #accept connections from outside
            (clientsocket, address) = serversocket.accept()
            print "Connected!"
            self.socket=clientsocket
            return True 

        def start(self,state):
                self.finishEvent=threading.Event()
                self.communicator_thread= commThread(1, "comm_Thread",1, state,self.socket,self.finishEvent)
                self.communicator_thread.start()
        def finish(self):
                 self.finishEvent.set()
                 print "waiting for the communication thread to finish"
                 self.communicator_thread.join()


class commThread (threading.Thread):
    def __init__(self, threadID, name, counter,state,socket,finishEvent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.state=state
        self.socket=socket
        self.socket_file=socket.makefile()
        self.finished=finishEvent
    def run(self):
        print "Starting communication thread"
        while not self.finished.is_set():
                state_string=self.socket_file.readline()
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
                                self.socket.send(key+"="+str(control_dicc[key])+"\n")
                        
        print "Closing communication thread"
        self.socket.close()



