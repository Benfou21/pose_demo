#!/usr/bin/env python
# coding: utf-8


import cv2
import mediapipe as mp
import math
import time
import numpy as np
from transitions import Machine


from utils_math import calculate_angle
from utils_math import calculate_dist




# Initialisation de MediaPipe Pose.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()







# ### 1er Exo (dev militaire)
# 
# - a 1 ) 11-13-15
# - a 2 ) 12-14-16
#     
#         Init/ 60-64
# 
#         End/ 145-150
# 
# - b 1 ) 13-11-23
# - b 2 ) 14-12-24
# 
#         Init/ 80-90
# 
#         End/ 155-165
# 
# - c 1 ) 14.y == 13.y
# - c 2 ) 16.y == 12.y
# 
# - E 0 ) 7.y == 21.y ; 8.y == 22.y
# - E 1 ) 15.y == ( dist(11,13) + dist(13,15)) + 11.y  ;  16.y == ( dist(12,14) + dist(14,16)) + 12.y
# 



def is_angled(cdt,dict_id):
    
    
    if(cdt == "a1") and dict_id[11] and dict_id[13] and dict_id[15] :
        target = 80
        a1 = dict_id[11]
        a2 = dict_id[13]
        a3 = dict_id[15]
        
    if(cdt == "a2") and dict_id[12] and dict_id[14] and dict_id[16] :
        target = 80
        a1 = dict_id[12]
        a2 = dict_id[14]
        a3 = dict_id[16]
        
        
    return abs(target - calculate_angle(a1,a2,a3)) <= 5 ,  calculate_angle(a1,a2,a3)
    
    



def E0(dict_id):
    if dict_id[7] and dict_id[8] and dict_id[21] and dict_id[22]:
        
        return abs(dict_id[7]["y"] - dict_id[21]["y"]) <= 60 and abs(dict_id[8]["y"] - dict_id[22]["y"]) <= 60
    else :
        return False
        
    



def E1(dict_id,lenght1, lenght2):
    if dict_id[15] and dict_id[16]  :
        # print(dict_id[15]["y"])
        # print(lenght1)
        
        return abs(dict_id[15]["y"] - lenght1) <= 10 and abs(dict_id[16]["y"] - lenght2) <= 10


def angled_line(dict_id) :
    
    
    if dict_id[11] and dict_id[13] and dict_id[14] and dict_id[12] :
        y11 = int(dict_id[11]["y"])
        x11 = int(dict_id[11]["x"])
                    
        y13 = int(dict_id[13]["y"])
        x13 = int(dict_id[13]["x"])
                    
        y14 = int(dict_id[14]["y"])
        x14 = int(dict_id[14]["x"])
                    
        y12 = int(dict_id[12]["y"])
        x12 = int(dict_id[12]["x"])
                    
        angle_1113 = math.atan2(y13 - y11, x13 - x11)
        # Convertir alpha en radians et ajuster pour l'inversion de l'axe y
        alpha_rad = 80
        # Calculer le nouvel angle
        new_angle = angle_1113 + alpha_rad

        # Calculer les nouvelles coordonnées du point C à une distance length de A
        Cx = int( x13 - 500 * math.cos(new_angle * 3.14 /180) )
        Cy = int( y13 - 500 * math.sin(new_angle *3.14 /180)  )# Soustraction due à l'inversion de l'axe y

                
        angle_1214 = math.atan2(y14 - y12, x14 - x12)
        # Calculer le nouvel angle
        new_angle_2 =  -(angle_1214 + alpha_rad)
                    
        xa2 = int( x14 + 500 * math.cos((new_angle_2 ) * 3.14 / 180))
        ya2 = int( y14 + 500 * math.sin((new_angle_2 ) * 3.14 /180))
        
        return (x13,y13),(Cx, Cy ), (x14,y14) , (xa2, ya2 )  
      
    else : 
         
        return None, None, None , None 
    




class StateMachine:
    states = ['A', 'B', 'C']

    def __init__(self):
        self.machine = Machine(model=self, states=StateMachine.states, initial='A')
        self.machine.add_transition(trigger='to_B', source='A', dest='B')
        self.machine.add_transition(trigger='to_A', source='B', dest='A')
        self.machine.add_transition(trigger='to_C', source='B', dest='C')





