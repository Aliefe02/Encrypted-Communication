import serial
import time

MSG_SIZE = 245

class LoRa:
    def __init__(self, baudrate, port):
        self.baudrate = baudrate
        self.port = port
        self.ser = serial.Serial(self.port, self.baudrate)
        time.sleep(3)

    def send_message(self, message):

        message_chunks = [message[i:i + MSG_SIZE] for i in range(0, len(message), MSG_SIZE)]
        
        message_chunks_len = len(message_chunks)

        if message_chunks_len > 1:
            print(f"%0 completed", end='\r')
            for i in range(message_chunks_len):
                
                self.ser.write((message_chunks[i]+'send\n').encode())
                if not self.waitACK():
                    return False
                print(f"%{int((i+1)*100/message_chunks_len)} complete", end='\r')
            print(f"%100 completed")
            return True

        else:
            self.ser.write((message_chunks[0]+'send\n').encode())
            return self.waitACK()

    def receive_message(self):
        self.ser.write("recv\n".encode())

        data = ''
        while True:
            if self.ser.in_waiting > 0:
                data += self.ser.read(self.ser.in_waiting).decode('utf-8')
                if data[-9:] == "[__END__]":
                    return data 
            
    def close(self):
        self.ser.close()

    def waitACK(self):
        while True:
            msg = ''
            if self.ser.in_waiting >= 0:
                while self.ser.in_waiting >= 0:    
                    msg += self.ser.read(self.ser.in_waiting).decode('utf-8').replace(" ", "").replace("\n", "")
                    if len(msg) >= 2:
                        return msg[:2] == 'ok'
