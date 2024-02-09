import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,QComboBox,QLabel
from pose_test import track



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

        # Configuration du widget central
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        
        self.cap = None

    def onButtonClicked(self):
        choice = self.comboBox.currentData()  # Récupère la donnée courante sélectionnée dans la comboBox, ici un entier
        track(choice)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
