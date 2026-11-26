
# ==========================================
# PARTIE 4 : DETECTION AUTOMATIQUE DES ANOMALIES
# ==========================================

import pandas as pd
import numpy as np
import os

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

print("\n===== PARTIE 4 : DETECTION DES ANOMALIES =====")

# 1. Chargement des donnees
df = pd.read_csv("data/dossiers_administratifs_fictifs.csv")

print("\nDimensions du dataset :", df.shape)

# 2. Separation des variables

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

X = df[colonnes_numeriques + colonnes_categorielles]

# Les anomalies reelles servent uniquement a l'evaluation
y_reel = pd.to_numeric(
    df["anomalie_reelle"],
    errors="coerce"
).fillna(0).astype(int)

# ==========================================
# 3. DETECTION PAR REGLES SIMPLES
# ==========================================

print("\n===== DETECTION PAR REGLES =====")

df["anomalie_regles"] = 0
raisons = [[] for _ in range(len(df))]


def ajouter_regle(condition, nom_regle):
    indices = np.where(condition.fillna(False).to_numpy())[0]

    for i in indices:
        df.loc[df.index[i], "anomalie_regles"] = 1
        raisons[i].append(nom_regle)


# Regle 1 : age anormal
ajouter_regle(
    (df["age_demandeur"] < 18) |
    (df["age_demandeur"] > 100),
    "Age hors limites normales"
)

# Regle 2 : montant demande tres eleve par rapport au revenu
ajouter_regle(
    (df["revenu_mensuel"] > 0) &
    (df["montant_demande"] > 5 * df["revenu_mensuel"]),
    "Montant superieur a 5 fois le revenu mensuel"
)

# Regles statistiques : methode IQR
for colonne in colonnes_numeriques:

    q1 = df[colonne].quantile(0.25)
    q3 = df[colonne].quantile(0.75)

    iqr = q3 - q1

    if iqr > 0:
        borne_inferieure = q1 - 1.5 * iqr
        borne_superieure = q3 + 1.5 * iqr

        ajouter_regle(
            (df[colonne] < borne_inferieure) |
            (df[colonne] > borne_superieure),
            f"Valeur extreme dans {colonne}"
        )

# Enregistrement des raisons
df["raisons_regles"] = [
    " ; ".join(liste) if liste else "Aucune anomalie detectee par les regles"
    for liste in raisons
]

pred_regles = df["anomalie_regles"].to_numpy()

print("Nombre d'anomalies detectees par les regles :",
      pred_regles.sum())

# ==========================================
# 4. PREPARATION DES DONNEES
# ==========================================

preparation_numerique = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("normalisation", StandardScaler())
])

preparation_categorielle = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encodage", OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    ))
])

preparation = ColumnTransformer([
    ("numerique", preparation_numerique, colonnes_numeriques),
    ("categorielle", preparation_categorielle, colonnes_categorielles)
])

X_prepare = preparation.fit_transform(X)

print("\nPreparation terminee.")
print("Dimensions apres preparation :", X_prepare.shape)

# ==========================================
# 5. DETECTION AVEC ISOLATION FOREST
# ==========================================

print("\n===== ISOLATION FOREST =====")

modele_if = IsolationForest(
    n_estimators=200,
    contamination=0.11,
    random_state=42
)

pred_if = modele_if.fit_predict(X_prepare)

# -1 = anomalie ; +1 = normal
pred_if = np.where(pred_if == -1, 1, 0)

print("Nombre d'anomalies detectees :", pred_if.sum())

# ==========================================
# 6. DETECTION AVEC LOF
# ==========================================

print("\n===== LOCAL OUTLIER FACTOR =====")

modele_lof = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.11
)

pred_lof = modele_lof.fit_predict(X_prepare)

# -1 = anomalie ; +1 = normal
pred_lof = np.where(pred_lof == -1, 1, 0)

print("Nombre d'anomalies detectees :", pred_lof.sum())

# ==========================================
# 7. EVALUATION DES METHODES
# ==========================================

def evaluer_modele(nom, y_true, y_pred):

    print(f"\n===== EVALUATION : {nom} =====")

    matrice = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    )

    print("\nMatrice de confusion :")
    print(matrice)

    tn, fp, fn, tp = matrice.ravel()

    print("\nVrais negatifs :", tn)
    print("Faux positifs :", fp)
    print("Faux negatifs :", fn)
    print("Vrais positifs :", tp)

    print("\nRapport de classification :")
    print(classification_report(
        y_true,
        y_pred,
        zero_division=0
    ))

    print("Accuracy :", accuracy_score(y_true, y_pred))
    print("Precision :", precision_score(
        y_true, y_pred, zero_division=0
    ))
    print("Recall :", recall_score(
        y_true, y_pred, zero_division=0
    ))
    print("F1-score :", f1_score(
        y_true, y_pred, zero_division=0
    ))


# Evaluation des trois methodes
evaluer_modele("REGLES", y_reel, pred_regles)
evaluer_modele("ISOLATION FOREST", y_reel, pred_if)
evaluer_modele("LOF", y_reel, pred_lof)

# ==========================================
# 8. COMPARAISON DES METHODES
# ==========================================

print("\n===== COMPARAISON DES METHODES =====")

comparaison = pd.DataFrame({
    "Methode": [
        "Regles",
        "Isolation Forest",
        "LOF"
    ],
    "Nombre_anomalies": [
        pred_regles.sum(),
        pred_if.sum(),
        pred_lof.sum()
    ],
    "Accuracy": [
        accuracy_score(y_reel, pred_regles),
        accuracy_score(y_reel, pred_if),
        accuracy_score(y_reel, pred_lof)
    ],
    "Precision": [
        precision_score(y_reel, pred_regles, zero_division=0),
        precision_score(y_reel, pred_if, zero_division=0),
        precision_score(y_reel, pred_lof, zero_division=0)
    ],
    "Recall": [
        recall_score(y_reel, pred_regles, zero_division=0),
        recall_score(y_reel, pred_if, zero_division=0),
        recall_score(y_reel, pred_lof, zero_division=0)
    ],
    "F1_score": [
        f1_score(y_reel, pred_regles, zero_division=0),
        f1_score(y_reel, pred_if, zero_division=0),
        f1_score(y_reel, pred_lof, zero_division=0)
    ]
})

print(comparaison.to_string(index=False))

# ==========================================
# 9. ENREGISTREMENT DES RESULTATS
# ==========================================

df["anomalie_IF"] = pred_if
df["anomalie_LOF"] = pred_lof

os.makedirs("results", exist_ok=True)

df.to_csv(
    "results/dossiers_avec_anomalies.csv",
    index=False
)

comparaison.to_csv(
    "results/comparaison_methodes.csv",
    index=False
)

print("\nFichiers sauvegardes avec succes !")
print("1. results/dossiers_avec_anomalies.csv")
print("2. results/comparaison_methodes.csv")

print("\n===== FIN PARTIE 4 =====")
