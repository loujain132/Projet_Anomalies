
# ==========================================
# PARTIE 8 : VERIFICATION FINALE DU PROJET
# ==========================================

import os
import pandas as pd

print("\n===== PARTIE 8 : VERIFICATION FINALE =====")

# 1. Verification des fichiers principaux

fichiers = [
    "data/dossiers_administratifs_fictifs.csv",
    "results/dossiers_prepares.csv",
    "results/dossiers_avec_anomalies.csv",
    "results/anomalies_communes.csv",
    "results/evaluation_finale.csv",
    "results/rapport_final.txt",
    "results/figures/comparaison_anomalies.png",
    "results/figures/repartition_anomalies.png",
    "results/figures/anomalies_age_montant.png"
]

print("\n===== VERIFICATION DES FICHIERS =====")

for fichier in fichiers:

    if os.path.exists(fichier):
        print("[OK] ", fichier)
    else:
        print("[ABSENT] ", fichier)

# 2. Verification du dataset final

print("\n===== VERIFICATION DU DATASET FINAL =====")

if os.path.exists("results/dossiers_avec_anomalies.csv"):

    df = pd.read_csv("results/dossiers_avec_anomalies.csv")

    print("Nombre de lignes :", len(df))
    print("Nombre de colonnes :", len(df.columns))

    print("\nColonnes disponibles :")
    print(df.columns.tolist())

    print("\nValeurs manquantes :")
    print(df.isnull().sum())

# 3. Verification des predictions

print("\n===== VERIFICATION DES PREDICTIONS =====")

if os.path.exists("results/dossiers_avec_anomalies.csv"):

    print("\nAnomalies reelles :")
    print(df["anomalie_reelle"].value_counts())

    print("\nIsolation Forest :")
    print(df["anomalie_IF"].value_counts())

    print("\nLOF :")
    print(df["anomalie_LOF"].value_counts())

# 4. Verification de l'evaluation

print("\n===== EVALUATION DES MODELES =====")

if os.path.exists("results/evaluation_finale.csv"):

    evaluation = pd.read_csv("results/evaluation_finale.csv")

    print(evaluation.to_string(index=False))

# 5. Bilan final

print("\n===== BILAN DU PROJET =====")

if all(os.path.exists(f) for f in fichiers):

    print("Tous les fichiers attendus sont presents.")

else:

    print("Certains fichiers sont absents.")
    print("Verifier les executions des parties precedentes.")

print("\n===== FIN PARTIE 8 =====")
