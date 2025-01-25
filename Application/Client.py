from encryptor import Encryptor, MSG_SIZE
import traceback
import serial
import json

arduino_port = 'COM3'
baud_rate = 9600

ser = serial.Serial(arduino_port, baud_rate)


def send_message(message):
    message_to_send = message + " send"
    ser.write((message_to_send + '\n').encode())
    print(f"Sent: {message_to_send}")

def receive_message():
    ser.write("recv\n".encode())
    print("Receiving message...")

    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"Received: {response}")
            break

CONFIG_PATH = 'config.json'

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def communicate(enc):
    while True:
        try:
            msg = input('+ ')
            if msg[:5] == '!file':
                msg_type = 'file'
                msg = msg[5:].strip()
            else:
                msg_type = 'string'

            encrypted_message = enc.generate_encrypted_message(msg, msg_type)
            for chunk in encrypted_message:
                send_message(chunk)
            
            if msg == '!exit':
                break
            
            data = receive_message()
            if not data:
                continue

            message, type, completed = enc.generate_decrypted_message(data)
            
            while not completed:
                new_data = receive_message()
                if not data:
                    continue
                data = data + new_data
                message, type, completed = enc.generate_decrypted_message(data)
                
            if type == 'string':
                if message == '!exit':
                    print("[SERVER HAS ENDED CONNECTION...]")
                    break
                
                print(f"- {message}")
            else:
                print(f"[{message} IS SAVED INTO FILES FOLDER]")

        except FileNotFoundError:
            print(f"[{msg} NOT FOUND]")
            continue

        except KeyboardInterrupt:
            break

        except:
            traceback.print_exc()
            break
    
if __name__== "__main__":
    config = load_json_file(CONFIG_PATH)
    
    enc = Encryptor(config['SECRET_KEY'])
    
    communicate(enc)

    print("[CLOSING CLIENT...]")
