#include <Wire.h>
#include<Servo.h> 
//Direccion I2C de la IMU
#define MPU 0x68
#define ACCEL_X 0x3B
#define GYRO_X 0x43
 
//Ratios de conversion
#define A_R 16384.0
#define G_R 131.072

// we compute bias for 10 cycles
#define BIAS_CYCLES 20
//this is the float version to compute the average
#define BIAS_DIVIDER 20.0

//Conversion de radianes a grados 180/PI
#define RAD_A_DEG = 57.295779

#define Eng0 2
#define Eng1 3
#define Eng2 4
#define Eng3 5

#define InitialSpeed 1000

class QuadState{

  unsigned long ptime;
  unsigned long ptimeControl;
  long interval,intervalControl;
public:
  float AcX,AcY,AcZ,GyX,GyY,GyZ;
  float AngleX,AngleY;
  int eng_speed[4];
  Servo engine[4];
  
  float DAngleX,DAngleY;
  int power;
  int STOP;
  float velZ;
  float ek,dk,ik,ekZ,dkZ,ikZ;
  float old_errX,old_errY,old_errVZ;
  float accum_errX,accum_errY,accum_errVZ;
  QuadState(){
    AcX=0;AcY=0;AcZ=0;GyX=0;GyY=0;GyZ=0;
    AngleX=0;
    AngleY=0;
    ptime=0;
    ptimeControl=0;
    interval=50;
    intervalControl=50;
   
    STOP=0;
    DAngleX=0;
    DAngleY=0;
    power=1000;
    velZ=0;
    
    old_errX=0;old_errY=0;old_errVZ=0;
    accum_errX=0;accum_errY=0;accum_errVZ=0;
  }
  void init(){
    for(int i=0;i<4;i++)
       eng_speed[i]=InitialSpeed;
    engine[0].attach(Eng0);
    engine[1].attach(Eng1);
    engine[2].attach(Eng2);
    engine[3].attach(Eng3);
    for(int i=0;i<4;i++)
       engine[i].writeMicroseconds(eng_speed[i]);
    ek=10;
    dk=2;
    ik=0.0;
    ekZ=2;
    dkZ=0.1;
    ikZ=0.0;
  }
  void setDAngleX(float val){
   DAngleX=val;
  }  
  void setDAngleY(float val){
   DAngleY=val;
  }
  void setPower(int val){
   power=val;
  }
  void setVelZ(int val){
   velZ=val;
  }  
  void setSTOP(int val){
   STOP=val;
  }
  void updateControl(){
     unsigned long timeControl=millis();
    if(timeControl-ptimeControl>intervalControl){
        ptimeControl=timeControl;
        if(STOP>0){
          set_engine(0,1000);
          set_engine(1,1000);
          set_engine(2,1000);
          set_engine(3,1000);
        }else{
          // try to reach the objective in 0.2 secs
          float fut_angleX=AngleX+GyX*0.2;
          float fut_angleY=AngleY+GyY*0.2;
          float err_angleX=DAngleX-fut_angleX;
          float err_angleY=DAngleY-fut_angleY;
          float err_vel_angleZ=velZ-GyZ;
  
          accum_errX=accum_errX+err_angleX;
          float diff_errX=err_angleX-old_errX;
          float unbalanceX=ek*err_angleX+dk*diff_errX+ik*accum_errX;
                  
          accum_errY=accum_errY+err_angleY;
          float diff_errY=err_angleY-old_errY;
          float unbalanceY=ek*err_angleY+dk*diff_errY+ik*accum_errY;
                  
          accum_errVZ=accum_errVZ+err_vel_angleZ;
          float diff_errVZ=err_vel_angleZ-old_errVZ;
          float unbalanceZ=ekZ*err_vel_angleZ+dkZ*diff_errVZ+ikZ*accum_errVZ;
                  
          old_errX=err_angleX;
          old_errY=err_angleY;
          old_errVZ=err_vel_angleZ;
                  
          unbalanceY=-unbalanceY;
          //Forward left 
          set_engine(0,int(min(max(power+unbalanceX+unbalanceY+unbalanceZ,1000),2000)));
          //Forward right
          set_engine(1,int(min(max(power-unbalanceX+unbalanceY-unbalanceZ,1000),2000)));
          //Back left
          set_engine(2,int(min(max(power+unbalanceX-unbalanceY-unbalanceZ,1000),2000)));
          //Back right
          set_engine(3,int(min(max(power-unbalanceX-unbalanceY+unbalanceZ,1000),2000)));
        }
    }
  }
  void set_engine(int engineId,int value){
   eng_speed[engineId]=value; 
   engine[engineId].writeMicroseconds(eng_speed[engineId]);
  }
  void computeAngles(){
     unsigned long time=millis();
     if(time-ptime>interval){
       ptime=time;
       //Se calculan los angulos Y, X respectivamente.
       float AccX = atan(-1*AcX/sqrt(pow(AcY,2) + pow(AcZ,2)))*RAD_TO_DEG;
       float AccY = atan(AcY/sqrt(pow(AcX,2) + pow(AcZ,2)))*RAD_TO_DEG;
       //Aplicar el Filtro Complementario
       AngleY = 0.8 *(AngleY+GyY*0.05) + 0.2*AccX;
       AngleX = 0.8 *(AngleX+GyX*0.05) + 0.2*AccY;
     }
  }
};
class AccelerometerReader{
  unsigned long ptime;
  long interval;
  int bias_counter;
  float biasX;
  float biasY;
  float biasZ;
public:
  AccelerometerReader(){
    interval=50;
    ptime=0;

    bias_counter=0;
    biasX=0;
    biasY=0;
    biasZ=0;
  }
  void init(){
    Wire.begin();
    Wire.beginTransmission(MPU);  
    Wire.write(0x6B);
    Wire.write(0);
    Wire.endTransmission(true);
  }
  void Read(QuadState &state){
    unsigned long time=millis();
    if(time-ptime>interval){
       ptime=time;
         //Leer los valores del Acelerometro de la IMU
       Wire.beginTransmission(MPU);
       Wire.write(0x3B); //Pedir el registro 0x3B - corresponde al AcX
       Wire.endTransmission(false);
       Wire.requestFrom(MPU,6,true); //A partir del 0x3B, se piden 6 registros
       int16_t AcX=Wire.read()<<8|Wire.read(); //Cada valor ocupa 2 registros
       int16_t AcY=Wire.read()<<8|Wire.read();
       int16_t AcZ=Wire.read()<<8|Wire.read();
       state.AcX=AcX/A_R;
       state.AcY=AcY/A_R;
       state.AcZ=AcZ/A_R;

       //Leer los valores del Giroscopio
       Wire.beginTransmission(MPU);
       Wire.write(0x43);
       Wire.endTransmission(false);
       Wire.requestFrom(MPU,6,true); 
       int16_t GyX=Wire.read()<<8|Wire.read();
       int16_t GyY=Wire.read()<<8|Wire.read();
       int16_t GyZ=Wire.read()<<8|Wire.read();
       state.GyX=GyX/G_R;
       state.GyY=GyY/G_R;
       state.GyZ=GyZ/G_R;
       if (bias_counter<BIAS_CYCLES){
         update_bias(state.GyX,state.GyY,state.GyZ);
         bias_counter++;
       }else{
       state.GyX=state.GyX-biasX;
       state.GyY=state.GyY-biasY;
       state.GyZ=state.GyZ-biasZ;
       }
    }
  }
  void update_bias(float x,float y,float z){
    biasX+=x/BIAS_DIVIDER;
    biasY+=y/BIAS_DIVIDER;
    biasZ+=z/BIAS_DIVIDER;
  }
};

