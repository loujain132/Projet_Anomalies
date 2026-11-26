
# ==========================================
# PARTIE 6 : EVALUATION FINALE
# ==========================================

import pandas as pd
import numpy as np
import os

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

print("\n===== PARTIE 6 : EVALUATION FINALE =====")

# 1. Chargement des resultats
df = pd.read_csv("results/dossiers_avec_anomalies.csv")

y_reel = df["anomalie_reelle"]

# 2. Liste des modeles
modeles = {
    "Isolation Forest": df["anomalie_IF"],
    "Local Outlier Factor": df["anomalie_LOF"]
}

# 3. Evaluation des modeles

resultats = []

for nom, predictions in modeles.items():

    print("\n================================")
    print(nom)
    print("================================")

    accuracy = accuracy_score(y_reel, predictions)

    precision = precision_score(
        y_reel, predictions, zero_division=0
    )

    recall = recall_score(
        y_reel, predictions, zero_division=0
    )

    f1 = f1_score(
        y_reel, predictions, zero_division=0
    )

    matrice = confusion_matrix(y_reel, predictions)

    print("\nMatrice de confusion :")
    print(matrice)

    print("\nRapport de classification :")
    print(classification_report(
        y_reel,
        predictions,
        zero_division=0
    ))

    resultats.append({
        "Modele": nom,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1_score": f1
    })

# 4. Tableau comparatif

df_resultats = pd.DataFrame(resultats)

print("\n===== TABLEAU COMPARATIF =====")
print(df_resultats.round(3))

# 5. Identification du meilleur modele selon le F1-score

meilleur_modele = df_resultats.loc[
    df_resultats["F1_score"].idxmax()
]

print("\n===== MEILLEUR MODELE =====")
print("Modele :", meilleur_modele["Modele"])
print("F1-score :", round(meilleur_modele["F1_score"], 3))

# 6. Identification des erreurs de detection

for nom, predictions in modeles.items():

    faux_positifs = (
        (y_reel == 0) & (predictions == 1)
    ).sum()

    faux_negatifs = (
        (y_reel == 1) & (predictions == 0)
    ).sum()

    print(f"\n{nom}")
    print("Faux positifs :", faux_positifs)
    print("Faux negatifs :", faux_negatifs)

# 7. Enregistrement des resultats

os.makedirs("results", exist_ok=True)

df_resultats.to_csv(
    "results/evaluation_finale.csv",
    index=False
)

print("\nEvaluation enregistree avec succes !")
print("Fichier : results/evaluation_finale.csv")

print("\n===== FIN PARTIE 6 =====")
