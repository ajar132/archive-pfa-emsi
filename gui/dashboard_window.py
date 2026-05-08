from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                              QGridLayout, QFrame, QGroupBox, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.crud import get_statistiques


class DashboardWindow(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.init_ui()
        self.charger_statistiques()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Titre + bouton refresh sur la même ligne
        titre_layout = QHBoxLayout()

        titre = QLabel("📊 Tableau de bord")
        titre.setFont(QFont("Arial", 22, QFont.Bold))
        titre_layout.addWidget(titre)

        titre_layout.addStretch()  # pousse le bouton à droite

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setFixedWidth(140)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1d7ba6;
            }
            QPushButton:pressed {
                background-color: #0d4863;
            }
        """)
        btn_refresh.clicked.connect(self.charger_statistiques)
        titre_layout.addWidget(btn_refresh)

        layout.addLayout(titre_layout)

        sous_titre = QLabel(f"Statistiques globales — Connecté en tant que : "
                             f"{self.utilisateur['role'].capitalize()}")
        sous_titre.setStyleSheet("color: gray; font-size: 13px;")
        layout.addWidget(sous_titre)

        layout.addSpacing(10)

        # ─── Cartes de statistiques ───
        self.cartes_layout = QGridLayout()
        self.cartes_layout.setSpacing(15)
        layout.addLayout(self.cartes_layout)

        layout.addSpacing(20)

        # ─── Section graphique ───
        groupe_graph = QGroupBox("📈 Répartition des rapports par statut")
        groupe_graph.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        graph_layout = QVBoxLayout()

        # Création de la figure matplotlib
        self.figure = Figure(figsize=(8, 4), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)

        groupe_graph.setLayout(graph_layout)
        layout.addWidget(groupe_graph)

        layout.addStretch()
        self.setLayout(layout)

    def charger_statistiques(self):
        """Récupère les stats et met à jour l'affichage."""
        stats = get_statistiques()

        # Définir les cartes (titre, valeur, couleur, icône)
        cartes_data = [
            ("Total des rapports",  stats['total'],    "#34495e", "📚"),
            ("Soumis",              stats['soumis'],   "#f39c12", "📥"),
            ("En cours",            stats['en_cours'], "#3498db", "⏳"),
            ("Évalués",             stats['evalues'],  "#27ae60", "✅"),
            ("Archivés",            stats['archives'], "#95a5a6", "📦"),
            ("Rejetés",             stats['rejetes'],  "#e74c3c", "❌"),
        ]

        # Vider d'abord les anciennes cartes (si on rafraîchit)
        for i in reversed(range(self.cartes_layout.count())):
            widget = self.cartes_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Afficher les cartes en grille 2x3
        for index, (titre, valeur, couleur, icone) in enumerate(cartes_data):
            row = index // 3
            col = index % 3
            carte = self.creer_carte(titre, valeur, couleur, icone)
            self.cartes_layout.addWidget(carte, row, col)

        # Mettre à jour le graphique
        self.dessiner_graphique(stats)

    def creer_carte(self, titre, valeur, couleur, icone):
     """Crée une carte de statistique colorée."""
     carte = QFrame()
     carte.setFixedHeight(130)   # ← augmenté de 110 à 130
     carte.setStyleSheet(f"""
        QFrame {{
            background-color: {couleur};
            border-radius: 10px;
        }}
        QLabel {{
            color: white;
            background-color: transparent;
        }}
    """)

     carte_layout = QVBoxLayout()
     carte_layout.setContentsMargins(20, 12, 20, 12)   # ← marges réduites
     carte_layout.setSpacing(5)                         # ← espacement réduit

    # Ligne du haut : icône + titre
     haut_layout = QHBoxLayout()
     label_icone = QLabel(icone)
     label_icone.setFont(QFont("Segoe UI", 22))

     label_titre = QLabel(titre)
     label_titre.setFont(QFont("Segoe UI", 11))
     label_titre.setStyleSheet("color: rgba(255,255,255,0.9);")

     haut_layout.addWidget(label_icone)
     haut_layout.addWidget(label_titre, stretch=1)
     carte_layout.addLayout(haut_layout)

    # Valeur — taille un peu réduite pour bien tenir
     label_valeur = QLabel(str(valeur))
     label_valeur.setFont(QFont("Segoe UI", 24, QFont.Bold))   # ← 28 → 24
     label_valeur.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
     label_valeur.setStyleSheet("color: white; padding-right: 5px;")
     carte_layout.addWidget(label_valeur)

     carte.setLayout(carte_layout)
     return carte

    def dessiner_graphique(self, stats):
        """Dessine un camembert de la répartition des statuts."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Préparer les données (exclure les statuts à 0)
        labels = []
        values = []
        couleurs = []
        mapping = [
            ("Soumis",   stats['soumis'],   "#f39c12"),
            ("En cours", stats['en_cours'], "#3498db"),
            ("Évalués",  stats['evalues'],  "#27ae60"),
            ("Archivés", stats['archives'], "#95a5a6"),
            ("Rejetés",  stats['rejetes'],  "#e74c3c"),
        ]

        for label, valeur, couleur in mapping:
            if valeur > 0:
                labels.append(f"{label} ({valeur})")
                values.append(valeur)
                couleurs.append(couleur)

        if not values:
            ax.text(0.5, 0.5, "Aucune donnée à afficher",
                    ha='center', va='center', fontsize=14, color='gray',
                    transform=ax.transAxes)
            ax.axis('off')
        else:
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                colors=couleurs,
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2},
                textprops={'fontsize': 10}
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            ax.axis('equal')

        self.figure.tight_layout()
        self.canvas.draw()