from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

app = FastAPI(
    title="NEXORA AI API",
    description="API de détection des anomalies administratives",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "results" / "dossiers_avec_anomalies.csv"

MODELES = {
    "regles": "anomalie_regles",
    "Isolation Forest": "anomalie_IF",
    "LOF": "anomalie_LOF"
}


class QuestionAssistant(BaseModel):
    question: str



def calculer_variables_inhabituelles(df):
    colonnes_numeriques = [
        "age_demandeur",
        "montant_demande",
        "revenu_mensuel",
        "nb_documents",
        "delai_traitement_jours",
        "nb_erreurs"
    ]

    colonnes_categorielles = [
        "type_dossier",
        "region"
    ]

    variables_par_ligne = [[] for _ in range(len(df))]

    # Analyse des variables numériques avec la méthode IQR
    for colonne in colonnes_numeriques:
        if colonne not in df.columns:
            continue

        q1 = df[colonne].quantile(0.25)
        q3 = df[colonne].quantile(0.75)
        iqr = q3 - q1

        for i, valeur in enumerate(df[colonne]):
            if pd.isna(valeur):
                variables_par_ligne[i].append(f"{colonne} (valeur manquante)")
            elif iqr > 0:
                borne_inf = q1 - 1.5 * iqr
                borne_sup = q3 + 1.5 * iqr

                if valeur < borne_inf or valeur > borne_sup:
                    variables_par_ligne[i].append(colonne)

    # Analyse des catégories rares
    for colonne in colonnes_categorielles:
        if colonne not in df.columns:
            continue

        frequences = df[colonne].value_counts(normalize=True)

        for i, valeur in enumerate(df[colonne]):
            if pd.isna(valeur):
                variables_par_ligne[i].append(
                    f"{colonne} (valeur manquante)"
                )
            elif frequences.get(valeur, 0) <= 0.05:
                variables_par_ligne[i].append(
                    f"{colonne} (catégorie rare)"
                )

    return [
        " ; ".join(variables) if variables else "Aucune variable inhabituelle"
        for variables in variables_par_ligne
    ]



def charger_donnees():
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Fichier CSV introuvable."
        )

    df = pd.read_csv(CSV_PATH)

    colonnes_requises = [
        "id_dossier",
        "anomalie_reelle",
        "anomalie_regles",
        "anomalie_IF",
        "anomalie_LOF"
    ]

    for colonne in colonnes_requises:
        if colonne not in df.columns:
            raise HTTPException(
                status_code=500,
                detail=f"Colonne manquante : {colonne}"
            )
        
    df["variables_inhabituelles"] = calculer_variables_inhabituelles(df)
    return df


def convertir_records(df):
    return (
        df.astype(object)
        .where(pd.notna(df), None)
        .to_dict(orient="records")
    )


def obtenir_contexte_projet():
    df = charger_donnees()

    total = len(df)
    anomalies = int(df["anomalie_reelle"].sum())
    normaux = total - anomalies

    comparaison = {
        nom: calculer_metriques(df, colonne)
        for nom, colonne in MODELES.items()
    }

    meilleur_modele = max(
        comparaison,
        key=lambda nom: comparaison[nom]["f1_score"]
    )

    return {
        "total_dossiers": total,
        "anomalies_reelles": anomalies,
        "dossiers_normaux": normaux,
        "comparaison": comparaison,
        "meilleur_modele": meilleur_modele
    }


