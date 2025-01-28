Encrypted message and file transfer application running on CLI.

Using AES encryption and the secret key inside the config file, each data is encrypted before being sent. Receiver must also have the same key in order to see the contents of the data. Any other individual who somehow got access to the sent package will not be able to view the contents.

There are 2 versions, Socket uses a regular TCP socket for communication.

The LoRa version is more complex. It requires 2 Arduino Nano with each connected to a LoRa Ra-02 sx1278. 
LoRa version allows data transmission with no Wifi or bluetooth. It simply uses radio waves and allows a free communication only downside being the range. Some models have a range of 5-10km however any building or tree on the way reduces this range dramatically.
The program was intented to be used with this version, it allows a free, off grid and encrypted communication.

When a message is written or a file is selected, that message is encrypted with the secret key. Then it is put in a json format. This the encrypted message, the iv, and the type of the message (file or text).

After creating the package, this package is converted to string and the "[__END__]" string is added to the end. This allows devices to know if a message is complete or only a part of the message is received.

Then this final string is divided into parts each containing at most 250 bytes. Arduino Nano has a variable with 255 bytes to hold the incoming data so any message cannot be just sent. It must follow that limit.

After creating the chunks, each chunk is sent to the Nano with adding "send" at the end of it using a serial connection. 

When Nano receives a message from serial it looks at the last 4 bytes and it it is "recv", it goes into receiving mode, if it is "send", it sends the data with removing "send" string.

After sending the data, Nano waits 5 seconds for an "ACK" message, this ensures that the package was succesfully sent to the receiver device. If no ACK message is received, Nano writes "no" into the serial.

The program also waits for this message after sending a chunk to Nano. If the response it "no", then it simply states that there was an error sending the message.

If messasge is succesfully sent, and there are more chunks, Nano continues to send them with the same format and the receiver looks at the end of each message, if there is and "[__END__]" at the end of the message, it stops receiving new messages and writes the complete message to serial. Otherwise it continues to wait for the next message.

After a message is succesfully received, program converts the string message to dict object and looks at the message type, if it is string, then it prints the message, if it is a file, then it saves the file into the files/ folder and prints filename.

![WhatsApp Image 2025-01-28 at 11 52 30](https://github.com/user-attachments/assets/9ca52364-d58e-48dc-ae36-d2c677665870)
![WhatsApp Image 2025-01-28 at 11 52 30(1)](https://github.com/user-attachments/assets/97c74f70-a125-4e27-97ae-9aa38394ecd9)
