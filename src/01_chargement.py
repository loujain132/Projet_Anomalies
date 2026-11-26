
# ==========================================
# PROJET : DETECTION DES ANOMALIES
# PARTIE 1 : CHARGEMENT DES DONNEES
# ==========================================

# 1. Importation des bibliotheques
import pandas as pd
import numpy as np

# 2. Chargement du dataset
df = pd.read_csv("data/dossiers_administratifs_fictifs.csv")

# 3. Afficher les premieres lignes
print("\n===== PREMIERES LIGNES =====")
print(df.head())

# 4. Afficher le nombre de lignes et colonnes
print("\n===== DIMENSIONS DU DATASET =====")
print(df.shape)

# 5. Afficher les noms des colonnes
print("\n===== NOMS DES VARIABLES =====")
print(df.columns.tolist())

# 6. Informations generales
print("\n===== INFORMATIONS GENERALES =====")
df.info()

# 7. Statistiques descriptives
print("\n===== STATISTIQUES DESCRIPTIVES =====")
print(df.describe())

# 8. Verifier les valeurs manquantes
print("\n===== VALEURS MANQUANTES =====")
print(df.isnull().sum())

# 9. Verifier les doublons
print("\n===== DOUBLONS =====")
print(df.duplicated().sum())

# 10. Repartition des anomalies artificielles
print("\n===== REPARTITION DES ANOMALIES =====")
print(df["anomalie_reelle"].value_counts())

print("\nChargement termine avec succes !")
