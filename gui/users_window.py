from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                              QVBoxLayout, QHBoxLayout, QFormLayout,
                              QComboBox, QSpinBox, QTableWidget, QTableWidgetItem,
                              QHeaderView, QGroupBox, QMessageBox, QDialog,
                              QAbstractItemView, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from src.crud import (lister_utilisateurs, ajouter_utilisateur,
                      modifier_utilisateur, supprimer_utilisateur,
                      get_utilisateur_by_id)


class UsersWindow(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur  # admin connecté
        self.user_selectionne = None
        self.init_ui()
        self.charger_utilisateurs()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Titre + bouton ajouter
        titre_layout = QHBoxLayout()

        titre = QLabel("👥 Gestion des utilisateurs")
        titre.setFont(QFont("Arial", 18, QFont.Bold))
        titre_layout.addWidget(titre)
        titre_layout.addStretch()

        btn_ajouter = QPushButton("➕ Ajouter un utilisateur")
        btn_ajouter.setFixedHeight(38)
        btn_ajouter.setFixedWidth(200)
        btn_ajouter.setCursor(Qt.PointingHandCursor)
        btn_ajouter.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                font-weight: bold; border: none; border-radius: 5px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_ajouter.clicked.connect(self.ouvrir_dialogue_ajout)
        titre_layout.addWidget(btn_ajouter)

        layout.addLayout(titre_layout)

        # Compteur
        self.label_compteur = QLabel("")
        self.label_compteur.setStyleSheet("color: #156082; font-weight: bold;")
        layout.addWidget(self.label_compteur)

        # Tableau
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(6)
        self.tableau.setHorizontalHeaderLabels(
            ["ID", "Nom", "Email", "Rôle", "Détails", "Actions"])
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
        layout.addWidget(self.tableau)

        self.setLayout(layout)

    def charger_utilisateurs(self):
        users = lister_utilisateurs()
        nb = len(users)
        self.label_compteur.setText(f"📋 {nb} utilisateur(s) enregistré(s) :")

        self.tableau.setRowCount(nb)
        couleurs_role = {
            'administrateur': QColor("#9b59b6"),
            'encadrant':      QColor("#3498db"),
            'etudiant':       QColor("#1abc9c"),
        }

        for i, u in enumerate(users):
            self.tableau.setItem(i, 0, QTableWidgetItem(str(u['id'])))
            self.tableau.setItem(i, 1, QTableWidgetItem(u['nom']))
            self.tableau.setItem(i, 2, QTableWidgetItem(u['email']))

            # Rôle avec couleur
            role_item = QTableWidgetItem(u['role'].capitalize())
            if u['role'] in couleurs_role:
                role_item.setBackground(couleurs_role[u['role']])
                role_item.setForeground(QColor("white"))
            self.tableau.setItem(i, 3, role_item)

            # Détails selon rôle
            if u['role'] == 'etudiant':
                details = f"Apogée: {u['numero_apogee'] or '-'} | {u['filiere'] or '-'}"
            elif u['role'] == 'encadrant':
                details = f"{u['departement'] or '-'} | {u['grade'] or '-'}"
            else:
                details = "-"
            self.tableau.setItem(i, 4, QTableWidgetItem(details))

            # Boutons d'action dans la colonne
            cell_widget = QWidget()
            cell_layout = QHBoxLayout()
            cell_layout.setContentsMargins(5, 2, 5, 2)
            cell_layout.setSpacing(5)

            btn_modif = QPushButton("✏️")
            btn_modif.setFixedSize(35, 28)
            btn_modif.setToolTip("Modifier")
            btn_modif.setCursor(Qt.PointingHandCursor)
            btn_modif.clicked.connect(lambda _, uid=u['id']: self.ouvrir_dialogue_modif(uid))

            btn_suppr = QPushButton("🗑️")
            btn_suppr.setFixedSize(35, 28)
            btn_suppr.setToolTip("Supprimer")
            btn_suppr.setCursor(Qt.PointingHandCursor)
            btn_suppr.clicked.connect(lambda _, uid=u['id'], nom=u['nom']: self.supprimer(uid, nom))

            cell_layout.addWidget(btn_modif)
            cell_layout.addWidget(btn_suppr)
            cell_widget.setLayout(cell_layout)
            self.tableau.setCellWidget(i, 5, cell_widget)

    def ouvrir_dialogue_ajout(self):
        dialog = UserDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.charger_utilisateurs()

    def ouvrir_dialogue_modif(self, user_id):
        # Empêcher l'admin de modifier son propre rôle
        if user_id == self.utilisateur['id']:
            QMessageBox.warning(self, "Action restreinte",
                                "Vous ne pouvez pas modifier votre propre rôle.\n"
                                "Demandez à un autre administrateur.")
            return
        user = get_utilisateur_by_id(user_id)
        dialog = UserDialog(user=user, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.charger_utilisateurs()

    def supprimer(self, user_id, nom):
        # Empêcher suppression de soi-même
        if user_id == self.utilisateur['id']:
            QMessageBox.warning(self, "Action interdite",
                                "Vous ne pouvez pas supprimer votre propre compte.")
            return

        # Confirmation
        reponse = QMessageBox.question(self, "Confirmation",
                                       f"Voulez-vous vraiment supprimer '{nom}' ?\n\n"
                                       "Cette action est irréversible.",
                                       QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            supprimer_utilisateur(user_id, self.utilisateur['id'])
            self.charger_utilisateurs()


# ─────────────────────────────────────────────────
#  DIALOGUE AJOUT / MODIFICATION
# ─────────────────────────────────────────────────
class UserDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user  # None = ajout, sinon = modification
        self.mode_modif = user is not None
        self.init_ui()
        if self.mode_modif:
            self.remplir_formulaire()

    def init_ui(self):
        titre = "Modifier l'utilisateur" if self.mode_modif else "Ajouter un utilisateur"
        self.setWindowTitle(titre)
        self.setFixedSize(500, 580)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Titre
        label_titre = QLabel(f"{'✏️' if self.mode_modif else '➕'} {titre}")
        label_titre.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(label_titre)

        # ─── Champs communs ───
        groupe_commun = QGroupBox("Informations générales")
        form_commun = QFormLayout()
        form_commun.setSpacing(10)

        self.input_nom = QLineEdit()
        self.input_nom.setFixedHeight(32)
        self.input_email = QLineEdit()
        self.input_email.setFixedHeight(32)
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedHeight(32)
        if self.mode_modif:
            self.input_password.setPlaceholderText("(laisser vide pour ne pas changer)")

        self.combo_role = QComboBox()
        self.combo_role.addItems(["etudiant", "encadrant", "administrateur"])
        self.combo_role.setFixedHeight(32)
        self.combo_role.currentTextChanged.connect(self.changer_role_affichage)

        form_commun.addRow("Nom complet *:", self.input_nom)
        form_commun.addRow("Email *:", self.input_email)
        form_commun.addRow("Mot de passe *:", self.input_password)
        form_commun.addRow("Rôle *:", self.combo_role)
        groupe_commun.setLayout(form_commun)
        layout.addWidget(groupe_commun)

        # ─── Champs spécifiques (étudiant) ───
        self.groupe_etudiant = QGroupBox("📚 Informations étudiant")
        form_etu = QFormLayout()

        self.input_apogee = QLineEdit()
        self.input_apogee.setPlaceholderText("Ex: AP2024001")
        self.input_apogee.setFixedHeight(32)

        self.input_filiere = QLineEdit()
        self.input_filiere.setPlaceholderText("Ex: Génie Informatique")
        self.input_filiere.setFixedHeight(32)

        self.spin_annee = QSpinBox()
        self.spin_annee.setRange(2000, 2050)
        self.spin_annee.setValue(2025)
        self.spin_annee.setFixedHeight(32)

        form_etu.addRow("N° Apogée :", self.input_apogee)
        form_etu.addRow("Filière :", self.input_filiere)
        form_etu.addRow("Année d'inscription :", self.spin_annee)
        self.groupe_etudiant.setLayout(form_etu)
        layout.addWidget(self.groupe_etudiant)

        # ─── Champs spécifiques (encadrant) ───
        self.groupe_encadrant = QGroupBox("🧑‍🏫 Informations encadrant")
        form_enc = QFormLayout()

        self.input_departement = QLineEdit()
        self.input_departement.setPlaceholderText("Ex: Informatique")
        self.input_departement.setFixedHeight(32)

        self.input_specialite = QLineEdit()
        self.input_specialite.setPlaceholderText("Ex: Intelligence Artificielle")
        self.input_specialite.setFixedHeight(32)

        self.combo_grade = QComboBox()
        self.combo_grade.addItems(["PA", "PH", "PES", "Vacataire"])
        self.combo_grade.setFixedHeight(32)

        form_enc.addRow("Département :", self.input_departement)
        form_enc.addRow("Spécialité :", self.input_specialite)
        form_enc.addRow("Grade :", self.combo_grade)
        self.groupe_encadrant.setLayout(form_enc)
        layout.addWidget(self.groupe_encadrant)

        layout.addStretch()

        # ─── Boutons ───
        btn_layout = QHBoxLayout()
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setFixedHeight(38)
        btn_annuler.clicked.connect(self.reject)

        btn_valider = QPushButton("✅ Valider")
        btn_valider.setFixedHeight(38)
        btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #156082; color: white;
                font-weight: bold; border: none; border-radius: 5px;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #1d7ba6; }
        """)
        btn_valider.clicked.connect(self.valider)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_annuler)
        btn_layout.addWidget(btn_valider)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.changer_role_affichage()  # cacher/afficher selon le rôle initial

    def changer_role_affichage(self):
        """Affiche les champs spécifiques selon le rôle sélectionné."""
        role = self.combo_role.currentText()
        self.groupe_etudiant.setVisible(role == 'etudiant')
        self.groupe_encadrant.setVisible(role == 'encadrant')

    def remplir_formulaire(self):
        """En mode modification, pré-remplit les champs."""
        u = self.user
        self.input_nom.setText(u['nom'])
        self.input_email.setText(u['email'])
        self.combo_role.setCurrentText(u['role'])

        if u['role'] == 'etudiant':
            self.input_apogee.setText(u['numero_apogee'] or '')
            self.input_filiere.setText(u['filiere'] or '')
            if u['annee_inscription']:
                self.spin_annee.setValue(u['annee_inscription'])
        elif u['role'] == 'encadrant':
            self.input_departement.setText(u['departement'] or '')
            self.input_specialite.setText(u['specialite'] or '')
            if u['grade']:
                self.combo_grade.setCurrentText(u['grade'])

    def valider(self):
        nom = self.input_nom.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        role = self.combo_role.currentText()

        # Validation de base
        if not nom or not email:
            QMessageBox.warning(self, "Champs manquants",
                                "Le nom et l'email sont obligatoires.")
            return

        if not self.mode_modif and not password:
            QMessageBox.warning(self, "Mot de passe requis",
                                "Le mot de passe est obligatoire à la création.")
            return

        # Récupérer les attributs spécifiques
        apogee = filiere = annee = None
        departement = specialite = grade = None

        if role == 'etudiant':
            apogee = self.input_apogee.text().strip() or None
            filiere = self.input_filiere.text().strip() or None
            annee = self.spin_annee.value()
        elif role == 'encadrant':
            departement = self.input_departement.text().strip() or None
            specialite = self.input_specialite.text().strip() or None
            grade = self.combo_grade.currentText()

        # Mode ajout vs modification
        if self.mode_modif:
            ok = modifier_utilisateur(self.user['id'], nom, email, role,
                                      apogee, filiere, annee,
                                      departement, specialite, grade)
            # Si nouveau mot de passe fourni, le mettre à jour
            if password:
                from src.database import get_connection
                from src.security import hasher_mot_de_passe
                conn = get_connection()
                conn.execute('UPDATE utilisateur SET mot_de_passe = ? WHERE id = ?',
                             (hasher_mot_de_passe(password), self.user['id']))
                conn.commit()
                conn.close()

            if ok:
                QMessageBox.information(self, "Succès",
                                        "✅ Utilisateur modifié avec succès.")
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur",
                                    "Cet email est déjà utilisé.")
        else:
            try:
                ajouter_utilisateur(nom, email, password, role,
                                    apogee, filiere, annee,
                                    departement, specialite, grade)
                QMessageBox.information(self, "Succès",
                                        f"✅ Utilisateur '{nom}' ajouté avec succès.")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Erreur",
                                    f"Impossible d'ajouter l'utilisateur :\n{e}")