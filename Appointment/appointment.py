import socket
import threading

host = "127.0.0.1"                              ## Runs in localhost
port = 6001                                     ## Port to listen on

## Takes a request, parameters separated by vertical bars. Handles either reading or writing to the database.
## TODO: Implement an actual database, not just a text file.
## TODO: Add a timeout so if a message never comes, the threads don't keep running forever

def listenForMessages(listened_to_client):
    while True:
        try:
            response = listened_to_client.recv(2048).decode('utf-8')
        except Exception as e:
            print(e)
            listened_to_client.sendall("an error occurred".encode("utf-8"))
            break
        try:
            parsedResponse = response.split("|")
            task = parsedResponse[1]
            if(task == "read"):
                appointmentID = parsedResponse[2]
                with open("appointmentDatabase.txt","r") as f:
                    if(appointmentID == "all"):
                        listened_to_client.sendall(str(f.readlines()).encode("utf-8"))
                        f.close()
                        break
                    else:
                        for line in f:
                            if(line.split(",")[0] == appointmentID):
                                listened_to_client.sendall(line.encode("utf-8"))
                                f.close()
                                break
                f.close()
                listened_to_client.sendall("no such appointment".encode("utf-8"))
                break
            if(task == "write"):
                doctorID = parsedResponse[2]
                patientID = parsedResponse[3]
                startTime = parsedResponse[4]
                endTime = parsedResponse[5]
                appointmentID = 0
                with open("appointmentDatabase.txt","r")as f:
                    for line in f:
                        appointmentID = appointmentID+1
                f.close()
                with open("appointmentDatabase.txt","a") as f:
                    f.write("\n"+str(appointmentID)+","+str(doctorID)+","+str(patientID)+","+startTime+","+endTime)
                    listened_to_client.sendall("success".encode("utf-8"))
                    f.close()
                    break
            else:
                listened_to_client.sendall("malformed request".encode("utf-8"))
                break
        except Exception as e:
            print(e)
            listened_to_client.sendall("malformed request".encode("utf-8"))
            break
    return      ##This closes the thread.

## Main function starts by creating a TCP IPv4 socket, binding it and starting to listen.
## Listens for new connections, starting a new thread that executes listenforMessages for each new connection.
## Threading implemented so that the service can handle multiple requests at once. 
def main():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:                     
        s.bind((host,port))                                                         
        s.listen()                                                                  
        while True:
            newClient, addr = s.accept()                                            
            print("New connection from "+str(addr))
            clientThread = threading.Thread(target=listenForMessages, args=(newClient,))
            clientThread.start()


if __name__ == "__main__":
    main()




