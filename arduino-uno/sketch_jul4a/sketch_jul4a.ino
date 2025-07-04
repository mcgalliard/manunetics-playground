void setup() {
  // Initialize UART (Serial over USB) at 9600 baud
  Serial.begin(9600);

  // Wait for Serial to initialize
  while (!Serial) {
    ; // wait
  }

  // Send an initial message
  Serial.println("UART Initialized!");
}

void loop() {
  // Send a message every second
  Serial.println("Hello from Arduino!");
  delay(1000); // wait 1 second
}
