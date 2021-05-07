#!/usr/bin/env python3

# Logiserver veebiserveri ja juturoboti vahelise suhtluse salvestamiseks

import socket
import re
import os
import ast
import sys

# Port, millel logiserver töötab
LISTEN_PORT = 5005
# Juturoboti API port
FORWARD_PORT = 5006


if __name__ == "__main__":
    # Töö lõpukäsu kena kinnipüüdmine
    try:
        # https://docs.python.org/3/howto/sockets.html
        nginx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nginx_socket.bind(("localhost", LISTEN_PORT))
        print("Listening on port", LISTEN_PORT)

        nginx_socket.listen(5)
        while True:
            # Veebiserverilt saadud andmete vastuvõtt ja töötlus
            (clientsocket, address) = nginx_socket.accept()
            data_in = clientsocket.recv(4096)
            msg_data_in = ast.literal_eval(re.findall(r"{[\s\S]+}", data_in.decode("utf-8"))[0])

            # Juturobotile andmete edastus
            rasa_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            rasa_socket.connect(("localhost", FORWARD_PORT))
            rasa_socket.send(data_in)

            # Sisendsõnumi salvestus
            with open(os.path.join("logs", str(msg_data_in['sender']) + ".txt"), 'a') as file:
                file.write("User: " + msg_data_in['message'] + "\n")
            file.close()

            # Juturoboti sõnumi vastuvõtt ja töötlus, klientsocketi sulgemine (vastasel juhul tekib viga), teabe edastus
            data_out = rasa_socket.recv(4096)
            data_out_decoded = re.findall(r"{[\s\S]+}", data_out.decode("utf-8"))
            if len(data_out_decoded) > 0:
                msg_data_out = ast.literal_eval(data_out_decoded[0])
            else:
                msg_data_out = [""]
            rasa_socket.close()
            clientsocket.send(data_out)

            # Andmestruktuuri muutmine üheainsa tagastatava sõnumi korral
            if type(msg_data_out) != tuple:
                msg_data_out = (msg_data_out,)

            # Väljaminevate sõnumite salvestamine
            with open(os.path.join("logs", str(msg_data_out[0]['recipient_id']) + ".txt"), 'a') as file:
                for msg in msg_data_out:
                    file.write("Bot: " + msg['text'] + "\n")
            file.close()

    except KeyboardInterrupt as ki:
        print("Quitting...")
        sys.exit(ki)
