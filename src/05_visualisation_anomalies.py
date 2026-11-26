
# ==========================================
# PARTIE 5 : VISUALISATION DES ANOMALIES
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import os

print("\n===== PARTIE 5 : VISUALISATION DES ANOMALIES =====")

# 1. Chargement des donnees
df = pd.read_csv("results/dossiers_avec_anomalies.csv")

print("\nDimensions du dataset :", df.shape)

# Creation du dossier des graphiques
os.makedirs("results/figures", exist_ok=True)

# 2. Repartition des anomalies reelles et detectees

print("\n===== REPARTITION DES ANOMALIES =====")

print("\nAnomalies reelles :")
print(df["anomalie_reelle"].value_counts())

print("\nAnomalies Isolation Forest :")
print(df["anomalie_IF"].value_counts())

print("\nAnomalies LOF :")
print(df["anomalie_LOF"].value_counts())

# 3. Graphique : comparaison des anomalies

comparaison = pd.DataFrame({
    "Anomalies reelles": [
        (df["anomalie_reelle"] == 0).sum(),
        (df["anomalie_reelle"] == 1).sum()
    ],
    "Isolation Forest": [
        (df["anomalie_IF"] == 0).sum(),
        (df["anomalie_IF"] == 1).sum()
    ],
    "LOF": [
        (df["anomalie_LOF"] == 0).sum(),
        (df["anomalie_LOF"] == 1).sum()
    ]
}, index=["Normaux", "Anormaux"])

comparaison.plot(kind="bar", figsize=(10, 6))

plt.title("Comparaison des anomalies detectees")
plt.xlabel("Type de dossier")
plt.ylabel("Nombre de dossiers")
plt.xticks(rotation=0)
plt.legend(title="Methodes")
plt.tight_layout()

plt.savefig("results/figures/comparaison_anomalies.png")
plt.show()

# 4. Graphique : anomalies reelles et predictions

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

colonnes = [
    ("anomalie_reelle", "Anomalies reelles"),
    ("anomalie_IF", "Isolation Forest"),
    ("anomalie_LOF", "Local Outlier Factor")
]

for ax, (colonne, titre) in zip(axes, colonnes):
    valeurs = df[colonne].value_counts().reindex([0, 1], fill_value=0)

    ax.pie(
        valeurs,
        labels=["Normaux", "Anormaux"],
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title(titre)

plt.tight_layout()
plt.savefig("results/figures/repartition_anomalies.png")
plt.show()

# 5. Graphique : age et montant des dossiers

plt.figure(figsize=(10, 6))

plt.scatter(
    df["age_demandeur"],
    df["montant_demande"],
    c=df["anomalie_IF"],
    alpha=0.6
)

plt.title("Detection des anomalies selon l'age et le montant")
plt.xlabel("Age du demandeur")
plt.ylabel("Montant demande")
plt.colorbar(label="0 = Normal / 1 = Anomalie")

plt.tight_layout()
plt.savefig("results/figures/anomalies_age_montant.png")
plt.show()

# 6. Identification des anomalies detectees par les deux modeles

anomalies_communes = df[
    (df["anomalie_IF"] == 1) &
    (df["anomalie_LOF"] == 1)
]

print("\n===== ANOMALIES DETECTEES PAR LES DEUX MODELES =====")

print("Nombre de dossiers detectes par les deux modeles :",
      len(anomalies_communes))

# Enregistrement des anomalies communes
anomalies_communes.to_csv(
    "results/anomalies_communes.csv",
    index=False
)

# 7. Comparaison des predictions avec les vraies anomalies

print("\n===== COMPARAISON AVEC LES ANOMALIES REELLES =====")

for colonne, nom in [
    ("anomalie_IF", "Isolation Forest"),
    ("anomalie_LOF", "LOF")
]:

    correctes = (
        (df[colonne] == 1) &
        (df["anomalie_reelle"] == 1)
    ).sum()

    print(f"{nom} : {correctes} anomalies correctement detectees")

# 8. Fin du programme

print("\nGraphiques enregistres dans results/figures/")
print("Fichier des anomalies communes : results/anomalies_communes.csv")

print("\n===== FIN PARTIE 5 =====")
