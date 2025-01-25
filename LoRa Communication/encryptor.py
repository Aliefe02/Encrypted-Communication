from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import datetime
import hashlib
import random
import base64
import json
import os


MSG_SIZE = 255

class Encryptor:
    def __init__(self, secret_key):
        self.key = self.create_key(secret_key)



    def create_key(self, user_key):
        return hashlib.sha256(user_key.encode('utf-8')).digest()



    def generate_encrypted_message(self, data, type):
        if type == 'string':
            encrypted_data, iv = self.encrypt_message(data)

        elif type == 'file':
            encrypted_data, iv = self.encrypt_file(filepath=data)

        encrypted_data_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        iv_base64 = base64.b64encode(iv).decode()

        message_json = {"body":encrypted_data_base64, "iv":iv_base64, "created_at":datetime.datetime.now().isoformat(), "type":type}

        if type == 'file':
            message_json["filename"] = os.path.basename(data) 

        message = json.dumps(message_json) + "[__END__]"

        message_chunks = [message[i:i + MSG_SIZE] for i in range(0, len(message), MSG_SIZE)]
        
        return message_chunks
    

    def generate_decrypted_message(self, encrypted_message):

        encrypted_message = encrypted_message.decode('utf-8')
        completed = encrypted_message[-9:] == '[__END__]'
        
        if not completed:
            return encrypted_message, '', completed
        
        encrypted_message = encrypted_message[:-9]
            
        encrypted_message = json.loads(encrypted_message)

        if encrypted_message['type'] == 'string':
            message = self.decrypt_message(encrypted_message['body'], encrypted_message['iv'])
            
        elif encrypted_message['type'] == 'file':
    
            message = self.decrypt_file(encrypted_message['body'], encrypted_message['iv'], encrypted_message['filename'])

        return message, encrypted_message['type'], completed
    

    def encrypt_message(self, message):
        iv_text = f"IV__KEY__{random.randint(1000000, 9999999)}"
        iv = iv_text.encode()
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))

        # Pad the data to make it a multiple of block size (16 bytes for AES)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message.encode('utf-8')) + padder.finalize()

        # Encrypt the padded data
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_data, iv


    def encrypt_file(self, filepath):

        with open(filepath, 'rb') as file:
            file_data = file.read()

        iv_text = f"IV__KEY__{random.randint(1000000, 9999999)}"
        iv = iv_text.encode()

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(file_data) + padder.finalize()

        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        return encrypted_data, iv


    def decrypt_message(self, encrypted_data, iv):

        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)

        # Initialize cipher with the same key and IV
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))

        # Decrypt the data
        decryptor = cipher.decryptor()
        decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Unpad the decrypted data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return decrypted_data.decode('utf-8')

    
    def decrypt_file(self, encrypted_data, iv, filename):
        encrypted_data = base64.b64decode(encrypted_data)
        iv = base64.b64decode(iv)

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))

        decryptor = cipher.decryptor()
        decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

        output_folder = "files"
        output_path = f"{output_folder}/{filename}"
        file_name_stripped, extension = os.path.splitext(filename)

        os.makedirs(output_folder, exist_ok=True)
        
        i = 1
        if os.path.exists(output_path):
            while True:
                if os.path.exists(f"{output_folder}/{file_name_stripped}_{i}{extension}"):
                    i += 1
                else:
                    filename = f"{file_name_stripped}_{i}{extension}"
                    output_path = f"{output_folder}/{filename}"
                    break
            
            
        with open(output_path, "wb") as file:
            file.write(decrypted_data)

        return filename




