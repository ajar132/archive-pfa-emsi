"""
Tests du module pdf_handler.py - Analyse de similarité TF-IDF.
"""
import pytest
from src.pdf_handler import analyser_similarite
from src.crud import ajouter_utilisateur, ajouter_rapport, get_utilisateur_by_email


class TestSimilarite:
    """Tests de l'algorithme de similarité TF-IDF."""

    def test_similarite_base_vide(self, db_temporaire):
        """Sans rapports en base, le résultat doit être vide."""
        resultats = analyser_similarite("Texte de test")
        assert resultats == []

    def test_texte_vide_ou_none(self, db_temporaire):
        """Un texte vide/None ne doit pas planter et retourner []."""
        assert analyser_similarite(None) == []
        assert analyser_similarite("") == []

    def test_similarite_textes_identiques(self, db_temporaire):
        """Deux textes identiques doivent avoir un score proche de 100%."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        texte = "intelligence artificielle machine learning python"
        ajouter_rapport("R1", "A", enc_id, 2025, None, "", "/p1.pdf", texte)

        resultats = analyser_similarite(texte)
        assert len(resultats) == 1
        assert resultats[0]['similarite'] >= 95  # quasi-identique

    def test_similarite_textes_differents(self, db_temporaire):
        """Deux textes sans aucun mot commun doivent avoir un score faible."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("R1", "A", enc_id, 2025, None, "", "/p1.pdf",
                       "cuisine recette pizza pâte tomate fromage")

        resultats = analyser_similarite(
            "génétique ADN chromosome biologie cellulaire")
        assert resultats[0]['similarite'] < 30  # très peu de mots en commun

    def test_resultats_tries_par_score(self, db_temporaire):
        """Les résultats doivent être triés par similarité décroissante."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("R1", "A", enc_id, 2025, None, "", "/p1.pdf",
                       "python programmation logiciel")
        ajouter_rapport("R2", "B", enc_id, 2025, None, "", "/p2.pdf",
                       "cuisine recette gastronomie")
        ajouter_rapport("R3", "C", enc_id, 2025, None, "", "/p3.pdf",
                       "python développement application")

        resultats = analyser_similarite("python développement logiciel application")

        # Les scores doivent être en ordre décroissant
        scores = [r['similarite'] for r in resultats]
        assert scores == sorted(scores, reverse=True)

    def test_resultats_contiennent_metadata(self, db_temporaire):
        """Chaque résultat doit contenir titre, auteurs, promotion, similarité."""
        ajouter_utilisateur("Enc", "enc@emsi.ma", "p", "encadrant")
        enc_id = get_utilisateur_by_email("enc@emsi.ma")['id']

        ajouter_rapport("Mon Titre", "Mon Auteur", enc_id, 2024,
                       None, "", "/p1.pdf", "test contenu")

        resultats = analyser_similarite("test contenu")
        assert 'titre' in resultats[0]
        assert 'auteurs' in resultats[0]
        assert 'promotion' in resultats[0]
        assert 'similarite' in resultats[0]
        assert resultats[0]['titre'] == "Mon Titre"