def generer_reponse_assistant(question: str):
    q = question.lower().strip()

    contexte = obtenir_contexte_projet()

    total = contexte["total_dossiers"]
    anomalies = contexte["anomalies_reelles"]
    normaux = contexte["dossiers_normaux"]
    meilleur = contexte["meilleur_modele"]
    comparaison = contexte["comparaison"]


     # Difference entre faux positif et faux negatif
    if "difference" in q or "différence" in q:
        if "faux positif" in q and (
            "faux negatif" in q or "faux négatif" in q
        ):
            return (
                "Un faux positif est un dossier normal "
                "que le modèle classe comme anomalie. "
                "Un faux négatif est une anomalie réelle "
                "que le modèle ne détecte pas."
            )
        
    # Faux positifs
    if "faux positif" in q:
        modele = "LOF" if "lof" in q else meilleur
        nombre = comparaison[modele]["FP"]
        return f"Le modèle {modele} a détecté {nombre} faux positifs."

    # Faux négatifs
    if "faux negatif" in q or "faux négatif" in q:
        modele = "LOF" if "lof" in q else meilleur
        nombre = comparaison[modele]["FN"]
        return f"Le modèle {modele} a détecté {nombre} faux négatifs."

    # Nombre de dossiers et anomalies
    if any(mot in q for mot in ["combien", "nombre", "total"]):
        if "anomalie" in q:
            return f"Notre dataset contient {anomalies} anomalies réelles."
        return f"Notre dataset contient {total} dossiers administratifs."

    # Dossiers normaux
    if any(mot in q for mot in ["normal", "normaux"]):
        return f"Le dataset contient {normaux} dossiers normaux."


    # Pourquoi LOF est le meilleur modèle
    if "pourquoi" in q and ("lof" in q or "meilleur" in q):
        m = comparaison["LOF"]

        return (
            f"LOF est le meilleur modèle de notre projet selon le F1-score "
            f"({m['f1_score']:.4f}). "
            f"Il présente une précision de {m['precision']:.4f} "
            f"et un rappel de {m['rappel']:.4f}. "
            f"Il a détecté {m['TP']} anomalies réelles, "
            f"avec {m['FP']} faux positifs et {m['FN']} faux négatifs. "
            f"Cependant, son F1-score reste modeste, "
            f"donc le modèle peut encore être amélioré."
        )

    
    # Meilleur modèle
    if any(mot in q for mot in ["meilleur", "performance"]):
        score = comparaison[meilleur]["f1_score"]
        return (
            f"Le meilleur modèle selon le F1-score est {meilleur}, "
            f"avec un score de {score:.4f}."
        )

    # Fraude
    if "fraude" in q:
        return (
            "Non. Une anomalie statistique ne signifie pas "
            "automatiquement une fraude. Elle indique seulement "
            "un comportement inhabituel qui nécessite une vérification."
        )

    # Isolation Forest
    if "isolation forest" in q:
        return (
            "Isolation Forest est un algorithme de Machine Learning "
            "qui détecte les observations atypiques en les isolant "
            "du reste des données."
        )


    # Interpretation du F1-score
    if "f1" in q and ("signifie" in q or "score" in q):
        m = comparaison["LOF"]

        return (
            f"Le F1-score de LOF est de {m['f1_score']:.4f}. "
            "Ce score combine la précision et le rappel. "
            "Un score de 0.3455 indique que le modèle "
            "a encore des difficultés à détecter correctement "
            "les anomalies. Il peut être amélioré en ajustant "
            "les paramètres du modèle et en travaillant sur les données."
        )


        # Interpretation du Recall
    if "recall" in q or "rappel" in q:
        m = comparaison["LOF"]

        return (
            f"Le Recall de LOF est de {m['rappel']:.4f}, "
            "soit 34.55%. "
            f"Le modèle a détecté {m['TP']} anomalies réelles "
            f"sur {m['TP'] + m['FN']} anomalies réelles au total. "
            "Le Recall mesure la capacité du modèle à retrouver "
            "les anomalies réellement présentes dans les données."
        )

    
    # LOF
    if "lof" in q:
        return (
            "LOF (Local Outlier Factor) détecte les observations "
            "atypiques en comparant leur densité locale avec celle "
            "de leurs voisins."
        )

    return (
        "Je peux répondre aux questions concernant les statistiques, "
        "les modèles de détection, les faux positifs, les faux négatifs "
        "et les anomalies du projet NEXORA AI. "
        "Peux-tu reformuler ta question ?"
    )


