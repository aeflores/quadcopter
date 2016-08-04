import threading

class QuadcopterState:
        def __init__(self):
                self.sensors_modified=threading.Event()
                self.controls_modified=threading.Event()
                self.sensor_dicc={"accX":0,"accY":0,"accZ":0,"gyX":0,"gyY":0,"gyZ":0,"angleX":0,"angleY":0,"eng1":1000,"eng2":1000,"eng3":1000,"eng4":1000}
                self.control_dicc={"eng1":1000, "eng2":1000, "eng3":1000,"eng4":1000}
        #Update the values of the state
        def update_sensors(self,update_dict):
                for key in update_dict:
                        self.sensor_dicc[key]=update_dict[key]
                self.sensors_modified.set()
        def update_controls(self,update_dict):
                for key in update_dict:
                        self.control_dicc[key]=update_dict[key]
                self.controls_modified.set()
                
        def updateModel(self):
                if self.sensor_dicc["accX"]>0.9:
                        self.sensor_dicc["accX"]=-0.9
                else:
                        self.sensor_dicc["accX"]=self.sensor_dicc["accX"]+0.01
                if self.sensor_dicc["angleX"]>90:
                        self.sensor_dicc["angleX"]=-90
                else:
                        self.sensor_dicc["angleX"]=self.sensor_dicc["angleX"]+0.1

        def getSensorValues(self):
                return self.sensor_dicc
        def getControlValues(self):
                return self.control_dicc