def track(nbRep):
    cap = cv2.VideoCapture(0)
    
    nb = 0
    text = f'0 / {nbRep}'
    dict_id = {
        7 : None,
        8 : None,
        21 : None,
        22 : None,
        11 : None,
        13 : None,
        15 : None,
        12 : None,
        14 : None,
        16 : None,
    }
    
    
    
    machine = StateMachine()
    
    lenght = None
   

    while cap.isOpened():
        
       
        
        # Couleur du cercle en BGR (Bleu, Vert, Rouge)
        colorA1,colorA2 = (255, 0, 0) , (255, 0, 0) # Un cercle bleu
        ret, frame = cap.read()
       
        if not ret:
            continue
        
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            for id, lm in enumerate(results.pose_landmarks.landmark):
                height, width, _ = frame.shape
                x, y = int(lm.x * width), int(lm.y * height)
                cv2.putText(frame, str(id), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                if lm.visibility >= 0.90:
                    p = {
                        'x' : None,
                        'y' : None,
                    }
                    p['x'] = x
                    p['y'] = y
                    dict_id[id] = p
                    
            
            #Update the lenght only on state A and C (so it don't change during state B)
            if machine.state == "A" or machine.state == "C":
                if dict_id[11] and dict_id[12] and dict_id[13] and dict_id[15]  :
            
                    lenght = int( calculate_dist(dict_id[11], dict_id[13], dict_id[15]) )
                    
                    
                    
                        
            if dict_id[11] and dict_id[12] :
                #Bottom Line
                y11 = int(dict_id[11]["y"])
                y12 = int(dict_id[12]["y"])
                
                cv2.line(frame,(0, y11  ),(width, y12 ),(255,0,0),2)
                
                if lenght != None :
                    #Top Line
                    #lenght = lenght of the arm
                    cv2.line(frame,(0,  -(lenght - y12) + 15 ),(width, -( lenght - y11) +15),(255,0,0),2)
            
            
            
            #If hand at head levels
            if E0(dict_id) and machine.state == "A" or machine.state == "C":
                
                #Correct angle
                
                pos13,pos13bis, pos14 , pos14bis  = angled_line(dict_id)
                
                if pos13 != None :
                    cv2.line(frame,pos13,pos13bis,colorA1,2)
                    cv2.line(frame,pos14,pos14bis,colorA2,2)
                
                
                #A1
                a1 , angle1 = is_angled("a1",dict_id)
                
                if a1 :
                    colorA1 = (0, 255, 0)  # Un cercle vert
                   
                else :
                    colorA1 = (0,0,255)
                    
                #A2
                a2, angle2 = is_angled("a2",dict_id)
                
                if a2 :
                    colorA2 =(0, 255, 0)
                    
                else :
                    colorA2 = (0,0,255)
                
                if a1 and a2 :
                    machine.to_B()
                
                
            
            
            #If hands on upper bound
            if lenght != None :
                if E1(dict_id, -(lenght - y11) + 15 , -(lenght - y12) + 15 ) and machine.state == "B" :
                    
                    machine.to_C()
                    nb += 1
                    text = f"{nb} / {nbRep}"
                    
              
            
    
        #Circles
        if dict_id[13] :
            cv2.circle(frame, (dict_id[13]["x"],dict_id[13]["y"]), 20, colorA1, 2)
        if dict_id[14] :
            cv2.circle(frame, (dict_id[14]["x"],dict_id[14]["y"]), 20, colorA2, 2)
            
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 400)
        fontScale = 1
        fontColor = (102, 0, 255)
        lineType = 2
        
        
        
              
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        frame = cv2.flip(frame,1)
        cv2.putText(frame, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        
        
        if nb >= nbRep :
            break
        
        
        frame_resized = cv2.resize(frame, (frame.shape[1] * 2, frame.shape[0] * 2))
    
        cv2.imshow("Pose Tracking", frame_resized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
   
    



def start():
    # lenght = None
    # while lenght == None :
    #     lenght=  calibrate() 
    
    track(10)
    

