import threading,socket,select,sys,time,random
from _thread import *
from qAndA import*


clients=[]
numOfClients=0
currentClient=0
currentClientNum=-1
buzzer=0
score=[0,0,0]
question=0
temp=0

#messages
timeupBuzz='Sorry TimeUp!!\nNext question..\n'
start='start'
timeLimit='(10 seconds left)'

# questions=['What is color of orange?',
#             '34+33 is how much?',
#             '39*3 is equal to',]
# answers=['orange','67','117']

def thread(conn,addr):
    global currentClient,numOfClients,currentClientNum,buzzer,temp,question,score,clients
    if numOfClients==3:
        print('Starting the game!!\n')
        sendMsgToAll(start.encode('ascii'),0)
    while True:
        message=conn.recv(2048).decode('ascii').split(' ')
        if message:
            if buzzer==0:
                if message[0]=='timeout':
                    print('No one pressed the buzzer..Sent the same to all the players..successfully')
                    sendMsgToAll(timeupBuzz.encode('ascii'),0)
                    answers.pop(question)
                    if len(questions)==0:
                        declareWinners()
                        # time.sleep(0.5)
                        # scoresTosend=''
                        # p=0
                        # while(p<len(score)):
                        #     scoresTosend+='Player'+str(p+1)+' : '+str(score[p])+'  '
                        # sendMsgToAll(scoresTosend.encode('ascii'),0)
                        break
                    else:
                        #printscores()
                        sendQuestion()
                elif message[0]=='h':
                    currentClient=conn
                    buzzer=1
                    i=0
                    while i<len(clients):
                        if clients[i]==currentClient:
                            break
                        i+=1
                    currentClientNum=i+1
                    print('Player '+str(currentClientNum)+' pressed the buzzer first!!')
                    firstPress='P '+str(currentClientNum)+' pressed first!'
                    sendMsgToAll(firstPress.encode('ascii'),conn)
                    conn.send(timeLimit.encode('ascii'))
                

            elif (buzzer and conn==currentClient):
                if message[0]=='timeout':
                    print('Player '+str(currentClientNum)+' did not answer even after pressing the buzzer..Hence -0.5')
                    score[i]-=0.5
                    didnotsend='Player '+str(currentClientNum)+' did not give any answer!\nGoing to next question..\n'
                    didnotsendExcep="TimeUp!\nHence -0.5\n"
                    sendMsgToAll(didnotsend.encode('ascii'),conn)
                    conn.send(didnotsendExcep.encode('ascii'))
                else:
                    answer=message[0]
                    print('Player '+str(currentClientNum)+' gave '+answer+' as answer, and the original answer is '+answers[question]),
                    checkAnswer(question,answer,i,conn)
                answers.pop(question)
                buzzer=0
                if len(questions)==0:
                    declareWinners()
                    # time.sleep(0.5)
                    # scoresTosend=''
                    # p=0
                    # while(p<len(score)):
                    #     scoresTosend+='Player'+str(p+1)+' : '+str(score[p])+'  '
                    # sendMsgToAll(scoresTosend.encode('ascii'),0)
                    break
                else:
                    printscores()
                    sendQuestion()

            elif buzzer and message[0]!='timeout':
                otherisfaster='P '+str(currentClientNum)+' is fast!'
                conn.send(otherisfaster.encode('ascii'))
       
        
        else:
            if conn in clients:
                clients.remove(conn)
    
    time.sleep(1)
    printscores()
    sendMsgToAll('quit',0)
    exit()



