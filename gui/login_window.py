from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                              QVBoxLayout, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys

from src.crud import get_utilisateur_by_email


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.utilisateur_connecte = None
        self.tentatives = 0
        self.init_ui()

    def init_ui(self):
        # Configuration de la fenêtre
        self.setWindowTitle("Archive Digitale PFA - Connexion")
        self.setFixedSize(400, 350)

        # Layout principal vertical
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        # Titre
        titre = QLabel("Archive Digitale PFA")
        titre.setAlignment(Qt.AlignCenter)
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titre)

        sous_titre = QLabel("Connexion à votre espace")
        sous_titre.setAlignment(Qt.AlignCenter)
        sous_titre.setStyleSheet("color: gray;")
        layout.addWidget(sous_titre)

        layout.addSpacing(20)

        # Champ Email
        layout.addWidget(QLabel("Email :"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@ecole.ma")
        self.email_input.setFixedHeight(35)
        layout.addWidget(self.email_input)

        # Champ Mot de passe
        layout.addWidget(QLabel("Mot de passe :"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setFixedHeight(35)
        layout.addWidget(self.password_input)

        layout.addSpacing(10)

        # Bouton Se connecter
        self.btn_connecter = QPushButton("Se connecter")
        self.btn_connecter.setFixedHeight(40)
        self.btn_connecter.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1d7ba6;
            }
        """)
        self.btn_connecter.clicked.connect(self.tenter_connexion)
        layout.addWidget(self.btn_connecter)

        # Permettre de valider avec Entrée
        self.password_input.returnPressed.connect(self.tenter_connexion)

        self.setLayout(layout)

    def tenter_connexion(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        # Validation des champs vides
        if not email or not password:
            QMessageBox.warning(self, "Champs manquants",
                                "Veuillez remplir tous les champs.")
            return

        # Vérification dans la base
        user = get_utilisateur_by_email(email)

        if user is None:
            QMessageBox.warning(self, "Compte introuvable",
                                "Compte introuvable, contactez l'administrateur.")
            return

        from src.security import verifier_mot_de_passe
        if not verifier_mot_de_passe(password, user['mot_de_passe']):
            self.tentatives += 1
            restantes = 3 - self.tentatives
            if restantes > 0:
                QMessageBox.warning(self, "Mot de passe incorrect",
                                    f"Mot de passe incorrect.\n"
                                    f"Tentatives restantes : {restantes}")
            else:
                QMessageBox.critical(self, "Compte bloqué",
                                     "Trop de tentatives. Compte bloqué temporairement.")
                self.btn_connecter.setEnabled(False)
            return

        # Connexion réussie
        self.utilisateur_connecte = user
        self.ouvrir_fenetre_principale(user)

    def ouvrir_fenetre_principale(self, utilisateur):
        """Ouvre la fenêtre principale et cache la fenêtre de connexion."""
        from gui.main_window import MainWindow
        self.main_window = MainWindow(dict(utilisateur), login_window=self)
        self.main_window.show()
        self.hide()


# Pour tester la fenêtre seule
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())