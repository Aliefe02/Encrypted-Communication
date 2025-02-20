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
    print("[COMMUNICATION HAS STARTED]")
    while True:
        try:
            data = lora.receive_message()

            message, type, completed = enc.generate_decrypted_message(data)
            
            while not completed:
                new_data = lora.receive_message()
                data = data + new_data
                message, type, completed = enc.generate_decrypted_message(data)
                
            if type == 'string':
                if message == '!exit':
                    print("[CLIENT HAS ENDED THE CONNECTION...]")
                    break

                print(f"- {message}")
            else:
                print(f"[{message} IS SAVED INTO FILES FOLDER]")

            msg = input('+ ')

            if msg[:5] == '!file':
                msg_type = 'file'
                msg = msg[5:].strip()
            else:
                msg_type = 'string'

            encrypted_message = enc.generate_encrypted_message(msg, msg_type)
            
            if not lora.send_message(encrypted_message):
                    print("[ERROR WHEN SENDING MESSAGE]")
                    continue
            
            if msg == '!exit':
                break
            
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
    print("[CLOSING SERVER...]")
