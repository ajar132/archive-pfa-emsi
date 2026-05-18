"""
Tests du module security.py - Hachage bcrypt.
"""
import pytest
from src.security import hasher_mot_de_passe, verifier_mot_de_passe


class TestHachage:
    """Tests de la fonction de hachage."""

    def test_hash_different_du_mot_de_passe(self):
        """Le hash ne doit JAMAIS être égal au mot de passe en clair."""
        password = "monMotDePasse123"
        hash_result = hasher_mot_de_passe(password)
        assert hash_result != password

    def test_hash_commence_par_2b(self):
        """bcrypt produit toujours un hash commençant par $2b$."""
        hash_result = hasher_mot_de_passe("test")
        assert hash_result.startswith("$2b$")

    def test_hashs_differents_pour_meme_mot_de_passe(self):
        """Le salt aléatoire fait que 2 hashs du même mot de passe sont différents."""
        password = "memepassword"
        hash1 = hasher_mot_de_passe(password)
        hash2 = hasher_mot_de_passe(password)
        assert hash1 != hash2

    def test_hash_avec_caracteres_speciaux(self):
        """Le hachage doit fonctionner avec des accents et caractères spéciaux."""
        password = "Mot$de_Passe@2025é"
        hash_result = hasher_mot_de_passe(password)
        assert verifier_mot_de_passe(password, hash_result) is True


class TestVerification:
    """Tests de la fonction de vérification."""

    def test_verification_correcte(self):
        """Un mot de passe correct doit retourner True."""
        password = "correctPassword"
        hash_result = hasher_mot_de_passe(password)
        assert verifier_mot_de_passe(password, hash_result) is True

    def test_verification_incorrecte(self):
        """Un mauvais mot de passe doit retourner False."""
        hash_result = hasher_mot_de_passe("vraiPassword")
        assert verifier_mot_de_passe("fauxPassword", hash_result) is False

    def test_verification_chaine_vide(self):
        """Une chaîne vide ne doit jamais valider un hash valide."""
        hash_result = hasher_mot_de_passe("test")
        assert verifier_mot_de_passe("", hash_result) is False

    def test_verification_hash_invalide(self):
        """Un hash mal formé doit retourner False sans crasher."""
        assert verifier_mot_de_passe("password", "ce_n_est_pas_un_hash") is False