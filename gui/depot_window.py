from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QComboBox, QSpinBox, QFileDialog, QMessageBox,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.crud import get_encadrants
from src.pdf_handler import deposer_rapport


class DepotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.chemin_pdf = None
        self.init_ui()
        self.charger_encadrants()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Titre
        titre = QLabel("📤 Déposer un nouveau rapport")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titre)

        # ─── Section 1 : Sélection du fichier PDF ───
        groupe_fichier = QGroupBox("1. Fichier PDF")
        groupe_fichier.setStyleSheet("QGroupBox { font-weight: bold; }")
        fichier_layout = QHBoxLayout()

        self.label_fichier = QLabel("Aucun fichier sélectionné")
        self.label_fichier.setStyleSheet("color: gray; padding: 5px;")

        btn_parcourir = QPushButton("📁 Parcourir...")
        btn_parcourir.setFixedHeight(35)
        btn_parcourir.setCursor(Qt.PointingHandCursor)
        btn_parcourir.clicked.connect(self.choisir_pdf)

        fichier_layout.addWidget(self.label_fichier, stretch=1)
        fichier_layout.addWidget(btn_parcourir)
        groupe_fichier.setLayout(fichier_layout)
        layout.addWidget(groupe_fichier)

        # ─── Section 2 : Métadonnées ───
        groupe_meta = QGroupBox("2. Métadonnées du rapport")
        groupe_meta.setStyleSheet("QGroupBox { font-weight: bold; }")
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.input_titre = QLineEdit()
        self.input_titre.setPlaceholderText("Ex: Système de gestion RH")
        self.input_titre.setFixedHeight(32)

        self.input_auteurs = QLineEdit()
        self.input_auteurs.setPlaceholderText("Ex: Ahmed Benali, Sara Alaoui")
        self.input_auteurs.setFixedHeight(32)

        self.input_promotion = QSpinBox()
        self.input_promotion.setRange(2000, 2050)
        self.input_promotion.setValue(2025)
        self.input_promotion.setFixedHeight(32)

        self.input_filiere = QLineEdit()
        self.input_filiere.setPlaceholderText("Ex: Génie Informatique")
        self.input_filiere.setFixedHeight(32)

        self.input_mots_cles = QLineEdit()
        self.input_mots_cles.setPlaceholderText("Ex: web, base de données, Python")
        self.input_mots_cles.setFixedHeight(32)

        # Combobox encadrants (Point 1 du prof)
        self.combo_encadrant = QComboBox()
        self.combo_encadrant.setFixedHeight(32)

        form_layout.addRow("Titre *:", self.input_titre)
        form_layout.addRow("Auteur(s) *:", self.input_auteurs)
        form_layout.addRow("Promotion *:", self.input_promotion)
        form_layout.addRow("Filière/Option:", self.input_filiere)
        form_layout.addRow("Mots-clés:", self.input_mots_cles)
        form_layout.addRow("Encadrant *:", self.combo_encadrant)

        groupe_meta.setLayout(form_layout)
        layout.addWidget(groupe_meta)

        # ─── Boutons d'action ───
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_annuler = QPushButton("Annuler")
        btn_annuler.setFixedHeight(40)
        btn_annuler.setFixedWidth(120)
        btn_annuler.clicked.connect(self.reinitialiser)

        btn_deposer = QPushButton("📤 Déposer le rapport")
        btn_deposer.setFixedHeight(40)
        btn_deposer.setFixedWidth(200)
        btn_deposer.setCursor(Qt.PointingHandCursor)
        btn_deposer.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1d7ba6; }
        """)
        btn_deposer.clicked.connect(self.valider_depot)

        btn_layout.addWidget(btn_annuler)
        btn_layout.addWidget(btn_deposer)
        layout.addLayout(btn_layout)

        # ─── Zone résultats similarité (CU08) ───
        self.groupe_similarite = QGroupBox("📊 Résultats d'analyse de similarité (CU08)")
        self.groupe_similarite.setStyleSheet("QGroupBox { font-weight: bold; }")
        sim_layout = QVBoxLayout()

        self.tableau_similarite = QTableWidget()
        self.tableau_similarite.setColumnCount(4)
        self.tableau_similarite.setHorizontalHeaderLabels(
            ["Titre", "Auteurs", "Promotion", "Similarité"])
        self.tableau_similarite.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableau_similarite.setMinimumHeight(150)

        sim_layout.addWidget(self.tableau_similarite)
        self.groupe_similarite.setLayout(sim_layout)
        self.groupe_similarite.setVisible(False)  # caché au début
        layout.addWidget(self.groupe_similarite)

        layout.addStretch()
        self.setLayout(layout)

    def charger_encadrants(self):
        """Remplit la liste déroulante avec les encadrants (Point 1 du prof)."""
        self.combo_encadrant.clear()
        encadrants = get_encadrants()
        if not encadrants:
            self.combo_encadrant.addItem("⚠️ Aucun encadrant en base", None)
            return
        self.combo_encadrant.addItem("-- Sélectionner un encadrant --", None)
        for e in encadrants:
            dep = e['departement'] if e['departement'] else 'N/A'
            label = f"{e['nom']} ({dep})"
            self.combo_encadrant.addItem(label, e['id'])  # stocke l'ID

    def choisir_pdf(self):
        """Ouvre une boîte de dialogue pour sélectionner un PDF."""
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier PDF",
            "",
            "Fichiers PDF (*.pdf)"
        )
        if fichier:
            self.chemin_pdf = fichier
            # Affiche juste le nom du fichier, pas le chemin complet
            import os
            nom = os.path.basename(fichier)
            self.label_fichier.setText(f"✅ {nom}")
            self.label_fichier.setStyleSheet("color: green; padding: 5px; font-weight: bold;")

    def valider_depot(self):
        """Lance le dépôt complet : copie + extraction + similarité + enregistrement."""
        # Validation des champs obligatoires
        if not self.chemin_pdf:
            QMessageBox.warning(self, "Fichier manquant",
                                "Veuillez sélectionner un fichier PDF.")
            return

        titre = self.input_titre.text().strip()
        auteurs = self.input_auteurs.text().strip()
        encadrant_id = self.combo_encadrant.currentData()

        if not titre:
            QMessageBox.warning(self, "Champ manquant", "Le titre est obligatoire.")
            return
        if not auteurs:
            QMessageBox.warning(self, "Champ manquant", "Les auteurs sont obligatoires.")
            return
        if encadrant_id is None:
            QMessageBox.warning(self, "Encadrant manquant",
                                "Veuillez sélectionner un encadrant.")
            return

        # Récupérer les autres champs
        promotion = self.input_promotion.value()
        filiere = self.input_filiere.text().strip()
        mots_cles = self.input_mots_cles.text().strip()

        # Lancer le dépôt complet
        try:
            rapport_id, resultats = deposer_rapport(
                self.chemin_pdf, titre, auteurs, encadrant_id,
                promotion, None, mots_cles  # option_id = None pour l'instant
            )

            if rapport_id is None:
                QMessageBox.critical(self, "Erreur", "Échec du dépôt.")
                return

            # Afficher les résultats de similarité
            self.afficher_resultats_similarite(resultats)

            QMessageBox.information(self, "Dépôt réussi",
                                    f"✅ Rapport déposé avec succès !\n\n"
                                    f"ID : {rapport_id}\n"
                                    f"Titre : {titre}\n"
                                    f"Statut : Soumis")

            # Réinitialiser le formulaire
            self.reinitialiser()

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Une erreur s'est produite :\n{str(e)}")

    def afficher_resultats_similarite(self, resultats):
        """Affiche le tableau de similarité (CU08)."""
        if not resultats:
            self.groupe_similarite.setVisible(False)
            return

        self.tableau_similarite.setRowCount(len(resultats))
        for i, r in enumerate(resultats):
            self.tableau_similarite.setItem(i, 0, QTableWidgetItem(r['titre']))
            self.tableau_similarite.setItem(i, 1, QTableWidgetItem(r['auteurs']))
            self.tableau_similarite.setItem(i, 2, QTableWidgetItem(str(r['promotion'])))

            # Cellule de similarité avec couleur selon le score
            score_item = QTableWidgetItem(f"{r['similarite']}%")
            if r['similarite'] >= 70:
                score_item.setBackground(Qt.red)
            elif r['similarite'] >= 40:
                score_item.setBackground(Qt.yellow)
            else:
                score_item.setBackground(Qt.green)
            self.tableau_similarite.setItem(i, 3, score_item)

        self.groupe_similarite.setVisible(True)

    def reinitialiser(self):
        """Vide tous les champs."""
        self.chemin_pdf = None
        self.label_fichier.setText("Aucun fichier sélectionné")
        self.label_fichier.setStyleSheet("color: gray; padding: 5px;")
        self.input_titre.clear()
        self.input_auteurs.clear()
        self.input_promotion.setValue(2025)
        self.input_filiere.clear()
        self.input_mots_cles.clear()
        self.combo_encadrant.setCurrentIndex(0)
        self.groupe_similarite.setVisible(False)
        self.tableau_similarite.setRowCount(0)