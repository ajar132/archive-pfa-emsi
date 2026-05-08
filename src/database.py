import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'archive.db')

def get_connection():
    """Retourne une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permet d'accéder aux colonnes par nom
    return conn

def create_tables():
    """Crée toutes les tables si elles n'existent pas."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table des utilisateurs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS utilisateur (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        nom             TEXT NOT NULL,
        email           TEXT NOT NULL UNIQUE,
        mot_de_passe    TEXT NOT NULL,
        role            TEXT NOT NULL CHECK(role IN ('etudiant', 'encadrant', 'administrateur')),
        -- Attributs étudiant
        numero_apogee   TEXT,
        filiere         TEXT,
        annee_inscription INTEGER,
        -- Attributs encadrant
        departement     TEXT,
        specialite      TEXT,
        grade           TEXT
    )
''')

    # Table des options/filières
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS option_filiere (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            nom   TEXT NOT NULL UNIQUE
        )
    ''')

    # Table des rapports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rapport (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            titre           TEXT NOT NULL,
            auteurs         TEXT NOT NULL,
            encadrant_id    INTEGER,
            promotion       INTEGER NOT NULL,
            option_id       INTEGER,
            mots_cles       TEXT,
            chemin_pdf      TEXT NOT NULL,
            texte_extrait   TEXT,
            statut          TEXT NOT NULL DEFAULT 'Soumis'
                            CHECK(statut IN ('Soumis','En cours','Evalué','Archivé','Rejeté')),
            note            REAL,
            commentaire     TEXT,
            date_depot      TEXT DEFAULT (date('now')),
            FOREIGN KEY (encadrant_id) REFERENCES utilisateur(id),
            FOREIGN KEY (option_id)    REFERENCES option_filiere(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Tables créées avec succès.")

if __name__ == '__main__':
    create_tables()