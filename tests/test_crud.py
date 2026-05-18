"""
Tests du module crud.py - Opérations sur la base de données.
"""
import pytest
from src.crud import (ajouter_utilisateur, get_utilisateur_by_email,
                      lister_utilisateurs, supprimer_utilisateur,
                      ajouter_rapport, rechercher_rapports,
                      get_statistiques, get_encadrants)


class TestUtilisateurs:
    """Tests des opérations sur les utilisateurs."""

    def test_ajout_utilisateur_simple(self, db_temporaire):
        """Un utilisateur ajouté doit être récupérable par email."""
        ajouter_utilisateur("Test User", "test@emsi.ma", "pass123", "etudiant",
                            numero_apogee="AP001", filiere="GL", annee_inscription=2025)
        user = get_utilisateur_by_email("test@emsi.ma")
        assert user is not None
        assert user['nom'] == "Test User"
        assert user['role'] == "etudiant"

    def test_email_unique(self, db_temporaire):
        """Impossible d'ajouter 2 utilisateurs avec le même email."""
        ajouter_utilisateur("User 1", "doublon@emsi.ma", "pass", "etudiant")
        ajouter_utilisateur("User 2", "doublon@emsi.ma", "pass", "encadrant")
        users = lister_utilisateurs()
        # Le 2ème doit être rejeté → toujours 1 seul utilisateur avec cet email
        emails = [u['email'] for u in users]
        assert emails.count("doublon@emsi.ma") == 1

    def test_mot_de_passe_hashe_en_base(self, db_temporaire):
        """Le mot de passe ne doit JAMAIS être stocké en clair."""
        ajouter_utilisateur("Test", "secure@emsi.ma", "monSecret", "administrateur")
        user = get_utilisateur_by_email("secure@emsi.ma")
        assert user['mot_de_passe'] != "monSecret"
        assert user['mot_de_passe'].startswith("$2b$")

    def test_get_encadrants_seulement(self, db_temporaire):
        """get_encadrants() ne retourne que les utilisateurs avec rôle 'encadrant'."""
        ajouter_utilisateur("Etu", "etu@emsi.ma", "p", "etudiant")
        ajouter_utilisateur("Enc1", "enc1@emsi.ma", "p", "encadrant", departement="GL")
        ajouter_utilisateur("Enc2", "enc2@emsi.ma", "p", "encadrant", departement="GI")
        ajouter_utilisateur("Adm", "adm@emsi.ma", "p", "administrateur")

        encadrants = get_encadrants()
        assert len(encadrants) == 2

    def test_suppression_utilisateur(self, db_temporaire):
        """Un utilisateur supprimé n'est plus dans la liste."""
        ajouter_utilisateur("À supprimer", "delete@emsi.ma", "p", "etudiant")
        user = get_utilisateur_by_email("delete@emsi.ma")
        supprimer_utilisateur(user['id'], admin_id=999)  # admin différent

        assert get_utilisateur_by_email("delete@emsi.ma") is None

    def test_admin_ne_peut_pas_se_supprimer(self, db_temporaire):
        """Un admin ne peut pas supprimer son propre compte."""
        ajouter_utilisateur("Admin", "admin@emsi.ma", "p", "administrateur")
        user = get_utilisateur_by_email("admin@emsi.ma")
        supprimer_utilisateur(user['id'], admin_id=user['id'])  # même ID

        # L'admin doit toujours exister
        assert get_utilisateur_by_email("admin@emsi.ma") is not None


class TestRapports:
    """Tests des opérations sur les rapports."""

    def test_ajout_rapport(self, db_temporaire):
        """Un rapport ajouté doit être récupérable."""
        # Créer d'abord un encadrant
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc = get_utilisateur_by_email("enc@emsi.ma")

        rapport_id = ajouter_rapport(
            "Mon Rapport", "Auteur Test", enc['id'], 2025,
            None, "test, ia", "/chemin/test.pdf", "texte du rapport"
        )

        assert rapport_id is not None
        rapports = rechercher_rapports()
        assert len(rapports) == 1
        assert rapports[0]['titre'] == "Mon Rapport"

    def test_recherche_par_motcle(self, db_temporaire):
        """La recherche par mot-clé doit filtrer correctement."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("Système RH", "A", enc_id, 2025, None, "rh", "/p1.pdf", "")
        ajouter_rapport("Système GL", "B", enc_id, 2025, None, "gl", "/p2.pdf", "")
        ajouter_rapport("Application Web", "C", enc_id, 2025, None, "web", "/p3.pdf", "")

        # Recherche "Système" → doit trouver 2 rapports
        results = rechercher_rapports(mot_cle="Système")
        assert len(results) == 2

    def test_recherche_par_promotion(self, db_temporaire):
        """La recherche par promotion doit filtrer correctement."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("R1", "A", enc_id, 2024, None, "", "/p1.pdf", "")
        ajouter_rapport("R2", "B", enc_id, 2025, None, "", "/p2.pdf", "")
        ajouter_rapport("R3", "C", enc_id, 2025, None, "", "/p3.pdf", "")

        results = rechercher_rapports(promotion=2025)
        assert len(results) == 2

    def test_recherche_combinee_et_logique(self, db_temporaire):
        """Plusieurs critères = ET logique."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("Web App", "A", enc_id, 2024, None, "", "/p1.pdf", "")
        ajouter_rapport("Web App", "B", enc_id, 2025, None, "", "/p2.pdf", "")

        # "Web" + 2025 → 1 seul résultat
        results = rechercher_rapports(mot_cle="Web", promotion=2025)
        assert len(results) == 1

    def test_statistiques_initiales(self, db_temporaire):
        """Une base vide doit retourner 0 partout."""
        stats = get_statistiques()
        assert stats['total'] == 0
        assert stats['soumis'] == 0
        assert stats['rejetes'] == 0

    def test_statistiques_apres_ajout(self, db_temporaire):
        """Les stats doivent refléter les rapports ajoutés."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("R1", "A", enc_id, 2025, None, "", "/p1.pdf", "")
        ajouter_rapport("R2", "B", enc_id, 2025, None, "", "/p2.pdf", "")

        stats = get_statistiques()
        assert stats['total'] == 2
        assert stats['soumis'] == 2  # statut par défaut