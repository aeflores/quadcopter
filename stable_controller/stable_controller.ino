#include <Wire.h>
#include<Servo.h> 
//Direccion I2C de la IMU
#define MPU 0x68
 
//Ratios de conversion
#define A_R 16384.0
#define G_R 10.0

// we compute bias for 10 cycles
#define BIAS_CYCLES 10
//this is the float version to compute the average
#define BIAS_DIVIDER 10.0

//Conversion de radianes a grados 180/PI
#define RAD_A_DEG = 57.295779

#define Eng0 2
#define Eng1 3
#define Eng2 4
#define Eng3 5

#define InitialSpeed 1000

class QuadState{

  unsigned long ptime;
  long interval;
public:
  float AcX,AcY,AcZ,GyX,GyY,GyZ;
  float AngleX,AngleY;
  int eng_speed[4];
  Servo engine[4];
  
  QuadState(){
    AcX=0;AcY=0;AcZ=0;GyX=0;GyY=0;GyZ=0;
    AngleX=0;
    AngleY=0;
    ptime=0;
    interval=5;
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
       AngleX = 0.98 *(AngleX+GyX*0.010) + 0.02*AccX;
       AngleY = 0.98 *(AngleY+GyY*0.010) + 0.02*AccY;
     }
  }
};
class AccelerometerReader{
  unsigned long ptime;
  long interval;
  int bias_counter;
  float biasX;
  float biasY;
public:
  AccelerometerReader(){
    interval=5;
    ptime=0;

    bias_counter=0;
    biasX=0;
    biasY=0;
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
       Wire.requestFrom(MPU,6,true); //A diferencia del Acelerometro, solo se piden 4 registros
       int16_t GyY=Wire.read()<<8|Wire.read();
       int16_t GyX=Wire.read()<<8|Wire.read();
       int16_t GyZ=Wire.read()<<8|Wire.read();
       state.GyX=GyX/G_R;
       state.GyY=GyY/G_R;
       state.GyZ=GyZ/G_R;
       if (bias_counter<BIAS_CYCLES){
         update_bias(state.GyX,state.GyY);
         bias_counter++;
       }else{
       state.GyX=state.GyX-biasX;
       state.GyY=state.GyY-biasY;
       }
    }
  }
  void update_bias(float x,float y){
    biasX+=x/BIAS_DIVIDER;
    biasY+=y/BIAS_DIVIDER;
  }
};

/*
class Tester{
  unsigned long ptime;
  long interval;
public:
  Tester(){
    ptime=0;
    interval=10;
  }

void updateValues(QuadState &state){
     // This is for testing
   unsigned long time=millis();
   if(time-ptime>interval){
     ptime=time;
     
     if (state.engine[0]>state.engine[1])
      state.AngleX= 15;
     else    
      state.AngleX= -15;
     
     if (state.engine[2]>state.engine[3])
      state.AngleY= 15;
     else    
      state.AngleY= -15;

     if (state.AcX>0.9)
      state.AcX=-0.9;
     else    
      state.AcX=state.AcX+ 0.1;
   }
}

};
*/
class SerialCommunicator{
  unsigned long ptime;
  long interval;
  char buffer[20];
  int bufferIndex;
  int control;
public:
  SerialCommunicator(){
    ptime=0;
    interval=10;
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
   if (strcmp(buffer,"eng1")==0)
     control=0;
   else if (strcmp(buffer,"eng2")==0)
     control=1;
   else if (strcmp(buffer,"eng3")==0)
     control=2;
   else if (strcmp(buffer,"eng4")==0)
     control=3;   
 }
 void set_value(QuadState &state){
   String str(buffer);
   state.set_engine(control,str.toInt());
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
 //tester.updateValues(state);
  serialComm.send_info(state);
  serialComm.recv_info(state);

}
