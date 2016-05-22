

class QuadcopterState:
        def __init__(self):
                self.state_dicc={"accX":0,"accY":0,"accZ":0,"gyX":0,"gyY":0,"gyZ":0,"angleX":0,"angleY":0}
        #Update the values of the state
        def update(self,update_dict):
                for key in update_dict:
                        self.state_dicc[key]=update_dict[key]
        def updateWorld(self):
                if self.state_dicc["accX"]>0.9:
                        self.state_dicc["accX"]=-0.9
                else:
                        self.state_dicc["accX"]=self.state_dicc["accX"]+0.01

        def getSensorValues(self):
                return self.state_dicc
