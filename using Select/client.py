import socket,sys,select,time

def main():
    clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = "127.0.0.1" 
    port = 1234
    clientSocket.connect((host,port))
    print("Hello!!\nWelcome to the quiz!\nWaiting for players to join..\n")
    
    while True:
        
        message=clientSocket.recv(2048).decode('ascii')
        
        if message:
            if message=='over1':
                print('Questions limit reached...Hence declaring the winner(s) with highest score')
                continue
            if message=='over':
                print('GameOver!!!')
                time.sleep(0.5)
                break
            elif message=='hit':
                print('(You have 10sec to hit the buzzer("h"))')
                r,o,e=select.select([sys.stdin,clientSocket],[],[],10)
                if r:
                    for sock in r:
                        if(sys.stdin==sock):
                            p=sys.stdin.readline().strip()
                            if(p=='h'):
                                clientSocket.send('h')
                            else:
                                print('(You have to press "h" to hit buzzer)')
                else:
                    clientSocket.send('nodata')

            elif message=='pleaseAnswer':
                print('(You have only 10sec to answer)')
                r,o,e=select.select([sys.stdin],[],[],10)
                if r:
                    m=sys.stdin.readline().strip()
                    clientSocket.send(m.encode('ascii'))
                else:
                    print('TimeUp!!..You lost your chance!!')
                    clientSocket.send('cannot')
            else:
                print(message)
    clientSocket.close()
    exit()

main()
