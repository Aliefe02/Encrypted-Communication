#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup() {
  Serial.begin(9600);

  if (!rf95.init()) {
    //Serial.println("LoRa init failed");
    while (1);
  }
  //Serial.println("LoRa init OK!");

  // Set frequency to 434.0MHz (change to your desired frequency)
  if (!rf95.setFrequency(434.0)) {
    //Serial.println("Frequency set failed");
    while (1);
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');  // Read serial input until newline
    input.trim();  // Remove leading/trailing spaces

    // Check if the input ends with 'send' or 'recv'
    if (input.endsWith("send")) {
      sendMessage(input);  // Send message
    } else if (input.endsWith("recv")) {
      receiveMessage();  // Wait for and print received data
    }
  }
}

// Function to send a message via LoRa
void sendMessage(String message) {
  message.trim();  // Clean the message

  // Remove the 'send' keyword
  message = message.substring(0, message.length() - 4);

  // Convert the string message to byte array
  uint8_t msg[message.length() + 1];
  message.getBytes(msg, message.length() + 1);  // Convert to byte array

  // Serial.print("Sending: ");
  // Serial.println(message);  // Print message to serial

  rf95.send(msg, sizeof(msg));  // Send the message
  rf95.waitPacketSent();  // Wait until message is sent

  // Now wait for ACK message
  if (waitACK()) {
    Serial.println("ok");
  } else {
    Serial.println("no");
  }
}

// Function to send ACK message
void sendACK() {
  String ackMessage = "[ACK]";
  uint8_t ack[ackMessage.length() + 1];
  ackMessage.getBytes(ack, ackMessage.length() + 1);

  rf95.send(ack, sizeof(ack));  // Send ACK message
  rf95.waitPacketSent();  // Wait until ACK is sent
}

bool waitACK() {
  uint8_t buf[10]; // Increased buffer size for safety
  uint8_t len = sizeof(buf);
  unsigned long startMillis = millis();  // Record start time
  unsigned long timeout = 5000;  // Timeout duration (5 seconds)

  while (millis() - startMillis < timeout) {
    if (rf95.available()) {
      uint8_t messageLength = rf95.recv(buf, &len);  // Receive message

      if (messageLength > 0) {
        String receivedMessage = String((char*)buf);  // Convert received bytes to string
        receivedMessage.trim();  // Remove leading/trailing whitespace or null characters

        // Print received data
        //Serial.print(receivedMessage);

        // Check if the message is ACK
        if (receivedMessage == "[ACK]") {
          return true;  // ACK received, return true
        }
      }
    }
  }

  // If timeout is reached without receiving ACK
  return false;  // Return false after 5 seconds
}


void receiveMessage() {
  uint8_t buf[255];  // Buffer to store incoming data
  uint8_t len = sizeof(buf);

  while (true) {
    if (rf95.available()) {
      // Clear the buffer for each iteration
      memset(buf, 0, sizeof(buf));  // Reset the buffer to zeros
      len = sizeof(buf);  // Reset the length

      uint8_t messageLength = rf95.recv(buf, &len);  // Receive message

      if (messageLength > 0) {
        String newData = String((char*)buf);  // Convert received bytes to string

        // Print the current data received
        Serial.print(newData);

        // Send ACK for every valid message part received
        sendACK();

        // Check if the message ends with '[__END__]'
        if (newData.endsWith("[__END__]")) {
          // If the message ends with '[__END__]', break out of the loop
          break;  // Exit the loop
        }
      }
    }
  }
}
