# 📚 Archive Digitale PFA

Application desktop de gestion des rapports de Projets de Fin d'Année (PFA) développée à l'EMSI.

## 🎯 Description

Système d'archivage numérique sécurisé permettant le dépôt, l'évaluation et la consultation des rapports PFA, avec **détection automatique de plagiat** par analyse de similarité (TF-IDF).

## ✨ Fonctionnalités

- 🔐 **Authentification sécurisée** avec hachage bcrypt
- 👥 **Gestion multi-rôles** : Étudiant, Encadrant, Administrateur (RBAC)
- 📤 **Dépôt de rapports** avec affectation d'encadrant
- 🔍 **Recherche multicritères** (mot-clé, promotion, filière)
- 📊 **Analyse de similarité TF-IDF** pour détecter les contenus similaires
- ✅ **Workflow d'évaluation** complet (acceptation/rejet)
- 👁️ **Prévisualisation PDF** intégrée avec navigation et zoom
- 📈 **Tableau de bord** statistique avec graphiques

## 🛠️ Technologies

- **Python 3.13** — langage principal
- **PyQt5** — interface graphique
- **SQLite3** — base de données
- **bcrypt** — sécurité des mots de passe
- **PyMuPDF** — manipulation des PDFs
- **scikit-learn** — analyse de similarité
- **Matplotlib** — graphiques statistiques

## 🚀 Installation

```bash
# Cloner le projet
git clone https://github.com/ajar132/archive-pfa-emsi.git
cd archive-pfa-emsi

# Installer les dépendances
pip install PyQt5 PyMuPDF scikit-learn matplotlib bcrypt

# Initialiser la base de données
python main.py

# Lancer l'application
python -m gui.login_window
```

## 📖 Comptes de test

| Rôle | Email | Mot de passe |
|---|---|---|
| Administrateur | admin@ecole.ma | admin123 |
| Encadrant | benali@ecole.ma | prof123 |
| Étudiant | ahmed@ecole.ma | pass123 |

## 📁 Structure du projet