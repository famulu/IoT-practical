const int smokeSensor = A0;
const int pushButton = 2;
const int fanPin = 8; // PWM Pin
const int buzzerPin = 6; // PWM Pin

int value = 0;

// last time millis() was called
unsigned long previousMillis = 0;

// interval at which to blink (in milliseconds)
const unsigned long interval = 200;

int smokeSensorValue = 0;
int pushButtonValue = 0;


void setup() {
  Serial.begin(9600);

  pinMode(pushButton, INPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT); 
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    value = Serial.read();

    if (value == '1') {
      digitalWrite(buzzerPin, LOW);
    } else if (value == '2') {
      digitalWrite(buzzerPin, HIGH);
    } else if (value == '3') {
      digitalWrite(fanPin, LOW);
    } else if (value == '4') {
      digitalWrite(fanPin, HIGH);
    }
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    smokeSensorValue = analogRead(smokeSensor);
    pushButtonValue = digitalRead(pushButton);

    Serial.println(smokeSensorValue + ',' + pushButtonValue);
  }

}
