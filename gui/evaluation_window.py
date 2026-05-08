from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                              QHBoxLayout, QTableWidget, QTableWidgetItem,
                              QHeaderView, QGroupBox, QMessageBox, QComboBox,
                              QAbstractItemView, QDialog, QFormLayout,
                              QDoubleSpinBox, QTextEdit, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.crud import get_rapports_par_encadrant, evaluer_rapport, changer_statut


class EvaluationWindow(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.rapport_selectionne = None
        self.init_ui()
        self.charger_rapports()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Titre + refresh
        titre_layout = QHBoxLayout()

        titre = QLabel("✅ Mes rapports à évaluer")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        titre_layout.addWidget(titre)
        titre_layout.addStretch()

        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedHeight(35)
        btn_refresh.setFixedWidth(140)
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #156082; color: white;
                font-weight: bold; border: none; border-radius: 5px;
            }
            QPushButton:hover { background-color: #1d7ba6; }
        """)
        btn_refresh.clicked.connect(self.charger_rapports)
        titre_layout.addWidget(btn_refresh)

        layout.addLayout(titre_layout)

        # Filtre par statut
        filtre_layout = QHBoxLayout()
        filtre_layout.addWidget(QLabel("Filtrer par statut :"))

        self.combo_statut = QComboBox()
        self.combo_statut.addItem("Tous", None)
        self.combo_statut.addItem("Soumis (à évaluer)", "Soumis")
        self.combo_statut.addItem("En cours", "En cours")
        self.combo_statut.addItem("Évalués", "Evalué")
        self.combo_statut.addItem("Rejetés", "Rejeté")
        self.combo_statut.setFixedHeight(32)
        self.combo_statut.setFixedWidth(200)
        self.combo_statut.currentIndexChanged.connect(self.charger_rapports)
        filtre_layout.addWidget(self.combo_statut)
        filtre_layout.addStretch()

        layout.addLayout(filtre_layout)

        # Label compteur
        self.label_compteur = QLabel("")
        self.label_compteur.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.label_compteur)

        # Tableau
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(7)
        self.tableau.setHorizontalHeaderLabels(
            ["ID", "Titre", "Auteurs", "Promotion", "Statut", "Note", "Date dépôt"])
        self.tableau.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableau.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tableau.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableau.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.setStyleSheet("""
            QTableWidget { background-color: white; }
            QTableWidget::item:selected { background-color: #156082; color: white; }
        """)
        self.tableau.itemSelectionChanged.connect(self.selection_changee)
        self.tableau.doubleClicked.connect(self.ouvrir_evaluation)
        layout.addWidget(self.tableau)

        # Boutons d'action
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_previsualiser = QPushButton("👁️ Prévisualiser PDF")
        self.btn_previsualiser.setFixedHeight(38)
        self.btn_previsualiser.setEnabled(False)
        self.btn_previsualiser.clicked.connect(self.previsualiser_pdf)

        self.btn_evaluer = QPushButton("✏️ Évaluer ce rapport")
        self.btn_evaluer.setFixedHeight(38)
        self.btn_evaluer.setEnabled(False)
        self.btn_evaluer.setCursor(Qt.PointingHandCursor)
        self.btn_evaluer.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-weight: bold; border: none; border-radius: 5px;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.btn_evaluer.clicked.connect(self.ouvrir_evaluation)

        action_layout.addWidget(self.btn_previsualiser)
        action_layout.addWidget(self.btn_evaluer)
        layout.addLayout(action_layout)

        self.setLayout(layout)

    def charger_rapports(self):
        """Charge les rapports assignés à l'encadrant connecté."""
        statut = self.combo_statut.currentData()
        rapports = get_rapports_par_encadrant(self.utilisateur['id'], statut)

        nb = len(rapports)
        if nb == 0:
            self.label_compteur.setText("Aucun rapport assigné pour ce filtre.")
            self.label_compteur.setStyleSheet("color: gray;")
        else:
            self.label_compteur.setText(f"📋 {nb} rapport(s) assigné(s) :")
            self.label_compteur.setStyleSheet("color: #156082;")

        self.tableau.setRowCount(nb)
        couleurs_statut = {
            'Soumis':   QColor("#f39c12"),
            'En cours': QColor("#3498db"),
            'Evalué':   QColor("#27ae60"),
            'Archivé':  QColor("#95a5a6"),
            'Rejeté':   QColor("#e74c3c"),
        }

        for i, r in enumerate(rapports):
            self.tableau.setItem(i, 0, QTableWidgetItem(str(r['id'])))
            self.tableau.setItem(i, 1, QTableWidgetItem(r['titre']))
            self.tableau.setItem(i, 2, QTableWidgetItem(r['auteurs']))
            self.tableau.setItem(i, 3, QTableWidgetItem(str(r['promotion'])))

            statut_item = QTableWidgetItem(r['statut'])
            if r['statut'] in couleurs_statut:
                statut_item.setBackground(couleurs_statut[r['statut']])
                statut_item.setForeground(QColor("white"))
            self.tableau.setItem(i, 4, statut_item)

            note_text = f"{r['note']}/20" if r['note'] is not None else "-"
            self.tableau.setItem(i, 5, QTableWidgetItem(note_text))
            self.tableau.setItem(i, 6, QTableWidgetItem(str(r['date_depot'])))

        self.rapport_selectionne = None
        self.btn_previsualiser.setEnabled(False)
        self.btn_evaluer.setEnabled(False)

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

            self.btn_previsualiser.setEnabled(True)

            # Le bouton Évaluer n'est actif que si le statut le permet
            statut = self.rapport_selectionne['statut']
            self.btn_evaluer.setEnabled(statut in ('Soumis', 'En cours'))
        else:
            self.rapport_selectionne = None
            self.btn_previsualiser.setEnabled(False)
            self.btn_evaluer.setEnabled(False)

    def previsualiser_pdf(self):
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

    def ouvrir_evaluation(self):
        """Ouvre le dialogue d'évaluation."""
        if not self.rapport_selectionne:
            return

        statut = self.rapport_selectionne['statut']
        if statut not in ('Soumis', 'En cours'):
            QMessageBox.information(self, "Évaluation impossible",
                                    f"Ce rapport est déjà à l'état '{statut}'.\n"
                                    "Vous ne pouvez plus le modifier.")
            return

        # Si c'est encore "Soumis", passer à "En cours" automatiquement
        if statut == 'Soumis':
            changer_statut(self.rapport_selectionne['id'], 'En cours')

        # Ouvrir le dialogue d'évaluation
        dialog = EvaluationDialog(self.rapport_selectionne, self.utilisateur['id'], self)
        if dialog.exec_() == QDialog.Accepted:
            self.charger_rapports()  # rafraîchir le tableau


# ─────────────────────────────────────────────────
#  DIALOGUE D'ÉVALUATION
# ─────────────────────────────────────────────────
class EvaluationDialog(QDialog):
    def __init__(self, rapport, encadrant_id, parent=None):
        super().__init__(parent)
        self.rapport = rapport
        self.encadrant_id = encadrant_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Évaluation - {self.rapport['titre']}")
        self.setFixedSize(500, 450)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Info du rapport
        info = QGroupBox("📄 Informations du rapport")
        info_layout = QFormLayout()
        info_layout.addRow("Titre :", QLabel(self.rapport['titre']))
        info_layout.addRow("Auteurs :", QLabel(self.rapport['auteurs']))
        info_layout.addRow("Promotion :", QLabel(str(self.rapport['promotion'])))
        info.setLayout(info_layout)
        layout.addWidget(info)

        # Note
        layout.addWidget(QLabel("Note (sur 20) * :"))
        self.spin_note = QDoubleSpinBox()
        self.spin_note.setRange(0, 20)
        self.spin_note.setSingleStep(0.5)
        self.spin_note.setValue(10)
        self.spin_note.setFixedHeight(35)
        self.spin_note.setStyleSheet("font-size: 14px; padding: 5px;")
        layout.addWidget(self.spin_note)

        # Commentaire
        layout.addWidget(QLabel("Commentaire :"))
        self.text_commentaire = QTextEdit()
        self.text_commentaire.setPlaceholderText(
            "Saisissez votre commentaire ici (obligatoire en cas de rejet)...")
        self.text_commentaire.setFixedHeight(100)
        layout.addWidget(self.text_commentaire)

        # Boutons d'action
        btn_layout = QHBoxLayout()

        btn_annuler = QPushButton("Annuler")
        btn_annuler.setFixedHeight(40)
        btn_annuler.clicked.connect(self.reject)

        btn_rejeter = QPushButton("❌ Rejeter")
        btn_rejeter.setFixedHeight(40)
        btn_rejeter.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                font-weight: bold; border: none; border-radius: 5px;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_rejeter.clicked.connect(self.rejeter)

        btn_accepter = QPushButton("✅ Accepter")
        btn_accepter.setFixedHeight(40)
        btn_accepter.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-weight: bold; border: none; border-radius: 5px;
                padding: 0 15px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_accepter.clicked.connect(self.accepter)

        btn_layout.addWidget(btn_annuler)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_rejeter)
        btn_layout.addWidget(btn_accepter)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def accepter(self):
        note = self.spin_note.value()
        commentaire = self.text_commentaire.toPlainText().strip()

        if evaluer_rapport(self.rapport['id'], self.encadrant_id, note, commentaire, 'accepter'):
            QMessageBox.information(self, "Évaluation enregistrée",
                                    f"✅ Rapport accepté avec la note {note}/20.\n"
                                    f"Le rapport est maintenant archivé et consultable par tous.")
            self.accept()
        else:
            QMessageBox.critical(self, "Accès refusé",
                                 "Vous n'êtes pas autorisé à évaluer ce rapport.")

    def rejeter(self):
        commentaire = self.text_commentaire.toPlainText().strip()
        if not commentaire:
            QMessageBox.warning(self, "Commentaire obligatoire",
                                "Un commentaire de motif est requis en cas de rejet.")
            return

        note = self.spin_note.value()
        if evaluer_rapport(self.rapport['id'], self.encadrant_id, note, commentaire, 'rejeter'):
            QMessageBox.information(self, "Rapport rejeté",
                                    "❌ Le rapport a été marqué comme rejeté.")
            self.accept()
        else:
            QMessageBox.critical(self, "Accès refusé",
                                 "Vous n'êtes pas autorisé à évaluer ce rapport.")
