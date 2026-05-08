from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout,
                              QHBoxLayout, QScrollArea, QWidget, QSpinBox,
                              QMessageBox, QSlider)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage
import fitz  # PyMuPDF


class PreviewWindow(QDialog):
    def __init__(self, chemin_pdf, titre_rapport=""):
        super().__init__()
        self.chemin_pdf = chemin_pdf
        self.titre_rapport = titre_rapport
        self.doc = None
        self.page_actuelle = 0
        self.zoom = 1.5  # zoom par défaut

        self.init_ui()
        self.charger_pdf()

    def init_ui(self):
        self.setWindowTitle(f"👁️ Prévisualisation - {self.titre_rapport}")
        self.setGeometry(150, 100, 900, 800)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ─── Barre d'outils en haut ───
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Boutons de navigation
        self.btn_premier = QPushButton("⏮️ Première")
        self.btn_premier.clicked.connect(self.aller_premiere)

        self.btn_precedent = QPushButton("◀️ Précédente")
        self.btn_precedent.clicked.connect(self.page_precedente)

        # Indicateur de page
        self.label_page = QLabel("Page 0 / 0")
        self.label_page.setAlignment(Qt.AlignCenter)
        self.label_page.setFixedWidth(120)
        self.label_page.setStyleSheet("font-weight: bold; padding: 5px;")

        self.btn_suivant = QPushButton("Suivante ▶️")
        self.btn_suivant.clicked.connect(self.page_suivante)

        self.btn_dernier = QPushButton("Dernière ⏭️")
        self.btn_dernier.clicked.connect(self.aller_derniere)

        # Saut direct à une page
        self.spin_page = QSpinBox()
        self.spin_page.setMinimum(1)
        self.spin_page.setFixedWidth(60)
        self.spin_page.valueChanged.connect(self.aller_a_page)

        toolbar.addWidget(self.btn_premier)
        toolbar.addWidget(self.btn_precedent)
        toolbar.addWidget(self.label_page)
        toolbar.addWidget(self.btn_suivant)
        toolbar.addWidget(self.btn_dernier)
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Aller à :"))
        toolbar.addWidget(self.spin_page)

        layout.addLayout(toolbar)

        # ─── Slider de zoom ───
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("🔍 Zoom :"))

        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setMinimum(50)   # 50%
        self.slider_zoom.setMaximum(300)  # 300%
        self.slider_zoom.setValue(150)    # 150% par défaut
        self.slider_zoom.valueChanged.connect(self.changer_zoom)

        self.label_zoom = QLabel("150%")
        self.label_zoom.setFixedWidth(50)

        zoom_layout.addWidget(self.slider_zoom)
        zoom_layout.addWidget(self.label_zoom)
        layout.addLayout(zoom_layout)

        # ─── Zone d'affichage PDF (scrollable) ───
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("background-color: #2c3e50;")

        self.label_pdf = QLabel()
        self.label_pdf.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.label_pdf)

        layout.addWidget(self.scroll_area)

        # ─── Bouton fermer ───
        btn_fermer = QPushButton("✖️ Fermer")
        btn_fermer.setFixedWidth(150)
        btn_fermer.setFixedHeight(35)
        btn_fermer.clicked.connect(self.close)

        bas_layout = QHBoxLayout()
        bas_layout.addStretch()
        bas_layout.addWidget(btn_fermer)
        bas_layout.addStretch()
        layout.addLayout(bas_layout)

        self.setLayout(layout)

    def charger_pdf(self):
        """Ouvre le PDF avec PyMuPDF."""
        try:
            self.doc = fitz.open(self.chemin_pdf)
            nb_pages = len(self.doc)
            self.spin_page.setMaximum(nb_pages)
            self.spin_page.setValue(1)
            self.afficher_page()
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Impossible d'ouvrir le PDF :\n{e}")
            self.close()

    def afficher_page(self):
        """Affiche la page actuelle dans le QLabel."""
        if not self.doc:
            return

        # Récupérer la page
        page = self.doc[self.page_actuelle]

        # Convertir en image avec le zoom
        matrice_zoom = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=matrice_zoom)

        # Conversion vers QImage puis QPixmap
        img = QImage(pix.samples, pix.width, pix.height,
                     pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)

        # Affichage
        self.label_pdf.setPixmap(pixmap)
        self.label_pdf.resize(pixmap.size())

        # Mise à jour de l'indicateur de page
        self.label_page.setText(f"Page {self.page_actuelle + 1} / {len(self.doc)}")

        # Mise à jour des boutons (désactiver si début/fin)
        self.btn_premier.setEnabled(self.page_actuelle > 0)
        self.btn_precedent.setEnabled(self.page_actuelle > 0)
        self.btn_suivant.setEnabled(self.page_actuelle < len(self.doc) - 1)
        self.btn_dernier.setEnabled(self.page_actuelle < len(self.doc) - 1)

    # ─── Navigation ───
    def aller_premiere(self):
        self.page_actuelle = 0
        self.spin_page.blockSignals(True)
        self.spin_page.setValue(1)
        self.spin_page.blockSignals(False)
        self.afficher_page()

    def page_precedente(self):
        if self.page_actuelle > 0:
            self.page_actuelle -= 1
            self.spin_page.blockSignals(True)
            self.spin_page.setValue(self.page_actuelle + 1)
            self.spin_page.blockSignals(False)
            self.afficher_page()

    def page_suivante(self):
        if self.doc and self.page_actuelle < len(self.doc) - 1:
            self.page_actuelle += 1
            self.spin_page.blockSignals(True)
            self.spin_page.setValue(self.page_actuelle + 1)
            self.spin_page.blockSignals(False)
            self.afficher_page()

    def aller_derniere(self):
        if self.doc:
            self.page_actuelle = len(self.doc) - 1
            self.spin_page.blockSignals(True)
            self.spin_page.setValue(self.page_actuelle + 1)
            self.spin_page.blockSignals(False)
            self.afficher_page()

    def aller_a_page(self, num):
        """Saute directement à la page demandée."""
        if self.doc and 1 <= num <= len(self.doc):
            self.page_actuelle = num - 1
            self.afficher_page()

    def changer_zoom(self, valeur):
        """Change le niveau de zoom."""
        self.zoom = valeur / 100.0
        self.label_zoom.setText(f"{valeur}%")
        self.afficher_page()

    def closeEvent(self, event):
        """Ferme proprement le document PDF."""
        if self.doc:
            self.doc.close()
        event.accept()