import socket,select,sys,time,random
from qAndA import *



clients=[]
currentClientNum=-1
currentClient=0
score=[0,0,0]
numOfClients=0
buzzer=0
othersCannot=0

hit='hit'
start='start'

def main():
    global clients,numOfClients
    host = "127.0.0.1"
    port = 1234
    serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    serverSocket.bind((host, port)) 
    print ("Socket binded to port "+str(port)) 
    serverSocket.listen(50) 
    print("Socket is listening\nServer is Ready!!")
    print("Waiting for the players to join!")
    clients=[serverSocket]

    while True:
        #conn is socket object   addr[0] contains host   addr[1] contains port number
        conn, addr = serverSocket.accept()
        print("Connection established successfully with " + str(addr[1]))
        clients.append(conn)
        numOfClients+=1
        conn.sendall('Waiting..\n')

        if(numOfClients==3):
            time.sleep(2)
            print('Starting the game..!')
            print('Scores are 0,0,0')
            game()
            break
    
    print('\nServer is closing..')
    serverSocket.close()


def game():
    global buzzer,othersCannot,currentClient,currentClientNum,score,clients
    while True:
        buzzer=0
        othersCannot=0
        if not len(questions):
            print('Questions limit reached...Hence declaring the winner(s) with highest score')
            sendMsgToAll('over1',0)
            printscores()
            break
        time.sleep(1)
        question=sendQuestion()
        r,w,e=select.select(clients,[],[],10)

        if r:
            for sock in r:
                message=sock.recv(1024).decode('ascii')
                if buzzer==0 and message!='nodata':
                    buzzer=1
                    othersCannot=1
                    currentClient=sock
                    i=0
                    while i<len(clients):
                        if clients[i]==currentClient:
                            i-=1
                            break
                        i+=1
                    currentClientNum=i+1
                    break

        if othersCannot:
            otherisfaster='Player'+str(currentClientNum)+' is fast!'
            sendMsgToAll(otherisfaster.encode('ascii'),currentClient)
        else:
            sendMsgToAll('\nTimeUp!!...No one pressed buzzer',0)
            time.sleep(0.5)
            sendMsgToAll('Proceeding with Next question..\n',0)
            answers.pop(question)
            print('No one pressed the buzzer! Proceeding with next question..\n')
            printscores()
            continue
        
        currentClient.send('pleaseAnswer')

        answerReceived=currentClient.recv(1024).decode('ascii')
        if answerReceived=='cannot':
            score[i]-=0.5
            answers.pop(question)
            print('Player '+str(i+1)+' did not give a answer..Hence -0.5')
            sendMsgToAll('Player '+str(i+1)+' did not give a answer..Hence -0.5\n',currentClient)
            currentClient.send('You did not answer..  -0.5')
            continue
                    
        if checkAnswer(question,answerReceived,i,currentClient):
            print('Player '+str(i)+' got 5 points..Hence declaring as the winner..')
            printscores()
            break
        else:
            buzzer=0
            answers.pop(question)
            printscores()
            time.sleep(1)

    time.sleep(1)
    declareWinners()
    time.sleep(1)
    sendMsgToAll('over',0)
    time.sleep(0.5)

def printscores():
    i=0
    print('Updated Scores are: ')
    while(i<len(score)):
        print('Player'+str(i+1)+': '+str(score[i])),
        i+=1
    print('\n')



def declareWinners():
    winners=[]
    for s in score:
        if s==max(score):
            winners.append(score.index(s))  
    conn=clients[winners[0]+1]
    limitReached=str(winners[0]+1)+' won!!\n'                          
    limitReachedExcep='You won!!\n'
    if len(winners)==1:
        print('Player '+str(winners[0]+1)+' is the winner!')
        sendMsgToAll(limitReached.encode('ascii'),conn)
        conn.send(limitReachedExcep.encode('ascii'))
    else:
        if len(winners)==2:
            print('Players '+str(winners[0]+1)+' '+str(winners[1]+1)+' are the winners!')
            limitReached1="You won along with "+str(winners[1]+1)+'\n'
            limitReachedExcep1="You won along with "+str(winners[0]+1)+'\n'
            limitReachedExcep11="Winners are "+str(winners[0]+1)+','+str(winners[1]+1)+'\n'
            clients[winners[0]+1].send(limitReached1.encode('ascii'))
            time.sleep(0.5)
            clients[winners[1]+1].send(limitReachedExcep1.encode('ascii'))
            clients[4-winners[0]-winners[1]].send(limitReachedExcep11.encode('ascii'))
        else:
            print('No one is a winner!')
            limitReached2='No winners due to same scores!!\n'
            sendMsgToAll(limitReached2.encode('ascii'),0)


def checkAnswer(question,answer,i,conn):
    print('Player'+str(i)+' answered '+answer+', and the correct answer is '+answers[question])
    if answer==answers[question]:
        print('Player'+str(i)+' answered correctly.. Hence +1\n')
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
            return True
    else:
        print('Player'+str(i)+' answered wrongly.. Hence -0.5\n')
        answeredwrongly='P '+str(currentClientNum)+' got -0.5\n'
        answeredwronglyExcep='Wrong answer..-0.5\n'
        score[i]-=0.5
        sendMsgToAll(answeredwrongly.encode('ascii'),conn)
        conn.send(answeredwronglyExcep.encode('ascii'))
    return False


def sendMsgToAll(m,exception):
    global clients
    for client in clients:
        if(exception==client):
            continue
        try:
            client.send(m.encode('ascii'))
        except:
            pass

def sendQuestion():
    question=random.randint(0,len(questions)-1)
    q='Q: '+questions[question]
    print(q)
    sendMsgToAll(q.encode('ascii'),0)
    questions.pop(question)
    print('Sent the question successfully!...Removing it from the list!')
    time.sleep(0.5)
    sendMsgToAll(hit.encode('ascii'),0)
    return question

main()
