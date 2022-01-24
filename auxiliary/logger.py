#!/usr/bin/env python3

# Logiserver veebiserveri ja juturoboti vahelise suhtluse salvestamiseks

import socket
import re
import ast
import sys
import psycopg2
from datetime import datetime

sys.path.append("../")

from components.helper_functions import stringify
# Andmebaasi seaded
from database_settings import *

# Port, millel logiserver töötab
LISTEN_PORT = 5005
# Juturoboti API port
FORWARD_PORT = 5006


def clear_latest(cursor, session_id):
    cursor.execute("UPDATE conversations SET latest = false WHERE user_id = " + session_id + ";")


if __name__ == "__main__":
    # Töö lõpukäsu kena kinnipüüdmine
    try:
        # https://docs.python.org/3/howto/sockets.html
        nginx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nginx_socket.bind(("localhost", LISTEN_PORT))
        conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT,
                                database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
        cur = conn.cursor()
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
            clear_latest(cur, str(msg_data_in['sender']))
            cur.execute("INSERT INTO conversations (user_id, message_timestamp, message, sent_by_user, flagged, annotation, latest) VALUES ("
                        + str(msg_data_in['sender'])
                        + ", " + stringify(datetime.now().isoformat(' ')) + ", "
                        + stringify(msg_data_in['message']) + ", "
                        + "true, false, NULL, true);")
            conn.commit()

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
            latest = "false"
            for index, msg in enumerate(msg_data_out):
                if index == len(msg_data_out) - 1:
                    clear_latest(cur, msg['recipient_id'])
                    latest = 'true'
                cur.execute("INSERT INTO conversations (user_id, message_timestamp, message, sent_by_user, flagged, annotation, latest) VALUES ("
                            + msg['recipient_id'] + ", "
                            + stringify(datetime.now().isoformat(' ')) + ", "
                            + stringify(str(msg['text'])) + ", "
                            + "false, false, NULL, " + latest + ");")
                conn.commit()

    except KeyboardInterrupt as ki:
        print("Quitting...")
        sys.exit(ki)