def checkAnswer(question,answer,i,conn):
    print(question)
    if answer==answers[question]:
        print('Hence +1')
        score[i]+=1
        answeredcorrectly='P '+str(currentClientNum)+' got +1!\n'
        answeredcorrectlyExcep='Correct!!..+1\n'
        sendMsgToAll(answeredcorrectly.encode('ascii'),conn)
        conn.send(answeredcorrectlyExcep.encode('ascii'))
        gameOver='Game over!!\n'+str(currentClientNum)+' Won!!'
        gameOverExcep='You Won!!\n'
        if score[i]==5:
            print('Player '+str(i+1)+'got 5 points..Hence declaring him as the winner!')
            sendMsgToAll(gameOver.encode('ascii'),conn)
            conn.send(gameOverExcep.encode('ascii'))
            # time.sleep(0.5)
            # scoresTosend=''
            # p=0
            # while(p<len(score)):
            #     scoresTosend+='Player'+str(p+1)+' : '+str(score[p])+'  '
            # sendMsgToAll(scoresTosend.encode('ascii'),0)
    else:
        print('Hence -0.5')
        answeredwrongly='P '+str(currentClientNum)+' got -0.5\n'
        answeredwronglyExcep='Wrong answer..-0.5\n'
        score[i]-=0.5
        sendMsgToAll(answeredwrongly.encode('ascii'),conn)
        conn.send(answeredwronglyExcep.encode('ascii'))

def declareWinners():
    print('Questions limit reached...Hence declaring the winner(s) with highest score')
    winners=[]
    for s in score:
        if s==max(score):
            winners.append(score.index(s))  
    conn=clients[winners[0]]
    limitReached='Q limit reached!!\n'+str(winners[0]+1)+' won\n'                          
    limitReachedExcep='Q limit reached!!\nYou won!!\n'
    if len(winners)==1:
        print('Player '+str(winners[0]+1)+' is the winner!')
        sendMsgToAll(limitReached.encode('ascii'),conn)
        conn.send(limitReachedExcep.encode('ascii'))
    else:
        if len(winners)==2:
            print('Players '+str(winners[0]+1)+' '+str(winners[1]+1)+' are the winners!')
            limitReached1="Q limit reached!!\nYou won along with "+str(winners[1]+1)+'\n'
            limitReachedExcep1="Q limit reached!!\nYou won along with "+str(winners[0]+1)+'\n'
            limitReachedExcep11="Q limit reached!!\nWinners are "+str(winners[0]+1)+','+str(winners[1]+1)+'\n'
            clients[winners[0]].send(limitReached1.encode('ascii'))
            clients[winners[1]].send(limitReachedExcep1.encode('ascii'))
            clients[3-winners[0]-winners[1]].send(limitReachedExcep11.encode('ascii'))
        else:
            print('No one is a winner!')
            limitReached2='Q limit reached!!\nNo winners due to same scores!!\n'
            sendMsgToAll(limitReached2.encode('ascii'),0)

def printscores():
    i=0
    print('Updated Scores are: ')
    while(i<len(score)):
        print('Player'+str(i+1)+': '+str(score[i])),
        i+=1
    print('\n')

def sendQuestion():
    global question
    #question+=1
    question=0
    print(question)
    q='Q: '+questions[question]
    for c in clients:
        c.send(q.encode('ascii'))
    questions.pop(question)
    print('Sent a question successfully!...Removing it from the list!')

def sendMsgToAll(m,exception):
    for client in clients:
        if(exception!=client):
            client.send(m.encode('ascii'))

def main():
    host = "127.0.0.1"
    port = 1234
    global numOfClients
    serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    serverSocket.bind((host, port)) 
    print ("Socket binded to port "+str(port)) 
    serverSocket.listen(50) 
    print("Socket is listening\nServer is Ready!!")
    print("Waiting for the players to join!")
    while True:
        #conn is socket object   addr[0] contains host   addr[1] contains port number
        conn, addr = serverSocket.accept()
        print("Connection established successfully with " + str(addr[1]))
        clients.append(conn)
        numOfClients+=1
        start_new_thread(thread,(conn,addr))

        if(numOfClients==3):
            time.sleep(2)
            print('Starting the game..!')
            print('\n')
            print('Scores are 0,0,0')
            sendQuestion()
    
    conn.close()
    serverSocket.close()
    exit()

main()