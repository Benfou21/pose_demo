import cv2
import mediapipe as mp
import math
import time
import numpy as np




def calculate_angle(landmark1, landmark2, landmark3):
    # Calculer l'angle formé par trois points de repère
    a = math.sqrt((landmark2["x"] - landmark1["x"]) ** 2 + (landmark2["y"] - landmark1["y"]) ** 2)
    b = math.sqrt((landmark2["x"] - landmark3["x"]) ** 2 + (landmark2["y"] - landmark3["y"]) ** 2)
    c = math.sqrt((landmark3["x"] - landmark1["x"]) ** 2 + (landmark3["y"] - landmark1["y"]) ** 2)
    angle = math.acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))
    return math.degrees(angle)



def calculate_dist(lm1, lm2, lm3):
    # Calcul de la distance entre lm1 et lm2
    dist1 = math.sqrt((lm2["x"] - lm1["x"])**2 + (lm2["y"] - lm1["y"])**2)

    # Calcul de la distance entre lm2 et lm3
    dist2 = math.sqrt((lm3["x"] - lm2["x"])**2 + (lm3["y"] - lm2["y"])**2)

    # Addition des deux distances
    total_dist = dist1 + dist2

    return total_dist