def calculer_metriques(df, colonne):
    reel = df["anomalie_reelle"].astype(int)
    prediction = df[colonne].astype(int)

    tp = int(((reel == 1) & (prediction == 1)).sum())
    fp = int(((reel == 0) & (prediction == 1)).sum())
    fn = int(((reel == 1) & (prediction == 0)).sum())
    tn = int(((reel == 0) & (prediction == 0)).sum())

    total = len(df)

    precision = tp / (tp + fp) if tp + fp else 0
    rappel = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * rappel / (precision + rappel)
        if precision + rappel else 0
    )
    accuracy = (tp + tn) / total if total else 0

    return {
        "dossiers_detectes": int(prediction.sum()),
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": round(precision, 4),
        "rappel": round(rappel, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4)
    }


@app.get("/")
def accueil():
    return {
        "message": "Bienvenue dans NEXORA AI API",
        "status": "Online"
    }


@app.get("/api/dossiers")
def obtenir_dossiers():
    df = charger_donnees()

    return {
        "total": len(df),
        "dossiers": convertir_records(df)
    }


@app.get("/api/statistiques")
def obtenir_statistiques():
    df = charger_donnees()

    total = len(df)
    anomalies = int((df["anomalie_reelle"] == 1).sum())

    return {
        "total_dossiers": total,
        "anomalies": anomalies,
        "dossiers_normaux": total - anomalies,
        "taux_anomalies": round(anomalies / total * 100, 2)
        if total else 0
    }


@app.get("/api/modeles")
def obtenir_modeles():
    df = charger_donnees()

    return {
        "Isolation Forest": int(df["anomalie_IF"].sum()),
        "LOF": int(df["anomalie_LOF"].sum()),
        "Regles": int(df["anomalie_regles"].sum())
    }


@app.get("/api/dossiers-suspects")
def obtenir_dossiers_suspects():
    df = charger_donnees()

    colonnes = list(MODELES.values())

    masque = df[colonnes].eq(1).any(axis=1)
    suspects = df[masque].copy()

    return {
        "total_suspects": len(suspects),
        "dossiers": convertir_records(suspects)
    }


@app.get("/api/comparaison")
def comparer_modeles():
    df = charger_donnees()

    resultats = {}

    for nom, colonne in MODELES.items():
        resultats[nom] = calculer_metriques(df, colonne)

    meilleur_modele = max(
        resultats,
        key=lambda nom: resultats[nom]["f1_score"]
    )

    return {
        "comparaison": resultats,
        "meilleur_modele": meilleur_modele
    }


@app.get("/api/erreurs")
def obtenir_erreurs(modele: str = "LOF"):
    df = charger_donnees()

    if modele not in MODELES:
        raise HTTPException(
            status_code=400,
            detail="Modèle invalide. Choisir regles, Isolation Forest ou LOF."
        )

    colonne = MODELES[modele]

    reel = df["anomalie_reelle"].astype(int)
    prediction = df[colonne].astype(int)

    faux_positifs = df[(reel == 0) & (prediction == 1)]
    faux_negatifs = df[(reel == 1) & (prediction == 0)]

    return {
        "modele": modele,
        "nombre_faux_positifs": len(faux_positifs),
        "nombre_faux_negatifs": len(faux_negatifs),
        "faux_positifs": convertir_records(faux_positifs),
        "faux_negatifs": convertir_records(faux_negatifs)
    }


@app.post("/api/assistant")
def assistant(question: QuestionAssistant):
    texte = question.question.strip()

    if not texte:
        raise HTTPException(
            status_code=400,
            detail="La question ne peut pas être vide."
        )

    reponse = generer_reponse_assistant(texte)

    return {
        "question": texte,
        "reponse": reponse
    }