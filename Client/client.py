import socket
import sys
import time
import threading
from os import system

def listenForServerMessages(client):
    while True:
        message = client.recv(2048).decode("utf-8")
        if message != "disconnected":
            print("Response from server:")
            print(message)
        else:
            print("Server confirmed disconnection!")
            return

def sendMessages(client):
    while True:
        message = input()
        if message.strip("\n") != "disconnect":
            client.sendall(bytes(message,"utf-8"))
        else:
            client.sendall(bytes(message,"utf-8"))
            break
    return

def sendSessionToken(client):
    sessionToken = input("Enter username|password:")
    if sessionToken != '':
        client.sendall(bytes(sessionToken,"utf-8"))
    else:
        print("Request cannot be empty!")

    timeout = time.time() + 30
    while True:
        response = client.recv(2048).decode("utf-8")
        if time.time() > timeout:
            print("Connection timed out, try again.")
            sys.exit(1)
        if response != "Session registered":
            print("An error occurred during session registration, exiting.")
            sys.exit(1)
        else:
            print("Session registered!")
            break

    threading.Thread(target=listenForServerMessages, args=(client,)).start()
    sendMessages(client)

def main():
    print("Enter the server ip to connect to. (Default: 127.0.0.1)")
    #host = input()
    host = "127.0.0.1"
    print("Enter the port the server is using. (Default: 6000)")
    #try:
    #    port = int(input())
    #except Exception as e:
    #    print("Port must be a number. Error:"+str(e))
    #    return 1
    port = 6000
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect((host,port))
    except:
        print("Error while connecting to server")
        sys.exit(1)
    sendSessionToken(client)
if __name__ == '__main__':
    main()



