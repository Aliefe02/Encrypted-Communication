from encryptor import Encryptor
from lora import LoRa
import traceback
import json

CONFIG_PATH = 'config.json'

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def communicate(lora, enc):
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
                lora.send_message(chunk)
            
            if msg == '!exit':
                break
            
            data = lora.receive_message()
            if not data:
                continue

            message, type, completed = enc.generate_decrypted_message(data)
            
            while not completed:
                new_data = lora.receive_message()
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
    lora = LoRa(config['BAUDRATE'], config['PORT'])
    communicate(lora, enc)

    lora.close()
    print("[CLOSING CLIENT...]")
    
