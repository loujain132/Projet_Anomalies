
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 1. Charger les donnees preparees
df = pd.read_csv("results/dossiers_prepares.csv")

print("===== INFORMATIONS GENERALES =====")
print(df.info())

# 2. Statistiques descriptives
print("\n===== STATISTIQUES DESCRIPTIVES =====")
print(df.describe())

# Selection des variables numeriques
features = [
    "age_demandeur",
    "montant_demande",
    "revenu_mensuel",
    "nb_documents",
    "delai_traitement_jours",
    "nb_erreurs"
]

X = df[features]

# Creer le dossier pour les graphiques
os.makedirs("results/figures", exist_ok=True)

# 3. Distribution des variables numeriques
print("\n===== ANALYSE DES DISTRIBUTIONS =====")

for col in features:
    print(f"\nVariable : {col}")
    print("Moyenne :", X[col].mean())
    print("Mediane :", X[col].median())
    print("Minimum :", X[col].min())
    print("Maximum :", X[col].max())

    plt.figure(figsize=(8, 5))
    plt.hist(X[col], bins=20, edgecolor="black")
    plt.title(f"Distribution de {col}")
    plt.xlabel(col)
    plt.ylabel("Frequence")
    plt.tight_layout()
    plt.savefig(f"results/figures/distribution_{col}.png")
    plt.close()

# 4. Detection des valeurs aberrantes avec IQR
print("\n===== DETECTION DES OUTLIERS =====")

for col in features:
    Q1 = X[col].quantile(0.25)
    Q3 = X[col].quantile(0.75)

    IQR = Q3 - Q1

    borne_inf = Q1 - 1.5 * IQR
    borne_sup = Q3 + 1.5 * IQR

    outliers = X[
        (X[col] < borne_inf) |
        (X[col] > borne_sup)
    ]

    print(f"\nVariable : {col}")
    print("Borne inferieure :", borne_inf)
    print("Borne superieure :", borne_sup)
    print("Nombre de valeurs aberrantes :", len(outliers))

    plt.figure(figsize=(8, 5))
    plt.boxplot(X[col])
    plt.title(f"Boxplot de {col}")
    plt.ylabel(col)
    plt.tight_layout()
    plt.savefig(f"results/figures/boxplot_{col}.png")
    plt.close()

# 5. Analyse des anomalies reelles
print("\n===== ANALYSE DES ANOMALIES REELLES =====")

print(df["anomalie_reelle"].value_counts())

print("\nPourcentage des anomalies :")
print(df["anomalie_reelle"].value_counts(normalize=True) * 100)

print("\n===== TYPES D'ANOMALIES =====")
print(df["type_anomalie"].value_counts())

# Graphique des anomalies
df["anomalie_reelle"].value_counts().plot(
    kind="bar",
    figsize=(7, 5),
    edgecolor="black"
)

plt.title("Repartition des anomalies reelles")
plt.xlabel("Anomalie reelle")
plt.ylabel("Nombre de dossiers")
plt.tight_layout()
plt.savefig("results/figures/repartition_anomalies.png")
plt.close()

print("\n===== ANALYSE EXPLORATOIRE TERMINEE =====")
print("Les graphiques sont sauvegardes dans results/figures/")
