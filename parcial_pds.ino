# Developed by jos_0W
const int sensorPin= A1;
void setup()
{
  Serial.begin(9600);
}

void loop()
{
  int value = analogRead(sensorPin);
  float millivolts = (value / 1023.0) * 5000;
  float celsius = millivolts / 10;
  
  Serial.println(celsius);
  delay(1000);
}
