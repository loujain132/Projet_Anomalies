
# ==========================================
# PARTIE 7 : RAPPORT FINAL DU PROJET
# ==========================================

import pandas as pd
import os
from datetime import datetime

print("\n===== PARTIE 7 : RAPPORT FINAL =====")

# 1. Chargement des donnees
df = pd.read_csv("results/dossiers_avec_anomalies.csv")
evaluation = pd.read_csv("results/evaluation_finale.csv")

# 2. Statistiques generales

nombre_dossiers = len(df)

anomalies_reelles = (df["anomalie_reelle"] == 1).sum()
dossiers_normaux = (df["anomalie_reelle"] == 0).sum()

anomalies_if = (df["anomalie_IF"] == 1).sum()
anomalies_lof = (df["anomalie_LOF"] == 1).sum()

# 3. Identification du meilleur modele
meilleur = evaluation.loc[
    evaluation["F1_score"].idxmax()
]

# 4. Creation du rapport
rapport = f"""
====================================================
       RAPPORT FINAL DU PROJET
       DETECTION DES ANOMALIES
       DANS LES DOSSIERS ADMINISTRATIFS
====================================================

Date de generation : {datetime.now().strftime("%d/%m/%Y %H:%M")}

1. PRESENTATION DU DATASET
--------------------------
Nombre total de dossiers : {nombre_dossiers}
Dossiers normaux : {dossiers_normaux}
Anomalies reelles : {anomalies_reelles}

2. RESULTATS DE LA DETECTION
----------------------------
Anomalies detectees par Isolation Forest : {anomalies_if}
Anomalies detectees par LOF : {anomalies_lof}

3. COMPARAISON DES MODELES
--------------------------
{evaluation.to_string(index=False)}

4. MEILLEUR MODELE
------------------
Modele : {meilleur['Modele']}
Accuracy : {meilleur['Accuracy']:.3f}
Precision : {meilleur['Precision']:.3f}
Recall : {meilleur['Recall']:.3f}
F1-score : {meilleur['F1_score']:.3f}

5. CONCLUSION
-------------
Le projet a permis d'explorer les donnees,
de preparer le dataset et de detecter
automatiquement les anomalies.

Deux algorithmes ont ete testes :
Isolation Forest et Local Outlier Factor.

Le modele ayant le meilleur F1-score est :
{meilleur['Modele']}.

Les resultats peuvent etre utilises comme
base pour ameliorer le systeme de detection
des anomalies dans les dossiers administratifs.

====================================================
                 FIN DU RAPPORT
====================================================
"""

# 5. Affichage du rapport
print(rapport)

# 6. Sauvegarde du rapport
os.makedirs("results", exist_ok=True)

with open(
    "results/rapport_final.txt",
    "w",
    encoding="utf-8"
) as fichier:
    fichier.write(rapport)

print("\nRapport genere avec succes !")
print("Fichier : results/rapport_final.txt")

print("\n===== FIN PARTIE 7 =====")
