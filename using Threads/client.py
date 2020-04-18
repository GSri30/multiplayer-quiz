import socket,sys,select,time

def main():
    clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = "127.0.0.1" 
    port = 1234
    clientSocket.connect((host,port))
    print("Hello!!\nWelcome to the quiz!\nWaiting for players to join..\n")
    
    start=clientSocket.recv(2048).decode('ascii')
    while True:
        while start=='start':
            sockets_list = [sys.stdin, clientSocket]
            read_sockets,write_socket, error_socket = select.select(sockets_list,[],[],10)
            if read_sockets:
                for s in read_sockets:
                    if s==clientSocket:
                        message=clientSocket.recv(2048).decode('ascii')
                        if message:
                            if message=='quit':
                                start='stop'
                                break
                            print(message)
                    else:
                        message=sys.stdin.readline().strip()
                        clientSocket.send(message.encode('ascii'))
            else:
                clientSocket.send('timeout')

        if(start=='stop'):
            break

    clientSocket.close()
    time.sleep(1)
    exit()

main()
