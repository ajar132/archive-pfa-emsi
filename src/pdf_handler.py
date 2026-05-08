import os
import shutil
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.database import get_connection

# Dossier de stockage des PDFs
STORAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'storage', 'rapports')

# ─────────────────────────────────────────
#  EXTRACTION DU TEXTE
# ─────────────────────────────────────────

def extraire_texte(chemin_pdf):
    """Extrait le texte d'un PDF via PyMuPDF."""
    try:
        doc = fitz.open(chemin_pdf)
        texte = " ".join(page.get_text() for page in doc)
        doc.close()
        if not texte.strip():
            print("⚠️ Avertissement : PDF sans couche texte (image scannée).")
            return None
        return texte
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")
        return None

# ─────────────────────────────────────────
#  COPIE DU FICHIER PDF
# ─────────────────────────────────────────

def copier_pdf(chemin_source, titre, promotion):
    """
    Copie le PDF dans le dossier de stockage sécurisé.
    Renomme le fichier : ANNEE_TITRE.pdf
    """
    try:
        # Nettoyer le titre pour le nom de fichier
        titre_propre = titre.strip().replace(' ', '_')
        titre_propre = ''.join(c for c in titre_propre
                               if c.isalnum() or c in ('_', '-'))

        nom_fichier  = f"{promotion}_{titre_propre}.pdf"
        chemin_dest  = os.path.join(STORAGE_PATH, nom_fichier)

        # Si un fichier du même nom existe déjà, ajouter un suffixe
        compteur = 1
        while os.path.exists(chemin_dest):
            nom_fichier = f"{promotion}_{titre_propre}_{compteur}.pdf"
            chemin_dest = os.path.join(STORAGE_PATH, nom_fichier)
            compteur += 1

        shutil.copy2(chemin_source, chemin_dest)
        print(f"✅ PDF copié : {nom_fichier}")
        return chemin_dest

    except Exception as e:
        print(f"❌ Erreur lors de la copie : {e}")
        return None

# ─────────────────────────────────────────
#  ANALYSE DE SIMILARITÉ (CU08)
# ─────────────────────────────────────────

def analyser_similarite(texte_nouveau):
    """
    Compare le texte d'un nouveau rapport avec tous
    les rapports existants en base.
    Retourne une liste triée par similarité décroissante.
    """
    if not texte_nouveau:
        print("⚠️ Analyse impossible : pas de texte extractible.")
        return []

    # Récupérer tous les rapports avec texte extrait
    conn = get_connection()
    rapports = conn.execute('''
        SELECT id, titre, auteurs, promotion, texte_extrait
        FROM rapport
        WHERE texte_extrait IS NOT NULL
    ''').fetchall()
    conn.close()

    if not rapports:
        print("ℹ️ Aucun rapport existant pour comparer.")
        return []

    # Préparer les textes
    textes   = [texte_nouveau] + [r['texte_extrait'] for r in rapports]

    # Calcul TF-IDF + similarité cosinus
    vectorizer = TfidfVectorizer()
    matrice    = vectorizer.fit_transform(textes)
    scores     = cosine_similarity(matrice[0:1], matrice[1:])[0]

    # Construire les résultats
    resultats = []
    for rapport, score in zip(rapports, scores):
        resultats.append({
            'id'         : rapport['id'],
            'titre'      : rapport['titre'],
            'auteurs'    : rapport['auteurs'],
            'promotion'  : rapport['promotion'],
            'similarite' : round(score * 100, 1)
        })

    # Trier par similarité décroissante
    resultats.sort(key=lambda x: x['similarite'], reverse=True)
    return resultats

# ─────────────────────────────────────────
#  FLUX COMPLET DE DÉPÔT
# ─────────────────────────────────────────

def deposer_rapport(chemin_source, titre, auteurs, encadrant_id,
                    promotion, option_id, mots_cles):
    """
    Orchestre le dépôt complet :
    1. Copie le PDF
    2. Extrait le texte
    3. Analyse la similarité
    4. Enregistre en base
    Retourne (rapport_id, resultats_similarite)
    """
    from src.crud import ajouter_rapport

    # Étape 1 — Copie
    chemin_dest = copier_pdf(chemin_source, titre, promotion)
    if not chemin_dest:
        return None, []

    # Étape 2 — Extraction texte
    texte = extraire_texte(chemin_dest)

    # Étape 3 — Similarité
    resultats = analyser_similarite(texte)

    # Afficher les résultats
    if resultats:
        print("\n📊 Analyse de similarité :")
        print(f"{'Titre':<40} {'Auteurs':<20} {'Promo':<6} {'Score':>6}")
        print("-" * 75)
        for r in resultats:
            print(f"{r['titre']:<40} {r['auteurs']:<20} "
                  f"{r['promotion']:<6} {r['similarite']:>5}%")
        print()

    # Étape 4 — Enregistrement en base
    rapport_id = ajouter_rapport(
        titre, auteurs, encadrant_id, promotion,
        option_id, mots_cles, chemin_dest, texte
    )

    return rapport_id, resultats