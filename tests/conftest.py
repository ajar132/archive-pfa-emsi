"""
Configuration partagée pour les tests pytest.
Crée une base de données temporaire pour chaque test.
"""
import os
import sys
import gc
import pytest
import tempfile

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def db_temporaire(monkeypatch):
    """
    Crée une base SQLite temporaire pour chaque test.
    Garantit l'isolation des tests (aucun effet de bord sur la vraie base).
    """
    # Créer un fichier temporaire pour la base
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    # Patcher le chemin de la base dans le module database
    from src import database
    monkeypatch.setattr(database, 'DB_PATH', db_path)

    # Créer les tables dans la base temporaire
    database.create_tables()

    yield db_path

    # Nettoyage : forcer la fermeture des connexions SQLite avant suppression
    gc.collect()  # libère les références aux connexions

    # Tentative de suppression avec gestion Windows
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            # Sous Windows, parfois le fichier reste verrouillé
            # On laisse Windows nettoyer le dossier temp lui-même
            pass