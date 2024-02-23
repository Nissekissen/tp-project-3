const uint8_t MAX_MESSAGE_LENGTH = 12;


void setup() {
  Serial.begin(9600);

}

void loop() {
  // put your main code here, to run repeatedly:
  while (Serial.available() > 0) {
    static char message[MAX_MESSAGE_LENGTH];
    static uint8_t messagePos = 0;

    char inByte = Serial.read();

    if (inByte == '\n' || messagePos >= MAX_MESSAGE_LENGTH) {
      message[messagePos] = '\0';
      Serial.println(message);
      messagePos = 0;
      continue;
    }

    message[messagePos] = inByte;
    messagePos++;
  }
}
