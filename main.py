from src.database import create_tables
from src.crud import (ajouter_utilisateur, get_statistiques,
                      changer_statut, lister_utilisateurs, get_encadrants)
from src.pdf_handler import deposer_rapport

# 1. Initialiser la base
create_tables()

# 2. Ajouter un administrateur
ajouter_utilisateur("Admin Test", "admin@ecole.ma",
                    "admin123", "administrateur")

# 3. Ajouter un encadrant avec ses attributs
ajouter_utilisateur("Prof Benali", "benali@ecole.ma",
                    "prof123", "encadrant",
                    departement="Informatique",
                    specialite="Intelligence Artificielle",
                    grade="PES")

# 4. Ajouter un étudiant avec ses attributs
ajouter_utilisateur("Ahmed Benali", "ahmed@ecole.ma",
                    "pass123", "etudiant",
                    numero_apogee="AP2024001",
                    filiere="Génie Informatique",
                    annee_inscription=2024)

# 5. Vérifier les utilisateurs
print("\n👥 Liste des utilisateurs :")
users = lister_utilisateurs()
for u in users:
    print(f"  👤 {u['nom']} ({u['role']})")

# 6. Tester la liste déroulante encadrants (pour CU04)
print("\n📋 Encadrants disponibles :")
encadrants = get_encadrants()
for e in encadrants:
    print(f"  🧑‍🏫 ID:{e['id']} | {e['nom']} | {e['departement']}")

# 7. Statistiques
stats = get_statistiques()
print(f"\n📊 Statistiques : {stats}")

from src.crud import changer_statut

# Dans main.py, ajoutez à la fin :
from src.crud import changer_statut

changer_statut(1, 'En cours')
changer_statut(2, 'Evalué', note=16, commentaire="Excellent travail")