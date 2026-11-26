
import pandas as pd
import numpy as np

# 1. Charger les donnees
df = pd.read_csv("data/dossiers_administratifs_fictifs.csv")

# 2. Verifier les valeurs manquantes
print("===== VALEURS MANQUANTES =====")
print(df.isnull().sum())

# 3. Calculer le pourcentage des valeurs manquantes
print("\n===== POURCENTAGE DES VALEURS MANQUANTES =====")
print((df.isnull().mean() * 100).round(2))

# 4. Verifier les doublons
print("\n===== DOUBLONS =====")
print(df.duplicated().sum())

# 5. Afficher les types des variables
print("\n===== TYPES DES VARIABLES =====")
print(df.dtypes)
#6.verifier les valeurs incoerentes
print("\n===== VERIFICATION DES VALEURS INCOHERENTES =====")

print("Age negatif :",
      (df["age_demandeur"] < 0).sum())

print("Montant negatif :",
      (df["montant_demande"] < 0).sum())

print("Nombre de documents negatif :",
      (df["nb_documents"] < 0).sum())

print("Delai negatif :",
      (df["delai_traitement_jours"] < 0).sum())

# 7.Selection des variables numeriques
features = [
    "age_demandeur",
    "montant_demande",
    "revenu_mensuel",
    "nb_documents",
    "delai_traitement_jours",
    "nb_erreurs"
]

X = df[features].copy()

print("\n===== VARIABLES NUMERIQUES =====")
print(X.head())

print("\nDimensions de X :", X.shape)

# 8.Creer le dossier results si necessaire(Sauvegarder les données préparées)
import os

os.makedirs("results", exist_ok=True)

# Sauvegarder le dataset
df.to_csv("results/dossiers_prepares.csv", index=False)

print("\nDataset prepare et sauvegarde avec succes !")
