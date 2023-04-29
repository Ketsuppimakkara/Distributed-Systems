import socket
import threading
import random
import string

host = "127.0.0.1"                              ## Runs in localhost
port = 6003                                     ## Port to listen on

## Given a client and a message, sends message to the client. Encoded in utf-8
def sendMessage_to(to_client,message):
    try:
        to_client.sendall(message.encode("utf-8"))
    except Exception as e:
        print(e)

## Takes a request, parameters separated by vertical bars. Handles either reading or writing to the database.
## TODO: Implement an actual database, not just a text file.
## TODO: Add a timeout so if a message never comes, the threads don't keep running forever
def listenForMessages(listened_to_client,sessiontoken):
    while True:
        try:
            response = listened_to_client.recv(2048).decode('utf-8')
        except Exception as e:
            print(e)
            listened_to_client.sendall("an error occurred".encode("utf-8"))
            break
        try:
            parsedResponse = response.split("|")
            username = str(parsedResponse[1]).strip("\n")
            password = str(parsedResponse[2]).strip("\n")
            with open("authenticationDatabase.txt","r") as f:
                for line in f:
                    if(line.split(",")[1].strip("\n") == username and line.split(",")[2].strip("\n") == password):
                        listened_to_client.sendall("success".encode("utf-8"))
                        f.close()
                        break
            f.close()
            listened_to_client.sendall("invalid credentials".encode("utf-8"))
            break
        except Exception as e:
            print(e)
            print("Received malformed request")
            listened_to_client.sendall("malformed request".encode("utf-8"))
            break


## Main function starts by creating a TCP IPv4 socket, binding it and starting to listen.
## Listens for new connectinos, starting a new thread that executes handleClient for each new connection.
def main():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:                     
        s.bind((host,port))                                                         
        s.listen()                                                                  
        while True:
            newClient, addr = s.accept()                                            
            print("New connection from "+str(addr))
            clientThread = threading.Thread(target=listenForMessages, args=(newClient,"TODOtoken"))
            clientThread.start()


if __name__ == "__main__":
    main()




