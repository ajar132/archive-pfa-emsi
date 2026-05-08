from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton,
                              QVBoxLayout, QHBoxLayout, QStackedWidget,
                              QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainWindow(QMainWindow):
    def __init__(self, utilisateur, login_window=None):
        super().__init__()
        self.utilisateur = utilisateur  # dict avec id, nom, role, etc.
        self.login_window = login_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Archive Digitale PFA - {self.utilisateur['nom']}")
        self.setGeometry(100, 100, 1100, 700)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)

        # Layout horizontal : sidebar à gauche, contenu à droite
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Construction de la sidebar
        sidebar = self.creer_sidebar()
        main_layout.addWidget(sidebar)

        # Zone de contenu (changera selon le menu cliqué)
        self.zone_contenu = QStackedWidget()
        self.zone_contenu.setStyleSheet("background-color: #f5f5f5;")
        main_layout.addWidget(self.zone_contenu, stretch=1)

        # Page d'accueil par défaut
        self.afficher_accueil()

        central.setLayout(main_layout)

    def creer_sidebar(self):
        """Crée la barre latérale avec menu adapté au rôle."""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #156082;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 12px 20px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1d7ba6;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # En-tête : nom et rôle
        header = QFrame()
        header.setStyleSheet("background-color: #0d4863;")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 25, 20, 25)

        nom_label = QLabel(self.utilisateur['nom'])
        nom_label.setFont(QFont("Arial", 13, QFont.Bold))

        role_label = QLabel(f"🔹 {self.utilisateur['role'].capitalize()}")
        role_label.setStyleSheet("color: #b3d4e0; font-size: 12px;")

        header_layout.addWidget(nom_label)
        header_layout.addWidget(role_label)
        header.setLayout(header_layout)
        layout.addWidget(header)

        # Boutons du menu — adaptés au rôle
        role = self.utilisateur['role']

        # Tout le monde voit ces options
        layout.addWidget(self.creer_bouton_menu("🏠  Accueil", self.afficher_accueil))
        layout.addWidget(self.creer_bouton_menu("🔍  Rechercher", self.afficher_recherche))

        # Administrateur uniquement
        if role == 'administrateur':
            layout.addWidget(self.creer_bouton_menu("📤  Déposer un rapport", self.afficher_depot))
            layout.addWidget(self.creer_bouton_menu("👥  Gérer utilisateurs", self.afficher_gestion_users))

        # Encadrant
        if role == 'encadrant':
            layout.addWidget(self.creer_bouton_menu("✅  Mes évaluations", self.afficher_evaluations))

        # Encadrant et administrateur ont accès au tableau de bord
        if role in ('encadrant', 'administrateur'):
            layout.addWidget(self.creer_bouton_menu("📊  Tableau de bord", self.afficher_dashboard))

        # Espace flexible pour pousser "Déconnexion" en bas
        layout.addStretch()

        # Bouton de déconnexion
        btn_deco = self.creer_bouton_menu("🚪  Déconnexion", self.deconnexion)
        btn_deco.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ff9999;
                border: none;
                padding: 12px 20px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                color: white;
            }
        """)
        layout.addWidget(btn_deco)

        sidebar.setLayout(layout)
        return sidebar

    def creer_bouton_menu(self, texte, fonction):
        """Crée un bouton de menu standardisé."""
        btn = QPushButton(texte)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(fonction)
        return btn

    # ─────────────────────────────────────────
    #  PAGES (placeholders pour l'instant)
    # ─────────────────────────────────────────

    def afficher_accueil(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        titre = QLabel(f"Bienvenue, {self.utilisateur['nom']} !")
        titre.setFont(QFont("Arial", 24, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)

        sous_titre = QLabel("Sélectionnez une option dans le menu de gauche.")
        sous_titre.setStyleSheet("color: gray; font-size: 14px;")
        sous_titre.setAlignment(Qt.AlignCenter)

        layout.addWidget(titre)
        layout.addWidget(sous_titre)
        page.setLayout(layout)

        self.changer_page(page)

    def afficher_recherche(self):
        from gui.recherche_window import RechercheWindow
        self.changer_page(RechercheWindow(self.utilisateur))

    def afficher_depot(self):
        from gui.depot_window import DepotWindow
        self.changer_page(DepotWindow())

    def afficher_gestion_users(self):
        from gui.users_window import UsersWindow
        self.changer_page(UsersWindow(self.utilisateur))
    def afficher_evaluations(self):
        from gui.evaluation_window import EvaluationWindow
        self.changer_page(EvaluationWindow(self.utilisateur))

    def afficher_dashboard(self):
        from gui.dashboard_window import DashboardWindow
        self.changer_page(DashboardWindow(self.utilisateur))

    def creer_page_placeholder(self, texte):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(texte)
        label.setFont(QFont("Arial", 18))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: gray;")
        layout.addWidget(label)
        page.setLayout(layout)
        return page

    def changer_page(self, nouvelle_page):
        """Remplace la page actuelle par une nouvelle."""
        # Supprimer la page actuelle
        while self.zone_contenu.count() > 0:
            widget = self.zone_contenu.widget(0)
            self.zone_contenu.removeWidget(widget)
            widget.deleteLater()
        # Ajouter la nouvelle
        self.zone_contenu.addWidget(nouvelle_page)

    def deconnexion(self):
        reponse = QMessageBox.question(self, "Déconnexion",
                                       "Voulez-vous vraiment vous déconnecter ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            if self.login_window:
                self.login_window.email_input.clear()
                self.login_window.password_input.clear()
                # Ne pas réinitialiser le compteur ni réactiver le bouton si le compte
                # est bloqué (3 tentatives échouées) — le blocage doit persister.
                if self.login_window.tentatives < 3:
                    self.login_window.tentatives = 0
                    self.login_window.btn_connecter.setEnabled(True)
                self.login_window.show()
            self.close()