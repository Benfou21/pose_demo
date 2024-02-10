import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QComboBox,QLabel,QGridLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont ,QPen

from pose_test import StateMachine, track
import cv2 
import numpy as np





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Démo")
        self.resize(800, 600)

        # Création de la liste déroulante (QComboBox)
        self.comboBox = QComboBox()
        
        # Ajout des choix dans la comboBox. Ici, nous ajoutons des entiers sous forme de texte.
        for i in range(1, 16):  # Ajoute les nombres de 1 à 10 comme choix
            self.comboBox.addItem(str(i), i)

        # Création du bouton
        self.button = QPushButton("Lancer")
        self.button.clicked.connect(self.onButtonClicked)  # Connecte le bouton à la méthode onButtonClicked

        #Bouton vidéo
        self.launchVideoButton = QPushButton("Vidéo démo")
        self.launchVideoButton.clicked.connect(self.launchVideo)
       
        
        #Qlabel
        self.imageLabel = QLabel()
        self.imageLabel.resize(640,480)
        
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.imageLabel, 0, 0, 1, 2)  # Row 0, Col 0, Span 1 row, Span 2 cols
        gridLayout.addWidget(self.comboBox, 1, 0)  # Row 1, Col 0
        gridLayout.addWidget(self.button, 1, 1)  # Row 1, Col 1
        gridLayout.addWidget(self.launchVideoButton, 2, 1)  # Row 2, Col 1

        # Configuration du layout
        # layout = QVBoxLayout()
        # layout.addWidget(self.comboBox)
        # layout.addWidget(self.button)
        # layout.addWidget(self.imageLabel)
        # layout.addWidget(self.launchVideoButton)


        # Configuration du widget central
        centralWidget = QWidget()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        
        
        self.cap = None
        self.video = None
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

        # self.fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec
        # self.out = cv2.VideoWriter('demo.avi', self.fourcc, 20.0, (640, 480))  # Nom de fichier, codec, FPS, résolution
        # Dans __init__ de MainWindow, ajoutez un nouveau bouton pour lancer la vidéo
        

        self.timer = QTimer(self)

        
    def onButtonClicked(self):
        
        self.nbRep = int(self.comboBox.currentText())  # Convertit le texte sélectionné en entier
        
        self.start_track()
        
        
        
    def start_track(self):
        
        if self.timer.isActive():
            self.timer.timeout.disconnect()
            self.timer.stop()
        if self.cap:
            self.cap.release()
        if self.video:
            self.video.release()
            self.video = None
            
        self.cap = cv2.VideoCapture(0)
        self.nb = 0
        # self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_track)
        self.timer.start(50)
        
    def launchVideo(self):
        
        # Assurez-vous d'arrêter la capture et le timer actuels s'ils sont en cours
        if self.timer.isActive():
            self.timer.timeout.disconnect()
            self.timer.stop()
        if self.video:
            self.video.release()
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # Ouvrir le fichier vidéo
        self.video = cv2.VideoCapture('demo.avi')
        
        
        if not self.video.isOpened():
            print("Erreur : Impossible d'ouvrir la vidéo.")
            return
        
        # Réinitialiser et démarrer le timer pour lire la vidéo
        
        self.timer.timeout.connect(self.updateVideoFrame)
        self.timer.start(50)  # Ajustez selon le FPS de votre vidéo
    
    
    def updateVideoFrame(self):
        ret, frame = self.video.read()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, _ = frame.shape
            bytes_per_line = 3 * width
            qImg = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            
            
            painter = QPainter(pixmap)
            painter.setPen(QColor("yellow"))
            painter.setFont(QFont("Arial", 20))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignHCenter, "Démo de l'exercice")
            painter.end()
        
        
            self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.width(), self.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))
        else:
            print("Fin de la vidéo ou erreur de lecture.")
            self.timer.stop()
            self.cap.release()
            self.imageLabel.clear()  # Efface le contenu du QLabel
            self.imageLabel.setText("La vidéo est terminée.")


    
    def update_track(self):
        
        ret, frame = self.cap.read()
        
        if ret:
            
            
            frame, self.nb, self.lenght, state, self.machine.state = track(frame,self.nbRep,self.machine,self.dict_id,self.nb,self.lenght)
            
            
            
            if state == "End" :
                
                #self.out.release() #End recording 
                self.timer.stop()
                self.cap.release()
                self.machine.state = "A"
                
                pixmap = QPixmap(self.imageLabel.size())  # Crée un QPixmap de la taille du QLabel
                pixmap.fill(QColor("green"))  # Remplit le QPixmap avec une couleur de fond
                painter = QPainter(pixmap)
                painter.setPen(QColor("white"))
                painter.setFont(QFont("Arial", 20))
                text = "L'exercice est terminée."
                
                # Calcule la position du texte pour le centrer
                textRect = painter.fontMetrics().boundingRect(text)
                textX = ( pixmap.width() - textRect.width()) / 2
                textY = (pixmap.height() - textRect.height()) / 2
                painter.drawText(int(textX), int(textY), text)
                painter.end()
                
                self.imageLabel.setPixmap(pixmap)
                
                
                
            
            
            else :
                
                color = QColor("Blue")
                message = ""
                
                if self.machine.state == "B" :
                    
                    message = "Montez"
                    color = QColor("Orange")
                    
                    
                if self.machine.state == "C" :
                    
                    message = "Descendez"
                    color = QColor("yellow")
                    
                    
                
                    
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, _ = frame.shape
                bytes_per_line = 3 * width
                qImg = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                
                
                painter = QPainter(pixmap)
                pen = QPen()
                pen.setWidth(1)
                pen.setColor(color)
                painter.setPen(pen)
                font = QFont()
                font.setFamily("Times")
                font.setPointSize((20))
                painter.setFont(font)
                painter.drawText(50, 100, message)
                painter.end()
                
                # #Conversion Pixmap to image
                # qImg = pixmap.toImage()
                # qImg = qImg.convertToFormat(QImage.Format.Format_RGB888)
                # ptr = qImg.bits()
                # ptr.setsize(qImg.sizeInBytes())  # Ajustement pour PyQt6
                # arr = np.array(ptr).reshape(qImg.height(), qImg.width(), 3)

                # # Convertir de RGB (PyQt) à BGR (OpenCV)
                # arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

                # self.out.write(arr_bgr) #Recording
                
                # Mettre à jour le QLabel avec le QPixmap qui a maintenant du texte dessus
                self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.width(), self.imageLabel.height(), Qt.AspectRatioMode.KeepAspectRatio))



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
