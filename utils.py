
import cv2
import mediapipe as mp
import math
import time
import numpy as np

from utils_math import calculate_dist
from utils_math import calculate_angle


# Initialisation de MediaPipe Pose.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()



def calibrate():
    dict_id = {
        11: None,
        13: None,
        15: None,
    }

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        height, width, _ = frame.shape
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            for id, lm in enumerate(results.pose_landmarks.landmark):
                
                x, y = int(lm.x * width), int(lm.y * height)

                if lm.visibility >= 0.90:
                    dict_id[id] = {'x': x, 'y': y}
                    
        cv2.putText(frame, "Levez les bras", (int(width/2 -100), 20 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("Calibration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or (dict_id[15] and dict_id[13] and dict_id[11]):
            break

    cap.release()
    cv2.destroyAllWindows()

    #return int( - ( dict_id[11]["y"] - calculate_dist(dict_id[11], dict_id[13], dict_id[15]) ) ), int(dict_id[11]["y"] ) , int(dict_id[12]["y"] )
    return int( calculate_dist(dict_id[11], dict_id[13], dict_id[15]) )






def capture_mouvement(a1,a2,a3):
    cap = cv2.VideoCapture(0)
    
    
    list_angle = []
    start_time = time.time()

    while cap.isOpened():
        text = ''
        p2, p1, p3 = None, None, None
        
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
                    
                    if id == a1: 
                        p1 = lm
                    elif id == a2:  
                        p2 = lm
                    elif id == a3:  
                        p3 = lm

            if p2 and p1 and p3:
                current_time = time.time()
                timing = current_time - start_time
                text = str(timing)
                #Calcul Angle
                angle = calculate_angle(p1, p2, p3)
                angle_text = str(int(angle))  # Arrondi à l'entier le plus proche et ajout du symbole degré

                #Affichage 
                x = (p1.x + p3.x) / 2
                y = (p1.y + p3.y) / 2

                x, y = int(x * width), int(y * height)

                cv2.putText(frame, angle_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (102, 0, 255), 2)
                    
                
                if timing >= 5:  # Capture l'angle toutes les 5 secondes
                    
                    list_angle.append(angle)
                
                    start_time = current_time

        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 400)
        fontScale = 1
        fontColor = (102, 0, 255)
        lineType = 2
        cv2.putText(frame, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow("Pose Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    return list_angle

