import cv2 as cv
import mediapipe as mp
import time
import pyfirmata2

#Defining I/O pins for arduino
board = pyfirmata2.Arduino('COM8')
Pin_1 = board.get_pin('d:12:o')
Pin_2 = board.get_pin('d:8:o')
Pin_3 = board.get_pin('d:7:o')
Pin_indicator = board.get_pin('d:13:o')

#Defining variables
prev=0
present=0
Flag=[0,0,0]
Mainflag=0
counter=0
BigCounter=0
tempcounter=0

#time.sleep(2.0)

#Function to count the number of fingers
def count_fingers(lst):
    cnt=0
    threshold=(lst.landmark[0].y*100-lst.landmark[9].y*100)/2.5
    
    finger1=lst.landmark[5].y*100-lst.landmark[8].y*100
    finger2=lst.landmark[9].y*100-lst.landmark[12].y*100
    finger3=lst.landmark[13].y*100-lst.landmark[16].y*100
    finger4=lst.landmark[17].y*100-lst.landmark[20].y*100
    thumb=abs(lst.landmark[5].x*100-lst.landmark[4].x*100)
   
    if(finger1>threshold):  
        cnt=1
    
    if(finger1>threshold and finger2>threshold):
        cnt+=1

    if(finger1>threshold and finger2>threshold and finger3>threshold):
        cnt+=1

    if(finger1>threshold and finger2>threshold and finger3>threshold and finger4>=threshold):
        cnt+=1

    if(finger1>threshold and finger2>threshold and finger3>threshold and finger4>=threshold and thumb>threshold/2):
        cnt+=1

    return cnt

#Function 
def led(count,Flag):

    if (count == 1 and Flag[0] == 0):
        Pin_1.write(1)
        print("Pin 1 ON")
        Flag[0]=1
    elif(count == 1 and Flag[0] == 1):
        Pin_1.write(0)
        print("Pin 1 OFF")
        Flag[0]=0

    if (count == 2 and Flag[1] == 0):
        Pin_2.write(1)
        print("Pin 2 ON")
        Flag[1]=1
    elif(count == 2 and Flag[1] == 1):
        Pin_2.write(0)
        print("Pin 2 Off")
        Flag[1]=0
    
    if (count == 3 and Flag[2] == 0):
        Pin_3.write(1)
        print("Pin 3 ON")
        Flag[2]=1
    elif(count == 3 and Flag[2] == 1):
        Pin_3.write(0)
        print("Pin 3 OFF")
        Flag[2]=0
    
    
    return Flag


cap = cv.VideoCapture(0)

drawing = mp.solutions.drawing_utils
hands=mp.solutions.hands
hand_obj = hands.Hands(max_num_hands=1)

while True:
    _, frm = cap.read() #Capture Frames

    frm = cv.flip(frm,1) #flipping frames

    res= hand_obj.process(cv.cvtColor(frm, cv.COLOR_BGR2RGB)) #Converting image format

    #Check for initial condition, For 2 seconds
    if res.multi_hand_landmarks:
        hand_keypoints = res.multi_hand_landmarks[0]
        count=count_fingers(hand_keypoints)
        if count==0:
            BigCounter+=1
    else:
        BigCounter=0

    if Mainflag==1:
        tempcounter+=1
        print(tempcounter)

    if tempcounter>200:
            Mainflag=0
            tempcounter=0
            print("Not Allowed")
            Pin_indicator.write(0)


    if res.multi_hand_landmarks:
        hand_keypoints = res.multi_hand_landmarks[0]
        count=count_fingers(hand_keypoints)
        
        if count==0 and Mainflag==0:
            print("counter: ",BigCounter)
            if BigCounter>45:
                    Mainflag=1
                    print("Allowed")
                    BigCounter=0
        else:
            BigCounter=0
            Pin_indicator.write(0)

        #If initial condition satistied, check if gesture is there for 1.5 seconds
            
        if Mainflag==1 and tempcounter<200: 
            Pin_indicator.write(1)
            present=count
            if prev==present and present!=0:
                prev=present
                counter+=1
                if counter>30:
                    led(count,Flag)
                    #print("Its ON/OFF")
                    counter=0
                    Mainflag=0
                    tempcounter=0
            else:
                prev=present
                counter=0
                

        drawing.draw_landmarks(frm,hand_keypoints,hands.HAND_CONNECTIONS)


    cv.imshow("window",frm)

    #close camera when ESC is pressed
    if cv.waitKey(1)==27:
        cv.destroyAllWindows()
        cap.release()
        break