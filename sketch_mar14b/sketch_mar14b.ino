

int sensorPin1 = A3;    // Blue signal = A3 (inside of arm) // select the input pin for the potentiometer
int sensorPin2 = A5;    // Red signal = A5 (outside of arm)
int sensorValue1 = 0;  // variable to store the value coming from the sensor
int sensorValue2 = 0;

void setup() {
  // declare the ledPin as an OUTPUT:
  Serial.begin(115200);
  // Serial.begin(9600);
}


void loop() {
  // read the value from the sensor:
  sensorValue1 = analogRead(sensorPin1);
  sensorValue2 = analogRead(sensorPin2);
  
  //Serial.print("Sensor1: ");
  Serial.print(sensorValue1);
  Serial.print(" ");  // Space separation (important for Serial Plotter)
  //Serial.print("Sensor2: ");
  Serial.println(sensorValue2);
  
  //delay(10);
}
