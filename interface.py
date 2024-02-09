import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QComboBox,QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

from pose_test import StateMachine, track
import cv2 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pose Demo")
        self.resize(800, 600)

        # Création de la liste déroulante (QComboBox)
        self.comboBox = QComboBox()
        # Ajout des choix dans la comboBox. Ici, nous ajoutons des entiers sous forme de texte.
        for i in range(1, 16):  # Ajoute les nombres de 1 à 10 comme choix
            self.comboBox.addItem(str(i), i)

        # Création du bouton
        self.button = QPushButton("Lancer OpenCV")
        self.button.clicked.connect(self.onButtonClicked)  # Connecte le bouton à la méthode onButtonClicked

        #Qlabel
        self.imageLabel = QLabel()
        self.imageLabel.resize(640,480)
        
        
        # Configuration du layout
        layout = QVBoxLayout()
        layout.addWidget(self.comboBox)
        layout.addWidget(self.button)
        layout.addWidget(self.imageLabel)


        # Configuration du widget central
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        
        
        self.cap = None
        self.machine = StateMachine()  # Initialisez votre machine à états ici
        self.nbRep = 0
        self.dict_id = {
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
        self.nb = 0
        self.lenght = None

    def onButtonClicked(self):
        
        self.nbRep = int(self.comboBox.currentText())  # Convertit le texte sélectionné en entier
        if not self.cap:
            
            self.cap = cv2.VideoCapture(0)
            self.start_track()
        
    def start_track(self):
        self.nb = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_track)
        self.timer.start(50)
        
    def update_track(self):
        
        ret, frame = self.cap.read()
        if ret:
          
            frame, self.nb, self.lenght, state = track(frame,self.nbRep,self.machine,self.dict_id,self.nb,self.lenght)
            
            if state == "End" :
                
                self.timer.stop()
                self.cap.release()
                self.cap = None
                
            else :
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, _ = frame.shape
                bytes_per_line = 3 * width
                qImg = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.width(), self.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
