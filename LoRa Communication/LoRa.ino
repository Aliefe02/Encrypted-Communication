#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS 10
#define RFM95_RST 9
#define RFM95_INT 2

RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup() {
  Serial.begin(9600);

  if (!rf95.init()) {
    while (1);
  }
  if (!rf95.setFrequency(434.0)) {
    while (1);
  }
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');  
    input.trim();  
    if (input.endsWith("send")) {
      sendMessage(input); 
    } else if (input.endsWith("recv")) {
      receiveMessage();  
    }
  }
}

void sendMessage(String message) {
  message.trim();  

  message = message.substring(0, message.length() - 4);

  uint8_t msg[message.length() + 1];
  message.getBytes(msg, message.length() + 1); 


  rf95.send(msg, sizeof(msg));
  rf95.waitPacketSent(); 

  if (waitACK()) {
    Serial.println("ok");
  } else {
    Serial.println("no");
  }
}

void sendACK() {
  String ackMessage = "[ACK]";
  uint8_t ack[ackMessage.length() + 1];
  ackMessage.getBytes(ack, ackMessage.length() + 1);

  rf95.send(ack, sizeof(ack));  
  rf95.waitPacketSent(); 
}

bool waitACK() {
  uint8_t buf[10]; 
  uint8_t len = sizeof(buf);
  unsigned long startMillis = millis();  
  unsigned long timeout = 5000;  

  while (millis() - startMillis < timeout) {
    if (rf95.available()) {
      uint8_t messageLength = rf95.recv(buf, &len);  

      if (messageLength > 0) {
        String receivedMessage = String((char*)buf); 
        receivedMessage.trim(); 

        if (receivedMessage == "[ACK]") {
          return true;  
        }
      }
    }
  }


  return false; 
}


void receiveMessage() {
  uint8_t buf[255]; 
  uint8_t len = sizeof(buf);

  while (true) {
    if (rf95.available()) {
      
      memset(buf, 0, sizeof(buf));
      len = sizeof(buf); 

      uint8_t messageLength = rf95.recv(buf, &len); 

      if (messageLength > 0) {
        String newData = String((char*)buf); 

        Serial.print(newData);

        sendACK();

        if (newData.endsWith("[__END__]")) {
          break;
        }
      }
    }
  }
}
