#!/usr/bin/env python3

import socket
import re
import os
import ast
import sys

LISTEN_PORT = 5005
FORWARD_PORT = 5006


if __name__ == "__main__":
    try:
        # https://docs.python.org/3/howto/sockets.html
        nginx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nginx_socket.bind(("localhost", LISTEN_PORT))
        print("Listening on port", LISTEN_PORT)

        nginx_socket.listen(5)
        while True:
            # Receive and parse data from the Nginx server
            (clientsocket, address) = nginx_socket.accept()
            data_in = clientsocket.recv(4096)
            msg_data_in = ast.literal_eval(re.findall(r"{[\s\S]+}", data_in.decode("utf-8"))[0])

            # Forward data to Rasa server
            rasa_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            rasa_socket.connect(("localhost", FORWARD_PORT))
            rasa_socket.send(data_in)

            # Log the incoming data
            with open(os.path.join("logs", str(msg_data_in['sender']) + ".txt"), 'a') as file:
                file.write("User: " + msg_data_in['message'] + "\n")
            file.close()

            # Receive and parse data from the Rasa server, close the client socket (crashes otherwise), and forward the data
            data_out = rasa_socket.recv(4096)
            data_out_decoded = re.findall(r"{[\s\S]+}", data_out.decode("utf-8"))
            if len(data_out_decoded) > 0:
                msg_data_out = ast.literal_eval(data_out_decoded[0])
            else:
                msg_data_out = [""]
            rasa_socket.close()
            clientsocket.send(data_out)

            # If outgoing data has only one message, the data structure needs to be modified
            if type(msg_data_out) != tuple:
                msg_data_out = (msg_data_out,)

            # Log the outgoing message(s)
            with open(os.path.join("logs", str(msg_data_out[0]['recipient_id']) + ".txt"), 'a') as file:
                for msg in msg_data_out:
                    file.write("Bot: " + msg['text'] + "\n")
            file.close()

    except KeyboardInterrupt as ki:
        print("Quitting...")
        sys.exit(ki)
