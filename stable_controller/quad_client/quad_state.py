import threading
import math
from scipy import optimize


    
class QuadcopterState:
        def __init__(self):
                self.sensors_modified=threading.Event()
                self.controls_modified=threading.Event()
                self.sensor_dicc={"accX":0,"accY":0,"accZ":0,"gyX":0,"gyY":0,"gyZ":0,"angleX":0,"angleY":0,"eng1":1000,"eng2":1000,"eng3":1000,"eng4":1000}
                self.control_dicc={"aX":0, "aY":0, "power":1000,"rotateZ":0}
   
                self.accum_errX=0.0
                self.accum_errY=0.0
                self.accum_err_vel_angleZ=0.0
                
                self.old_errX=0.0
                self.old_errY=0.0
                self.old_err_velZ=0.0
                
                self.iAngleX=0.0
                self.iAngleY=0.0
                self.iAngleZ=0.0
                self.old_p=0.0
                self.old_q=0.0
                self.old_r=0.0
                
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
            self.updateWorld()
            self.computeSensorAngles()
            self.updateControl()
            
        
        def scale_engine(self,val):
            return float(val-1000)/1000   
            
        def updateWorld(self):
            Dt=0.01
            #compute Ti (par de cada motor)
            engine=[self.scale_engine(self.sensor_dicc["eng1"]),self.scale_engine(self.sensor_dicc["eng2"]),self.scale_engine(self.sensor_dicc["eng3"]),self.scale_engine(self.sensor_dicc["eng4"])]
            Fmax=-0.92*9.8
            engine_force=[Fmax*engine[0],Fmax*engine[1],Fmax*engine[2],Fmax*engine[3]]
            print "engine forces:"+str(engine_force)
            Tmax=(240*60)/(12100*2*math.pi)
            print "Tmax:"+str(Tmax)
            Tzi=[Tmax*engine[0],-Tmax*engine[1],-Tmax*engine[2],Tmax*engine[3]]
            print "Tzi:"+str(Tzi)
            Tzi_total=Tzi[0]+Tzi[1]+Tzi[2]+Tzi[3]
            print "par z:"+str(Tzi_total)
            #compute Mi
            fctr=math.sqrt(2)/2*0.26
            M1=[fctr*engine_force[0],fctr*engine_force[0],0]
            M2=[-fctr*engine_force[1],fctr*engine_force[1],0]
            M3=[fctr*engine_force[2],-fctr*engine_force[2],0]
            M4=[-fctr*engine_force[3],-fctr*engine_force[3],0]
            #compute L,M,N
            self.L=M1[0]+M2[0]+M3[0]+M4[0]
            self.M=M1[1]+M2[1]+M3[1]+M4[1]
            self.N=Tzi_total
            #Solve system of equations
            
            sol = optimize.root(self.model, [1, 1,1])
            p=sol['x'][0]
            q=sol['x'][1]
            r=sol['x'][2]
            print "p:"+str(p)
            print "q:"+str(q)
            print "r:"+str(r)
            #save new values
            self.old_p=p
            self.old_q=q
            self.old_r=r
            #compute angle differential
            diff_angleX=p+(q*math.sin(self.iAngleX)+r*math.cos(self.iAngleX))*math.tan(self.iAngleY)
            diff_angleY=q*math.cos(self.iAngleX)-r*math.sin(self.iAngleX)
            diff_angleZ=(q*math.sin(self.iAngleX)+r*math.cos(self.iAngleX))*(1/math.cos(self.iAngleY))
            #compute angles
            self.iAngleX=self.iAngleX+(diff_angleX*Dt)
            self.iAngleY=self.iAngleY+(diff_angleY*Dt)
            self.iAngleZ=self.iAngleZ+(diff_angleZ*Dt)
            RAD_TO_DEG=57.295779
            print "internal angles"
            print self.iAngleX*RAD_TO_DEG
            print self.iAngleY*RAD_TO_DEG
            print self.iAngleZ*RAD_TO_DEG
            #compute gravity
            
            m=1.5
            g=9.8
            engine_force_total=engine_force[0]+engine_force[1]+engine_force[2]+engine_force[3]
            accX=-g*math.sin(self.iAngleY)
            accY=g*math.cos(self.iAngleY)*math.sin(self.iAngleX)
            accZ=g*math.cos(self.iAngleY)*math.cos(self.iAngleX)
            #accX=-2*g*math.sin(self.iAngleY)
            #accY=2*g*math.cos(self.iAngleY)*math.sin(self.iAngleX)
            #accZ=2*g*math.cos(self.iAngleY)*math.cos(self.iAngleX)+engine_force_total/m 
            #compute accelerations
            self.sensor_dicc["accX"]=accX/g
            self.sensor_dicc["accY"]=accY/g
            self.sensor_dicc["accZ"]=accZ/g
            
            self.sensor_dicc["gyX"]=p*30/math.pi
            self.sensor_dicc["gyY"]=q*30/math.pi
            self.sensor_dicc["gyZ"]=r*30/math.pi
            
        def computeSensorAngles(self):
            RAD_TO_DEG=57.295779
            AccY = math.atan(-1*self.sensor_dicc["accX"]/math.sqrt(pow(self.sensor_dicc["accY"],2) + pow(self.sensor_dicc["accZ"],2)))*RAD_TO_DEG
            AccX = math.atan(self.sensor_dicc["accY"]/math.sqrt(pow(self.sensor_dicc["accX"],2) + pow(self.sensor_dicc["accZ"],2)))*RAD_TO_DEG
            self.sensor_dicc["angleX"]=self.iAngleX*RAD_TO_DEG
            self.sensor_dicc["angleY"]=self.iAngleY*RAD_TO_DEG
            #self.sensor_dicc["angleX"] = 0.98 *(self.sensor_dicc["angleX"]+self.sensor_dicc["gyX"]) + 0.02*AccX
            #self.sensor_dicc["angleY"] = 0.98*(self.sensor_dicc["angleY"]+self.sensor_dicc["gyY"]) + 0.02*AccY
            #print "diff angulos"
            #print (self.iAngleX*RAD_TO_DEG)-self.sensor_dicc["angleX"] 
            #print (self.iAngleY*RAD_TO_DEG)-self.sensor_dicc["angleY"]

        
        def model(self,x):
            p=x[0]
            q=x[1]
            r=x[2]
            Ix=0.05408
            Iy=0.05408
            Iz=0.10816
            old_p=self.old_p
            old_q=self.old_q
            old_r=self.old_r
            L=self.L
            M=self.M
            N=self.N
            Dt=0.01
            return [-L+Ix*(p-old_p)/Dt+r*q*(Iz-Iy), -M+Iy*(q-old_q)/Dt+p*r*(Ix-Iz),-N+Iz*(r-old_r)/Dt]
           
        def updateControl(self):
            ek=5
            dk=70
            ik=0.001
            ekZ=50
            dkZ=10
            ikZ=0.5
            print self.control_dicc
            err_angleX=self.control_dicc["aX"]-self.sensor_dicc["angleX"]
            err_angleY=self.control_dicc["aY"]-self.sensor_dicc["angleY"]
            err_vel_angleZ=self.control_dicc["rotateZ"]-self.sensor_dicc["gyZ"]
            print err_angleX
            print err_angleY
            self.accum_errX=self.accum_errX+err_angleX
            diff_errX=err_angleX-self.old_errX
            unbalanceX=ek*err_angleX+dk*diff_errX+ik*self.accum_errX
            
            self.accum_errY=self.accum_errY+err_angleY
            diff_errY=err_angleY-self.old_errY
            unbalanceY=ek*err_angleY+dk*diff_errY+ik*self.accum_errY
            
            self.accum_err_vel_angleZ=self.accum_err_vel_angleZ+err_vel_angleZ
            diff_err_vel_angleZ=err_vel_angleZ-self.old_err_velZ
            unbalanceZ=ekZ*err_vel_angleZ+dkZ*diff_err_vel_angleZ+ikZ*self.accum_err_vel_angleZ
            
            self.old_errX=err_angleX
            self.old_errY=err_angleY
            self.old_err_velZ=err_vel_angleZ
            
            unbalanceX=-unbalanceX
            unbalanceY=-unbalanceY
            #Forward left
            self.sensor_dicc["eng1"]=min(max(self.control_dicc["power"]+unbalanceX+unbalanceY+unbalanceZ,1000),2000)
            #Forward right
            self.sensor_dicc["eng2"]=min(max(self.control_dicc["power"]-unbalanceX+unbalanceY-unbalanceZ,1000),2000)
            #Back left
            self.sensor_dicc["eng3"]=min(max(self.control_dicc["power"]+unbalanceX-unbalanceY-unbalanceZ,1000),2000)
            #Back right
            self.sensor_dicc["eng4"]=min(max(self.control_dicc["power"]-unbalanceX-unbalanceY+unbalanceZ,1000),2000)
            
        def getSensorValues(self):
                return self.sensor_dicc
        def getControlValues(self):
                return self.control_dicc
