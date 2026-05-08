import bcrypt


def hasher_mot_de_passe(mot_de_passe):
    """
    Transforme un mot de passe en hash sécurisé.
    Le hash est différent à chaque appel grâce au "salt" automatique.
    """
    # Convertir le mot de passe en bytes
    password_bytes = mot_de_passe.encode('utf-8')
    # Générer le hash avec un salt aléatoire
    hash_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Retourner le hash comme string pour stockage en base
    return hash_bytes.decode('utf-8')


def verifier_mot_de_passe(mot_de_passe_saisi, hash_stocke):
    """
    Vérifie si un mot de passe correspond à un hash stocké.
    Retourne True si correspondance, False sinon.
    """
    try:
        password_bytes = mot_de_passe_saisi.encode('utf-8')
        hash_bytes = hash_stocke.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False