class SerialCommunicator{
  unsigned long ptime;
  long interval;
  char buffer[20];
  int bufferIndex;
  int control;
public:
  SerialCommunicator(){
    ptime=0;
    interval=50;
    bufferIndex=0;
    control=0;
  }
  void init(){
   Serial.begin(9600); 
  }
  void send_info(QuadState &state){
   unsigned long time=millis();
   if(time-ptime>interval){
     ptime=time;
     Serial.print("{");
     Serial.print("\"accX\":"); Serial.print(state.AcX); 
     Serial.print(",\"accY\":"); Serial.print(state.AcY); 
     Serial.print(",\"accZ\":"); Serial.print(state.AcZ); 
     Serial.print(",\"gyX\":"); Serial.print(state.GyX); 
     Serial.print(",\"gyY\":"); Serial.print(state.GyY); 
     Serial.print(",\"gyZ\":"); Serial.print(state.GyZ); 
     Serial.print(",\"angleX\":"); Serial.print(state.AngleX); 
     Serial.print(",\"angleY\":"); Serial.print(state.AngleY); 
     
     Serial.print(",\"eng1\":"); Serial.print(state.eng_speed[0]); 
     Serial.print(",\"eng2\":"); Serial.print(state.eng_speed[1]);
     Serial.print(",\"eng3\":"); Serial.print(state.eng_speed[2]);
     Serial.print(",\"eng4\":"); Serial.print(state.eng_speed[3]);
     Serial.print("}\n");
   }
 }
 void recv_info(QuadState &state){
   while(Serial.available()>0){
                buffer[bufferIndex]= Serial.read();
                if(buffer[bufferIndex]=='='){
                  buffer[bufferIndex]='\0';
                  set_control();
                  bufferIndex=0;
                } else if(buffer[bufferIndex]=='\n'){
                  buffer[bufferIndex]='\0';
                  set_value(state);
                  bufferIndex=0;
                } else
                bufferIndex++;
        }
 }
 void set_control(){
   if (strcmp(buffer,"aX")==0)
     control=0;
   else if (strcmp(buffer,"aY")==0)
     control=1;
   else if (strcmp(buffer,"power")==0)
     control=2;
   else if (strcmp(buffer,"rotateZ")==0)
     control=3;   
    else if (strcmp(buffer,"STOP")==0)
     control=4;     
 }
 void set_value(QuadState &state){
   String str(buffer);
    switch (control){
    case 0:
      state.setDAngleX(str.toInt());
      break;
    case 1:
      state.setDAngleY(str.toInt());
      break;
    case 2:
      state.setPower(str.toInt());
      break;
    case 3:
      state.setVelZ(str.toInt());
      break;
    case 4:
      state.setSTOP(str.toInt());
      break;
    default:
        break;
   }
 }
    
};

QuadState state;
AccelerometerReader accReader;
SerialCommunicator serialComm;
//Tester tester;
void setup(){
    serialComm.init();
    accReader.init();
    state.init();
}

void loop()
{
  accReader.Read(state);
  state.computeAngles();
  state.updateControl();
  serialComm.send_info(state);
  serialComm.recv_info(state);

}
