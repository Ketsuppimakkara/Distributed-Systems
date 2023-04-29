import random
import socket
import string
import threading

host = "127.0.0.1"                              ## Runs in localhost
port = 6000                                     ## Port to listen on

#This sends a request to the appointment service
def appointmentRequest(listened_to_client,response):
    request = response.split("|")
    if(request[0] == "appointment"):
            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            try:
                client.connect(("127.0.0.1",6001))
                client.sendall(bytes(response,"utf-8"))
                while True:
                    try:
                        serviceResponse = client.recv(2048).decode('utf-8')
                    except Exception as e:
                        print(e)
                        break
                    listened_to_client.sendall(serviceResponse.encode("utf-8"))
                    break
            except Exception as e:
                print(e)
                print("Error while connecting to server")
                listened_to_client.sendall("Error connecting to service".encode("utf-8"))
            return
                    
#This sends a request to the authentication service
def authenticationRequest(listened_to_client,response):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect(("127.0.0.1",6003))
        client.sendall(bytes(response,"utf-8"))
        while True:
            try:
                serviceResponse = client.recv(2048).decode('utf-8')
            except Exception as e:
                print(e)
                break
            if(listened_to_client != ""):   ##This is a dirty workaround that lets the gateway communicate with authentication service without providing the connected client when first verifying username/password for new connection
                listened_to_client.sendall(serviceResponse.encode("utf-8"))
            return serviceResponse
    except Exception as e:
        print(e)
        print("Error while connecting to server")
        return("Error connecting to service")
    return

## This sends a request to the profile service
def profileRequest(listened_to_client,response):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client.connect(("127.0.0.1",6002))
            client.sendall(bytes(response,"utf-8"))
            while True:
                try:
                    serviceResponse = client.recv(2048).decode('utf-8')
                except Exception as e:
                    print(e)
                    break
                listened_to_client.sendall(serviceResponse.encode("utf-8"))
                break
        except Exception as e:
            print(e)
            print("Error connecting to service")
            listened_to_client.sendall("Error connecting to service".encode("utf-8"))
        return

## Main loop for receiving messages from authenticated user. Simply takes the first part of the input it receives to determine which service to contact
def listenForMessages(listened_to_client):
    while True:
        try:
            response = listened_to_client.recv(2048).decode('utf-8')
        except Exception as e:
            print(e)
            continue
        request = response.split("|")
        if(request[0] == "disconnect"):
            listened_to_client.sendall(bytes("disconnected".encode("utf-8")))
            return                      ##This closes the thread
        if(request[0] == "appointment"):
            appointmentRequest(listened_to_client,response)
            continue
        if(request[0] == "profile"):
            profileRequest(listened_to_client,response)
            continue
        if(request[0] == "auth"):
            authenticationRequest(listened_to_client,response)
            continue
            

## Runs in a thread for each connected client. Listens for the first message sent by the client, which is the username and password of the user.
## Once the credentials are received, queries the authentication service to generate a session token if credentials are correct. 
## IF so, starts a thread which listens for messages from the authenticated user. Sends a confirmation to client that authentication was successful.
def handleClient(client):
    while True:
        try:
            handshakeContent = client.recv(2048).decode('utf-8')
        except Exception as e:
            print(e)
            client.sendall("Error occurred: "+str(e).encode("utf-8"))
            return 1                    
        if handshakeContent != '':
            username = handshakeContent.split("|")[0]
            password = handshakeContent.split("|")[1]
            authResponse = authenticationRequest("","auth|"+username+"|"+password)
            if(authResponse == "malformed request" or authResponse == "invalid credentials" or authResponse == "Error connecting to service"):
                client.sendall("Error in auth, try again".encode("utf-8"))
                return
            else:
                
            ## This generates a session token. So far it's just a random string.
            ## TODO: Include useful data into session token like userID and Role. 
            ## Implement secure encryption for the data so that plaintext information is not freely flying about the network.
                sessionToken = "".join(random.choice(string.ascii_lowercase) for i in range(12))
                client.sendall("Session registered".encode("utf-8"))
                break
        else:
            print("Request is empty!")
            client.sendall("Request is empty".encode("utf-8"))
            return
    threading.Thread(target=listenForMessages,args=(client,)).start()
        
## Main function starts by creating a TCP IPv4 socket, binding it and starting to listen.
## Listens for new connections, starting a new thread that executes handleClient for each new connection. This allows the gateway to serve multiple users at the same time.
def main():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:                     
        s.bind((host,port))                                                         
        s.listen()                                                                  
        while True:
            newClient, addr = s.accept()                                            
            print("New connection from "+str(addr))
            clientThread = threading.Thread(target=handleClient, args=(newClient,))
            clientThread.start()


if __name__ == "__main__":
    main()




