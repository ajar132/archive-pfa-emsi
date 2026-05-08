import sqlite3
from src.database import get_connection
from src.security import hasher_mot_de_passe
# ─────────────────────────────────────────
#  UTILISATEURS
# ─────────────────────────────────────────

def ajouter_utilisateur(nom, email, mot_de_passe, role,
                        numero_apogee=None, filiere=None, annee_inscription=None,
                        departement=None, specialite=None, grade=None):
    """Ajoute un utilisateur avec attributs spécifiques selon le rôle."""
    try:
        conn = get_connection()
        conn.execute('''
            INSERT INTO utilisateur
                (nom, email, mot_de_passe, role,
                 numero_apogee, filiere, annee_inscription,
                 departement, specialite, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nom, email, hasher_mot_de_passe(mot_de_passe), role,
              numero_apogee, filiere, annee_inscription,
              departement, specialite, grade))
        conn.commit()
        conn.close()
        print(f"✅ Utilisateur '{nom}' ({role}) ajouté.")
    except sqlite3.IntegrityError:
        print(f"❌ Erreur : l'email '{email}' est déjà utilisé.")

def get_encadrants():
    """Retourne la liste de tous les encadrants (pour la liste déroulante CU04)."""
    conn = get_connection()
    encadrants = conn.execute(
        "SELECT id, nom, departement FROM utilisateur WHERE role = 'encadrant'"
    ).fetchall()
    conn.close()
    return encadrants

def get_utilisateur_by_email(email):
    """Retourne un utilisateur par son email."""
    conn = get_connection()
    user = conn.execute(
        'SELECT * FROM utilisateur WHERE email = ?', (email,)
    ).fetchone()
    conn.close()
    return user

def supprimer_utilisateur(user_id, admin_id):
    """Supprime un utilisateur (interdit de se supprimer soi-même)."""
    if user_id == admin_id:
        print("❌ Erreur : vous ne pouvez pas supprimer votre propre compte.")
        return
    conn = get_connection()
    conn.execute('DELETE FROM utilisateur WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    print(f"✅ Utilisateur {user_id} supprimé.")

def lister_utilisateurs():
    """Retourne la liste de tous les utilisateurs (sans le mot de passe)."""
    conn = get_connection()
    users = conn.execute(
        'SELECT id, nom, email, role, numero_apogee, filiere, annee_inscription, '
        'departement, specialite, grade FROM utilisateur'
    ).fetchall()
    conn.close()
    return users

# ─────────────────────────────────────────
#  RAPPORTS
# ─────────────────────────────────────────

def ajouter_rapport(titre, auteurs, encadrant_id, promotion,
                    option_id, mots_cles, chemin_pdf, texte_extrait):
    """Ajoute un nouveau rapport à l'état Soumis."""
    try:
        conn = get_connection()
        cursor = conn.execute('''
            INSERT INTO rapport
                (titre, auteurs, encadrant_id, promotion,
                 option_id, mots_cles, chemin_pdf, texte_extrait, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Soumis')
        ''', (titre, auteurs, encadrant_id, promotion,
              option_id, mots_cles, chemin_pdf, texte_extrait))
        rapport_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"✅ Rapport '{titre}' ajouté avec l'ID {rapport_id}.")
        return rapport_id
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de l'ajout : {e}")
        return None

def rechercher_rapports(mot_cle=None, promotion=None, option_id=None, statut_filtre=None):
    """Recherche multicritères (ET logique)."""
    conn = get_connection()
    query = 'SELECT * FROM rapport WHERE 1=1'
    params = []

    if mot_cle:
        query += ' AND (titre LIKE ? OR mots_cles LIKE ? OR auteurs LIKE ?)'
        params.extend([f'%{mot_cle}%', f'%{mot_cle}%', f'%{mot_cle}%'])
    if promotion:
        query += ' AND promotion = ?'
        params.append(promotion)
    if option_id:
        query += ' AND option_id = ?'
        params.append(option_id)
    if statut_filtre:
        query += ' AND statut = ?'
        params.append(statut_filtre)

    rapports = conn.execute(query, params).fetchall()
    conn.close()
    return rapports

def changer_statut(rapport_id, nouveau_statut, note=None, commentaire=None):
    """Met à jour le statut d'un rapport."""
    statuts_valides = ['Soumis', 'En cours', 'Evalué', 'Archivé', 'Rejeté']
    if nouveau_statut not in statuts_valides:
        print(f"❌ Statut invalide : {nouveau_statut}")
        return
    conn = get_connection()
    conn.execute('''
        UPDATE rapport
        SET statut = ?, note = ?, commentaire = ?
        WHERE id = ?
    ''', (nouveau_statut, note, commentaire, rapport_id))
    conn.commit()
    conn.close()
    print(f"✅ Rapport {rapport_id} → statut '{nouveau_statut}'.")

def get_statistiques():
    """Retourne les statistiques pour le tableau de bord."""
    conn = get_connection()
    stats = {}
    stats['total']     = conn.execute('SELECT COUNT(*) FROM rapport').fetchone()[0]
    stats['soumis']    = conn.execute("SELECT COUNT(*) FROM rapport WHERE statut = 'Soumis'").fetchone()[0]
    stats['en_cours']  = conn.execute("SELECT COUNT(*) FROM rapport WHERE statut = 'En cours'").fetchone()[0]
    stats['evalues']   = conn.execute("SELECT COUNT(*) FROM rapport WHERE statut = 'Evalué'").fetchone()[0]
    stats['archives']  = conn.execute("SELECT COUNT(*) FROM rapport WHERE statut = 'Archivé'").fetchone()[0]
    stats['rejetes']   = conn.execute("SELECT COUNT(*) FROM rapport WHERE statut = 'Rejeté'").fetchone()[0]
    conn.close()
    return stats

def supprimer_rapport(rapport_id):
    """Supprime un rapport de la base."""
    conn = get_connection()
    conn.execute('DELETE FROM rapport WHERE id = ?', (rapport_id,))
    conn.commit()
    conn.close()
    print(f"✅ Rapport {rapport_id} supprimé.")

def get_rapports_par_encadrant(encadrant_id, statut_filtre=None):
    """Retourne les rapports assignés à un encadrant, avec filtre optionnel par statut."""
    conn = get_connection()
    if statut_filtre:
        rapports = conn.execute('''
            SELECT * FROM rapport
            WHERE encadrant_id = ? AND statut = ?
            ORDER BY date_depot DESC
        ''', (encadrant_id, statut_filtre)).fetchall()
    else:
        rapports = conn.execute('''
            SELECT * FROM rapport
            WHERE encadrant_id = ?
            ORDER BY date_depot DESC
        ''', (encadrant_id,)).fetchall()
    conn.close()
    return rapports


def evaluer_rapport(rapport_id, encadrant_id, note, commentaire, decision):
    """
    Enregistre l'évaluation d'un rapport.
    Vérifie que le rapport appartient bien à l'encadrant avant toute modification.
    decision = 'accepter' → statut 'Archivé'
    decision = 'rejeter'  → statut 'Rejeté'
    """
    if decision == 'accepter':
        nouveau_statut = 'Archivé'
    elif decision == 'rejeter':
        nouveau_statut = 'Rejeté'
    else:
        print(f"❌ Décision invalide : {decision}")
        return False

    conn = get_connection()
    rapport = conn.execute(
        'SELECT encadrant_id FROM rapport WHERE id = ?', (rapport_id,)
    ).fetchone()

    if rapport is None or rapport['encadrant_id'] != encadrant_id:
        conn.close()
        print(f"❌ Accès refusé : rapport {rapport_id} n'appartient pas à l'encadrant {encadrant_id}.")
        return False

    conn.execute('''
        UPDATE rapport
        SET statut = ?, note = ?, commentaire = ?
        WHERE id = ?
    ''', (nouveau_statut, note, commentaire, rapport_id))
    conn.commit()
    conn.close()
    print(f"✅ Rapport {rapport_id} évalué : {nouveau_statut} (note: {note})")
    return True

def modifier_utilisateur(user_id, nom, email, role,
                        numero_apogee=None, filiere=None, annee_inscription=None,
                        departement=None, specialite=None, grade=None):
    """Modifie un utilisateur existant."""
    try:
        conn = get_connection()
        conn.execute('''
            UPDATE utilisateur
            SET nom = ?, email = ?, role = ?,
                numero_apogee = ?, filiere = ?, annee_inscription = ?,
                departement = ?, specialite = ?, grade = ?
            WHERE id = ?
        ''', (nom, email, role,
              numero_apogee, filiere, annee_inscription,
              departement, specialite, grade, user_id))
        conn.commit()
        conn.close()
        print(f"✅ Utilisateur {user_id} modifié.")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ Erreur : email déjà utilisé.")
        return False


def get_utilisateur_by_id(user_id):
    """Retourne un utilisateur par son ID."""
    conn = get_connection()
    user = conn.execute(
        'SELECT * FROM utilisateur WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return user