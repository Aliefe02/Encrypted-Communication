from encryptor import Encryptor, MSG_SIZE
import traceback
import socket
import json

CONFIG_PATH = 'config.json'

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def start_client(host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((host, port))
    data = conn.recv(MSG_SIZE).decode('utf-8')
    print(data)
    conn.send('[CONNECTION SUCCESFUL!]'.encode('utf-8'))

    return conn

def communicate(conn, enc):
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
                conn.send(chunk.encode('utf-8'))
            
            if msg == '!exit':
                conn.close()
                break
            
            data = conn.recv(MSG_SIZE)
            if not data:
                continue

            message, type, completed = enc.generate_decrypted_message(data)
            
            while not completed:
                new_data = conn.recv(MSG_SIZE)
                if not data:
                    continue
                data = data + new_data
                message, type, completed = enc.generate_decrypted_message(data)
                
            if type == 'string':
                if message == '!exit':
                    print("[SERVER HAS ENDED CONNECTION...]")
                    conn.close()
                    break
                
                print(f"- {message}")
            else:
                print(f"[{message} IS SAVED INTO FILES FOLDER]")

        except FileNotFoundError:
            print(f"[{msg} NOT FOUND]")
            continue

        except KeyboardInterrupt:
            conn.close()
            break

        except:
            traceback.print_exc()
            conn.close()
            break
    
if __name__== "__main__":
    config = load_json_file(CONFIG_PATH)
    
    conn = start_client(config['HOST'], config['PORT'])
    
    enc = Encryptor(config['SECRET_KEY'])
    
    communicate(conn, enc)

    print("[CLOSING CLIENT...]")

    if conn:
        conn.close()
