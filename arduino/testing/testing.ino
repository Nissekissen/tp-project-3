

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    uint8_t data = (uint8_t) Serial.read();
    
    if (data == 0x31) {
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("HIGH");
      return;
    }

    digitalWrite(LED_BUILTIN, LOW);

    Serial.println("LOW");
  }
}
