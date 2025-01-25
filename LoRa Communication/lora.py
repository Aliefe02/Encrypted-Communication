import serial

class LoRa:
    def __init__(self, baudrate, port):
        self.baudrate = baudrate
        self.port = port
        self.ser = serial.Serial(self.baudrate, self.port)

    def send_message(self, message):
        message_to_send = message + "send\n"
        self.ser.write(message_to_send.encode())

    def receive_message(self):
        self.ser.write("recv\n".encode())

        while True:
            if self.ser.in_waiting > 0:
                return self.ser.readline().decode().strip()
            
    def close(self):
        self.ser.close()
                
