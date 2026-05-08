from src.database import create_tables
from src.crud import (ajouter_utilisateur, get_statistiques,
                      lister_utilisateurs, get_encadrants)

# 1. Initialiser la base
create_tables()

# 2. Créer l'administrateur principal
ajouter_utilisateur(
    nom="El Mahdi BAKIROU",
    email="bakirou.admin@emsi.ma",
    mot_de_passe="bakirou2026",
    role="administrateur"
)

# 3. Créer un encadrant
ajouter_utilisateur(
    nom="Yassine ZAIDANY",
    email="zaidany.encadrant@emsi.ma",
    mot_de_passe="zaidany2026",
    role="encadrant",
    departement="Génie Logiciel",
    specialite="Ingénierie Logicielle",
    grade="PA"
)

# 4. Créer un étudiant
ajouter_utilisateur(
    nom="El Mahdi BAKIROU",
    email="bakirou.etudiant@emsi.ma",
    mot_de_passe="bakirou123",
    role="etudiant",
    numero_apogee="EMSI2025001",
    filiere="Génie Logiciel",
    annee_inscription=2023
)

# 5. Vérifier la création
print("\n👥 Liste des utilisateurs créés :")
users = lister_utilisateurs()
for u in users:
    print(f"  👤 {u['nom']} | {u['email']} | {u['role']}")

# 6. Afficher les encadrants disponibles
print("\n📋 Encadrants disponibles pour assignation :")
for e in get_encadrants():
    print(f"  🧑‍🏫 ID:{e['id']} | {e['nom']} | {e['departement']}")

# 7. Statistiques de la base
stats = get_statistiques()
print(f"\n📊 Statistiques : {stats}")