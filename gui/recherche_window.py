from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QSpinBox, QTableWidget, QTableWidgetItem,
                              QHeaderView, QGroupBox, QMessageBox,
                              QCheckBox, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.crud import rechercher_rapports


class RechercheWindow(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.rapport_selectionne = None
        self.init_ui()
        self.lancer_recherche()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        titre = QLabel("🔍 Rechercher un rapport")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titre)

        # ─── Critères ───
        groupe_criteres = QGroupBox("Critères de recherche (combinés par ET logique)")
        groupe_criteres.setStyleSheet("QGroupBox { font-weight: bold; }")
        criteres_layout = QFormLayout()
        criteres_layout.setSpacing(10)

        self.input_motcle = QLineEdit()
        self.input_motcle.setPlaceholderText("Ex: gestion, IA, web, base de données...")
        self.input_motcle.setFixedHeight(32)
        self.input_motcle.returnPressed.connect(self.lancer_recherche)

        promo_layout = QHBoxLayout()
        self.check_promotion = QCheckBox("Filtrer par promotion :")
        self.input_promotion = QSpinBox()
        self.input_promotion.setRange(2000, 2050)
        self.input_promotion.setValue(2025)
        self.input_promotion.setFixedHeight(32)
        self.input_promotion.setEnabled(False)
        self.check_promotion.toggled.connect(self.input_promotion.setEnabled)
        promo_layout.addWidget(self.check_promotion)
        promo_layout.addWidget(self.input_promotion)
        promo_layout.addStretch()

        criteres_layout.addRow("Mot-clé :", self.input_motcle)
        criteres_layout.addRow("", promo_layout)
        groupe_criteres.setLayout(criteres_layout)
        layout.addWidget(groupe_criteres)

        # ─── Boutons ───
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_reinit = QPushButton("🔄 Réinitialiser")
        btn_reinit.setFixedHeight(35)
        btn_reinit.setFixedWidth(150)
        btn_reinit.clicked.connect(self.reinitialiser)

        btn_chercher = QPushButton("🔍 Rechercher")
        btn_chercher.setFixedHeight(35)
        btn_chercher.setFixedWidth(150)
        btn_chercher.setCursor(Qt.PointingHandCursor)
        btn_chercher.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1d7ba6; }
        """)
        btn_chercher.clicked.connect(self.lancer_recherche)

        btn_layout.addWidget(btn_reinit)
        btn_layout.addWidget(btn_chercher)
        layout.addLayout(btn_layout)

        # ─── Tableau des résultats ───
        self.label_resultats = QLabel("Résultats :")
        self.label_resultats.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.label_resultats)

        self.tableau = QTableWidget()
        self.tableau.setColumnCount(6)
        self.tableau.setHorizontalHeaderLabels(
            ["ID", "Titre", "Auteurs", "Promotion", "Statut", "Date dépôt"])
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableau.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableau.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.setStyleSheet("""
            QTableWidget { background-color: white; }
            QTableWidget::item:selected { background-color: #156082; color: white; }
        """)
        self.tableau.itemSelectionChanged.connect(self.selection_changee)
        layout.addWidget(self.tableau)

        # ─── Boutons d'action ───
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_previsualiser = QPushButton("👁️ Prévisualiser")
        self.btn_previsualiser.setFixedHeight(38)
        self.btn_previsualiser.setEnabled(False)
        self.btn_previsualiser.clicked.connect(self.previsualiser_pdf)

        self.btn_telecharger = QPushButton("⬇️ Télécharger")
        self.btn_telecharger.setFixedHeight(38)
        self.btn_telecharger.setEnabled(False)
        self.btn_telecharger.clicked.connect(self.telecharger_pdf)

        self.btn_ouvrir = QPushButton("📂 Ouvrir avec lecteur PDF")
        self.btn_ouvrir.setFixedHeight(38)
        self.btn_ouvrir.setEnabled(False)
        self.btn_ouvrir.clicked.connect(self.ouvrir_pdf)

        action_layout.addWidget(self.btn_previsualiser)
        action_layout.addWidget(self.btn_telecharger)
        action_layout.addWidget(self.btn_ouvrir)
        layout.addLayout(action_layout)

        self.setLayout(layout)

    def lancer_recherche(self):
        mot_cle = self.input_motcle.text().strip() or None
        promotion = self.input_promotion.value() if self.check_promotion.isChecked() else None

        # Un étudiant ne peut consulter que les rapports officiellement archivés
        statut_filtre = 'Archivé' if self.utilisateur['role'] == 'etudiant' else None
        rapports = rechercher_rapports(mot_cle=mot_cle, promotion=promotion, statut_filtre=statut_filtre)

        nb = len(rapports)
        if nb == 0:
            self.label_resultats.setText("❌ Aucun document ne correspond à votre recherche.")
            self.label_resultats.setStyleSheet("color: #c0392b; font-weight: bold;")
        else:
            self.label_resultats.setText(f"✅ {nb} rapport(s) trouvé(s) :")
            self.label_resultats.setStyleSheet("color: #27ae60; font-weight: bold;")

        self.tableau.setRowCount(nb)
        for i, r in enumerate(rapports):
            self.tableau.setItem(i, 0, QTableWidgetItem(str(r['id'])))
            self.tableau.setItem(i, 1, QTableWidgetItem(r['titre']))
            self.tableau.setItem(i, 2, QTableWidgetItem(r['auteurs']))
            self.tableau.setItem(i, 3, QTableWidgetItem(str(r['promotion'])))

            statut_item = QTableWidgetItem(r['statut'])
            couleurs_statut = {
                'Soumis':   QColor("#f39c12"),
                'En cours': QColor("#3498db"),
                'Evalué':   QColor("#27ae60"),
                'Archivé':  QColor("#95a5a6"),
                'Rejeté':   QColor("#e74c3c"),
            }
            if r['statut'] in couleurs_statut:
                statut_item.setBackground(couleurs_statut[r['statut']])
                statut_item.setForeground(QColor("white"))
            self.tableau.setItem(i, 4, statut_item)

            self.tableau.setItem(i, 5, QTableWidgetItem(str(r['date_depot'])))

        self.rapport_selectionne = None
        self.activer_boutons_action(False)

    def reinitialiser(self):
        self.input_motcle.clear()
        self.check_promotion.setChecked(False)
        self.input_promotion.setValue(2025)
        self.lancer_recherche()

    def selection_changee(self):
        rows = self.tableau.selectionModel().selectedRows()
        if rows:
            row_idx = rows[0].row()
            rapport_id = int(self.tableau.item(row_idx, 0).text())

            from src.database import get_connection
            conn = get_connection()
            self.rapport_selectionne = conn.execute(
                'SELECT * FROM rapport WHERE id = ?', (rapport_id,)
            ).fetchone()
            conn.close()

            self.activer_boutons_action(True)
        else:
            self.rapport_selectionne = None
            self.activer_boutons_action(False)

    def activer_boutons_action(self, actif):
        self.btn_previsualiser.setEnabled(actif)
        self.btn_telecharger.setEnabled(actif)
        self.btn_ouvrir.setEnabled(actif)

    def previsualiser_pdf(self):
        """Ouvre la fenêtre de prévisualisation intégrée."""
        import os

        if not self.rapport_selectionne:
            return

        chemin = self.rapport_selectionne['chemin_pdf']
        if not os.path.exists(chemin):
            QMessageBox.warning(self, "Fichier introuvable",
                                "Fichier indisponible, contactez l'administrateur.")
            return

        from gui.preview_window import PreviewWindow
        self.preview = PreviewWindow(chemin, self.rapport_selectionne['titre'])
        self.preview.exec_()

    def telecharger_pdf(self):
        import os
        import shutil
        from PyQt5.QtWidgets import QFileDialog

        if not self.rapport_selectionne:
            return

        chemin_source = self.rapport_selectionne['chemin_pdf']
        if not os.path.exists(chemin_source):
            QMessageBox.warning(self, "Fichier introuvable",
                                "Fichier indisponible, contactez l'administrateur.")
            return

        nom_defaut = os.path.basename(chemin_source)
        chemin_dest, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le PDF", nom_defaut, "Fichiers PDF (*.pdf)")

        if chemin_dest:
            try:
                shutil.copy2(chemin_source, chemin_dest)
                QMessageBox.information(self, "Téléchargement réussi",
                                        f"✅ Fichier enregistré :\n{chemin_dest}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Échec du téléchargement :\n{e}")

    def ouvrir_pdf(self):
        import os

        if not self.rapport_selectionne:
            return

        chemin = self.rapport_selectionne['chemin_pdf']
        if not os.path.exists(chemin):
            QMessageBox.warning(self, "Fichier introuvable",
                                "Fichier indisponible, contactez l'administrateur.")
            return

        try:
            os.startfile(chemin)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier :\n{e}")