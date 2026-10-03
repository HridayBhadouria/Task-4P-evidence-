// I read the PIR sensor every 5 seconds.
// I send 1 when motion is detected and 0 when there is no motion.

const int PIR_PIN = 2;
const unsigned long SAMPLE_INTERVAL_MS = 5000;

unsigned long lastSampleTime = 0;

void setup() {
  Serial.begin(9600);
  pinMode(PIR_PIN, INPUT);

  // I wait briefly so the USB serial connection can start.
  delay(2000);
}

void loop() {
  unsigned long currentTime = millis();

  // I only take one reading every 5 seconds.
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentTime;

    int motionReading = digitalRead(PIR_PIN);
    Serial.println(motionReading);
  }
}
