import { useState, useEffect, useMemo } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const navItems = [
  ["Dashboard", "⌂"],
  ["Dossiers administratifs", "▤"],
  ["Détection anomalies", "⌕"],
  ["Visualisations", "◷"],
  ["Rapports", "▧"],
  ["Assistant IA", "✧"],
];

const emptyStats = {
  total_dossiers: 0,
  anomalies: 0,
  dossiers_normaux: 0,
  taux_anomalies: 0,
};

const emptyModels = {
  Regles: 0,
  "Isolation Forest": 0,
  LOF: 0,
};

function App() {
  const [active, setActive] = useState("Dashboard");
  const [search, setSearch] = useState("");

  const [dossiers, setDossiers] = useState([]);
  const [statistiques, setStatistiques] = useState(emptyStats);
  const [modeles, setModeles] = useState(emptyModels);
  const [comparaison, setComparaison] = useState({});
  const [meilleurModele, setMeilleurModele] = useState("");
  const [suspects, setSuspects] = useState([]);
  const [erreurs, setErreurs] = useState(null);

  const [chargement, setChargement] = useState(true);
  const [erreurAPI, setErreurAPI] = useState("");

  const [messages, setMessages] = useState([
    {
      from: "ai",
      text: "Bonjour ! Je suis l'assistant NEXORA. Je peux vous aider à comprendre les résultats de détection.",
    },
  ]);

  const [question, setQuestion] = useState("");

  // Chargement de toutes les données depuis FastAPI
  useEffect(() => {
    let actif = true;

    const chargerDonnees = async () => {
      try {
        setChargement(true);
        setErreurAPI("");

        const endpoints = [
          "/api/dossiers",
          "/api/statistiques",
          "/api/modeles",
          "/api/comparaison",
          "/api/dossiers-suspects",
          "/api/erreurs",
        ];

        const responses = await Promise.all(
          endpoints.map((endpoint) =>
            fetch(`${API}${endpoint}`)
          )
        );

        const failed = responses.find((response) => !response.ok);

        if (failed) {
          throw new Error(
            `Erreur API : ${failed.status} ${failed.statusText}`
          );
        }

        const [
          dossiersData,
          statsData,
          modelesData,
          comparaisonData,
          suspectsData,
          erreursData,
        ] = await Promise.all(
          responses.map((response) => response.json())
        );

        if (!actif) return;

        const dossiersFormates = dossiersData.dossiers.map((d) => ({
          ...d,
          id: d.id_dossier,
          type: d.type_dossier || "Non précisé",
          region: d.region || "Non précisée",
          age: d.age_demandeur,
          montant: Number(d.montant_demande) || 0,
          statut:
            Number(d.anomalie_reelle) === 1
              ? "Anomalie"
              : "Normal",
        }));

        setDossiers(dossiersFormates);
        setStatistiques(statsData);
        setModeles(modelesData);
        setComparaison(comparaisonData.comparaison || {});
        setMeilleurModele(comparaisonData.meilleur_modele || "");
        setSuspects(suspectsData.dossiers || []);
        console.log("Nombre de dossiers suspects :", suspectsData.dossiers?.length);
        setErreurs(erreursData);
      } catch (error) {
        console.error("Erreur de chargement :", error);
        if (actif) {
          setErreurAPI(
            "Impossible de charger les données. Vérifiez que le serveur FastAPI fonctionne."
          );
        }
      } finally {
        if (actif) setChargement(false);
      }
    };

    chargerDonnees();

    return () => {
      actif = false;
    };
  }, []);

  // Recherche dans les dossiers
  const filtered = useMemo(() => {
    const terme = search.toLowerCase().trim();

    if (!terme) return dossiers;

    return dossiers.filter((d) =>
      `${d.id} ${d.type} ${d.region} ${d.statut}`
        .toLowerCase()
        .includes(terme)
    );
  }, [dossiers, search]);

  const goTo = (page) => {
    setActive(page);
    setSearch("");
  };

  // Calcul des données pour les graphiques
  const repartitionRegions = useMemo(
    () => compterParCategorie(dossiers, "region"),
    [dossiers]
  );

  const repartitionTypes = useMemo(
    () => compterParCategorie(dossiers, "type"),
    [dossiers]
  );

  const repartitionAges = useMemo(
    () =>
      compterParTranches(
        dossiers,
        "age_demandeur",
        [
          { label: "Moins de 20 ans", min: -Infinity, max: 20 },
          { label: "20–29 ans", min: 20, max: 30 },
          { label: "30–39 ans", min: 30, max: 40 },
          { label: "40–49 ans", min: 40, max: 50 },
          { label: "50–59 ans", min: 50, max: 60 },
          { label: "60 ans et plus", min: 60, max: Infinity },
        ]
      ),
    [dossiers]
  );

  const repartitionMontants = useMemo(
    () =>
      compterParTranches(
        dossiers,
        "montant_demande",
        [
          { label: "Moins de 2 000", min: -Infinity, max: 2000 },
          { label: "2 000–4 999", min: 2000, max: 5000 },
          { label: "5 000–7 999", min: 5000, max: 8000 },
          { label: "8 000–10 999", min: 8000, max: 11000 },
          { label: "11 000 et plus", min: 11000, max: Infinity },
        ]
      ),
    [dossiers]
  );

  const repartirAnomalies = useMemo(() => {
    const total = dossiers.length;
    const normales = dossiers.filter(
      (d) => Number(d.anomalie_reelle) === 0
    ).length;

    const anomalies = dossiers.filter(
      (d) => Number(d.anomalie_reelle) === 1
    ).length;

    return [
      { label: "Normaux", value: normales },
      { label: "Anomalies réelles", value: anomalies },
    ];
  }, [dossiers]);

  
const sendMessage = async () => {
  const texte = question.trim();

  if (!texte) return;

  setMessages((old) => [
    ...old,
    { from: "user", text: texte },
  ]);

  setQuestion("");

  try {
    const response = await fetch(`${API}/api/assistant`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: texte,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Erreur du serveur.");
    }

    setMessages((old) => [
      ...old,
      {
        from: "ai",
        text: data.reponse,
      },
    ]);

  } catch (error) {
    console.error("Erreur Assistant IA :", error);

    setMessages((old) => [
      ...old,
      {
        from: "ai",
        text: "Désolé, impossible de contacter le serveur. Vérifiez que le Backend fonctionne.",
      },
    ]);
  }
};


  const valeurF1 = (nom) =>
    comparaison[nom]?.f1_score ?? 0;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">N</div>
          <div>
            <h2>
              NEXORA<span> AI</span>
            </h2>
            <small>INTELLIGENCE SYSTEM</small>
          </div>
        </div>

        <div className="nav-label">MENU PRINCIPAL</div>

        <nav>
          {navItems.map(([name, icon]) => (
            <button
              key={name}
              className={`nav-link ${
                active === name ? "active" : ""
              }`}
              onClick={() => goTo(name)}
            >
              <span className="nav-icon">{icon}</span>
              <span>{name}</span>
              {active === name && (
                <span className="nav-indicator" />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="online-dot" />
          <span>
            {erreurAPI ? "Connexion API indisponible" : "Système opérationnel"}
          </span>
          <small>VERSION 2.0.0</small>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <div className="breadcrumb">
              NEXORA AI / <span>{active}</span>
            </div>
            <h2>{active}</h2>
          </div>

          <div className="top-actions">
            <div className="search-box">
              <span>⌕</span>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Rechercher..."
              />
            </div>

            <div className="profile">
              <div className="profile-avatar">A</div>
              <div>
                <strong>Administrateur</strong>
                <small>Workspace</small>
              </div>
            </div>
          </div>
        </header>

        <div className="page-content">
          {chargement && (
            <div className="panel">
              Chargement des données de NEXORA AI...
            </div>
          )}

          {erreurAPI && (
            <div className="panel" style={{ color: "#c85e91" }}>
              {erreurAPI}
            </div>
          )}

          {!chargement && !erreurAPI && (
            <>
              {/* DASHBOARD */}
              {active === "Dashboard" && (
                <>
                  <section className="welcome-banner">
                    <div>
                      <span className="eyebrow">
                        PLATEFORME INTELLIGENTE
                      </span>

                      <h1>
                        Bienvenue dans <span>NEXORA AI</span>
                      </h1>

                      <p>
                        Surveillez, analysez et détectez les anomalies
                        dans vos dossiers administratifs.
                      </p>

                      <button
                        className="primary-btn"
                        onClick={() => goTo("Détection anomalies")}
                      >
                        Lancer l'analyse <span>→</span>
                      </button>
                    </div>

                    <div className="hero-orb">
                      <div className="orb-core">N</div>
                    </div>
                  </section>

                  <div className="section-heading">
                    <div>
                      <span className="eyebrow">VUE GLOBALE</span>
                      <h2>Tableau de bord</h2>
                    </div>
                    <span className="demo-label">
                      DONNÉES DU DATASET
                    </span>
                  </div>

                  <div className="stats-grid">
                    <Stat
                      title="Total des dossiers"
                      value={statistiques.total_dossiers}
                      detail="Dossiers chargés"
                      icon="▤"
                    />

                    <Stat
                      title="Anomalies réelles"
                      value={statistiques.anomalies}
                      detail={`${statistiques.taux_anomalies}% du total`}
                      icon="⚠"
                    />

                    <Stat
                      title="Isolation Forest"
                      value={modeles["Isolation Forest"] ?? 0}
                      detail="Anomalies détectées"
                      icon="◈"
                    />

                    <Stat
                      title="LOF"
                      value={modeles.LOF ?? 0}
                      detail="Anomalies détectées"
                      icon="✧"
                    />
                  </div>

                  <div className="dashboard-grid">
                    <div className="panel">
                      <PanelTitle
                        title="Répartition des dossiers"
                        subtitle="Distribution réelle du dataset"
                      />

                      <DonutChart
                        normal={statistiques.dossiers_normaux}
                        anomalie={statistiques.anomalies}
                        total={statistiques.total_dossiers}
                      />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="Performance des modèles"
                        subtitle="Comparaison des scores F1"
                      />

                      <MetricBar
                        name="Rules"
                        value={`${(valeurF1("regles") * 100).toFixed(2)}%`}
                        width={`${valeurF1("regles") * 100}%`}
                      />

                      <MetricBar
                        name="Isolation Forest"
                        value={`${(valeurF1("Isolation Forest") * 100).toFixed(2)}%`}
                        width={`${valeurF1("Isolation Forest") * 100}%`}
                      />

                      <MetricBar
                        name="LOF"
                        value={`${(valeurF1("LOF") * 100).toFixed(2)}%`}
                        width={`${valeurF1("LOF") * 100}%`}
                      />

                      <div className="insight">
                        ✦ Meilleur modèle selon le F1-score :{" "}
                        {meilleurModele}
                      </div>
                    </div>
                  </div>

                  <div className="panel table-panel">
                    <PanelTitle
                      title="Dossiers récents"
                      subtitle="Données chargées depuis le fichier CSV"
                    />

                    <DossierTable data={filtered.slice(0, 5)} />

                    <button
                      className="text-btn"
                      onClick={() =>
                        goTo("Dossiers administratifs")
                      }
                    >
                      Voir tous les dossiers →
                    </button>
                  </div>
                </>
              )}

              {/* DOSSIERS ADMINISTRATIFS */}
              {active === "Dossiers administratifs" && (
                <section className="page-view">
                  <PageIntro
                    eyebrow="GESTION DES DONNÉES"
                    title="Dossiers administratifs"
                    description="Consultez et recherchez les dossiers administratifs."
                  />

                  <div className="stats-grid compact">
                    <Stat
                      title="Dossiers affichés"
                      value={filtered.length}
                      detail="Résultats du filtre"
                      icon="▤"
                    />

                    <Stat
                      title="Normaux"
                      value={statistiques.dossiers_normaux}
                      detail="Dans le dataset"
                      icon="✓"
                    />

                    <Stat
                      title="Anomalies réelles"
                      value={statistiques.anomalies}
                      detail="Dans le dataset"
                      icon="⚠"
                    />
                  </div>

                  <div className="panel table-panel">
                    <PanelTitle
                      title="Liste des dossiers"
                      subtitle="Utilisez la recherche en haut de la page"
                    />

                    <DossierTable data={filtered} />

                    {filtered.length === 0 && (
                      <p className="empty-state">
                        Aucun dossier ne correspond à votre recherche.
                      </p>
                    )}
                  </div>
                </section>
              )}

              {/* DETECTION */}
              {active === "Détection anomalies" && (
                <section className="page-view">
                  <PageIntro
                    eyebrow="MACHINE LEARNING"
                    title="Détection des anomalies"
                    description="Comparaison des résultats des trois méthodes utilisées dans le projet."
                  />

                  <div className="model-grid">
                    <ModelCard
                      name="Rules"
                      score={valeurF1("regles")}
                      precision={comparaison.regles?.precision}
                      recall={comparaison.regles?.rappel}
                      accuracy={comparaison.regles?.accuracy}
                      anomalies={modeles.Regles}
                      best={meilleurModele === "regles"}
                    />

                    <ModelCard
                      name="Isolation Forest"
                      score={valeurF1("Isolation Forest")}
                      precision={comparaison["Isolation Forest"]?.precision}
                      recall={comparaison["Isolation Forest"]?.rappel}
                      accuracy={comparaison["Isolation Forest"]?.accuracy}
                      anomalies={modeles["Isolation Forest"]}
                      best={meilleurModele === "Isolation Forest"}
                    />

                    <ModelCard
                      name="Local Outlier Factor"
                      score={valeurF1("LOF")}
                      precision={comparaison.LOF?.precision}
                      recall={comparaison.LOF?.rappel}
                      accuracy={comparaison.LOF?.accuracy}
                      anomalies={modeles.LOF}
                      best={meilleurModele === "LOF"}
                    />
                  </div>

                  <div className="panel explanation">
                    <h3>Comment fonctionne la détection ?</h3>

                    <p>
                      <strong>Rules :</strong> identifie les dossiers
                      qui respectent les conditions définies dans les
                      règles de détection.
                    </p>

                    <p>
                      <strong>Isolation Forest :</strong> identifie les
                      observations difficiles à isoler par rapport
                      aux autres données.
                    </p>

                    <p>
                      <strong>LOF :</strong> compare la densité locale
                      d'un dossier avec celle de ses voisins pour
                      repérer les valeurs inhabituelles.
                    </p>

                    <div className="insight">
                      Meilleur modèle selon le F1-score :{" "}
                      <strong>{meilleurModele}</strong>. Les performances
                      restent modestes et nécessitent une amélioration.
                    </div>
                  </div>

                  <div className="panel explanation">
                    <h3>Analyse des erreurs – LOF</h3>

                    {erreurs && (
                      <>
                        <p>
                          Faux positifs :{" "}
                          <strong>{erreurs.nombre_faux_positifs}</strong>
                        </p>
                        <p>
                          Faux négatifs :{" "}
                          <strong>{erreurs.nombre_faux_negatifs}</strong>
                        </p>
                      </>
                    )}
                  </div>

                  <div className="panel table-panel">
                    <PanelTitle
                      title="Dossiers suspects"
                      subtitle="Dossiers signalés par au moins une méthode"
                    />
                    <DossierTable
                      data={suspects.map((d) => ({
                        ...d,
                        id: d.id_dossier,
                        type: d.type_dossier,
                        region: d.region,
                        age: d.age_demandeur,
                        montant: d.montant_demande,
                        statut:
                          Number(d.anomalie_reelle) === 1
                            ? "Anomalie"
                            : "À vérifier",
                      }))}
                    />
                  </div>
                </section>
              )}

              {/* VISUALISATIONS */}
              {active === "Visualisations" && (
                <section className="page-view">
                  <PageIntro
                    eyebrow="DATA ANALYTICS"
                    title="Visualisations"
                    description="Analyse graphique du dataset et des résultats de détection."
                  />

                  <div className="stats-grid">
                    <Stat
                      title="Total"
                      value={statistiques.total_dossiers}
                      detail="Dossiers"
                      icon="▤"
                    />
                    <Stat
                      title="Normaux"
                      value={statistiques.dossiers_normaux}
                      detail="Dossiers normaux"
                      icon="✓"
                    />
                    <Stat
                      title="Anomalies"
                      value={statistiques.anomalies}
                      detail="Anomalies réelles"
                      icon="⚠"
                    />
                    <Stat
                      title="Taux d'anomalies"
                      value={`${statistiques.taux_anomalies}%`}
                      detail="Dans le dataset"
                      icon="◈"
                    />
                  </div>

                  <div className="dashboard-grid">
                    <div className="panel">
                      <PanelTitle
                        title="1. Répartition des dossiers"
                        subtitle="Normaux et anomalies réelles"
                      />
                      <DonutChart
                        normal={statistiques.dossiers_normaux}
                        anomalie={statistiques.anomalies}
                        total={statistiques.total_dossiers}
                      />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="2. Distribution des âges"
                        subtitle="Répartition par tranche d'âge"
                      />
                      <BarChart data={repartitionAges} />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="3. Distribution des montants"
                        subtitle="Montant demandé par tranche"
                      />
                      <BarChart data={repartitionMontants} />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="4. Dossiers par région"
                        subtitle="Répartition géographique"
                      />
                      <BarChart data={repartitionRegions} />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="5. Dossiers par type"
                        subtitle="Répartition selon le type de dossier"
                      />
                      <BarChart data={repartitionTypes} />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="6. Comparaison des méthodes"
                        subtitle="Nombre d'anomalies détectées"
                      />
                      <BarChart
                        data={[
                          {
                            label: "Rules",
                            value: modeles.Regles ?? 0,
                          },
                          {
                            label: "Isolation Forest",
                            value: modeles["Isolation Forest"] ?? 0,
                          },
                          {
                            label: "LOF",
                            value: modeles.LOF ?? 0,
                          },
                        ]}
                      />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="7. Comparaison F1-score"
                        subtitle="Performance des méthodes"
                      />
                      <BarChart
                        data={[
                          {
                            label: "Rules",
                            value: valeurF1("regles"),
                          },
                          {
                            label: "Isolation Forest",
                            value: valeurF1("Isolation Forest"),
                          },
                          {
                            label: "LOF",
                            value: valeurF1("LOF"),
                          },
                        ]}
                        percent
                      />
                    </div>

                    <div className="panel">
                      <PanelTitle
                        title="8. Matrice de confusion – LOF"
                        subtitle="Résultats par rapport aux anomalies réelles"
                      />
                      <ConfusionMatrix
                        metrics={comparaison.LOF}
                      />
                    </div>
                  </div>

                  <div className="panel explanation">
                    <h3>Interprétation</h3>
                    <p>
                      Le dataset contient{" "}
                      <strong>{statistiques.dossiers_normaux}</strong>{" "}
                      dossiers normaux et{" "}
                      <strong>{statistiques.anomalies}</strong>{" "}
                      anomalies réelles.
                    </p>
                    <p>
                      Le meilleur F1-score est obtenu par{" "}
                      <strong>{meilleurModele}</strong>.
                    </p>
                    <p>
                      Une valeur statistiquement atypique n'est pas
                      automatiquement une erreur ou une fraude.
                      Chaque dossier suspect doit être examiné.
                    </p>
                  </div>
                </section>
              )}

              {/* RAPPORTS */}
              {active === "Rapports" && (
                <section className="page-view">
                  <PageIntro
                    eyebrow="RÉSULTATS FINAUX"
                    title="Rapports"
                    description="Synthèse dynamique de l'évaluation du projet."
                  />

                  <div className="stats-grid">
                    <Stat
                      title="Dataset"
                      value={statistiques.total_dossiers}
                      detail="Observations"
                      icon="▤"
                    />

                    <Stat
                      title="Anomalies réelles"
                      value={statistiques.anomalies}
                      detail={`${statistiques.taux_anomalies}% du total`}
                      icon="⚠"
                    />

                    <Stat
                      title="Meilleur modèle"
                      value={meilleurModele || "N/A"}
                      detail="Selon le F1-score"
                      icon="✧"
                    />

                    <Stat
                      title="F1-score LOF"
                      value={(valeurF1("LOF")).toFixed(4)}
                      detail="Performance mesurée"
                      icon="◈"
                    />
                  </div>

                  <div className="panel explanation">
                    <h3>1. Présentation du dataset</h3>
                    <p>
                      Le dataset contient {statistiques.total_dossiers}{" "}
                      dossiers administratifs fictifs. Parmi eux,{" "}
                      {statistiques.dossiers_normaux} sont normaux et{" "}
                      {statistiques.anomalies} présentent une anomalie
                      connue.
                    </p>

                    <h3>2. Méthodes utilisées</h3>
                    <p>
                      Trois approches ont été évaluées : les règles
                      de détection, Isolation Forest et Local Outlier
                      Factor (LOF).
                    </p>

                    <h3>3. Comparaison des performances</h3>
                    <p>
                      Rules : F1-score de{" "}
                      {(valeurF1("regles")).toFixed(4)}.
                    </p>
                    <p>
                      Isolation Forest : F1-score de{" "}
                      {(valeurF1("Isolation Forest")).toFixed(4)}.
                    </p>
                    <p>
                      LOF : F1-score de{" "}
                      {(valeurF1("LOF")).toFixed(4)}.
                    </p>

                    <h3>4. Analyse des erreurs de LOF</h3>
                    <p>
                      Faux positifs :{" "}
                      {erreurs?.nombre_faux_positifs ?? "N/A"}.
                    </p>
                    <p>
                      Faux négatifs :{" "}
                      {erreurs?.nombre_faux_negatifs ?? "N/A"}.
                    </p>

                    <h3>5. Conclusion générale</h3>
                    <p>
                      Selon les résultats calculés sur le dataset,
                      le meilleur modèle est {meilleurModele}, avec
                      un F1-score de{" "}
                      {(valeurF1(meilleurModele)).toFixed(4)}.
                      Ces résultats montrent que la détection des
                      anomalies peut être améliorée.
                    </p>

                    <div className="report-note">
                      Rapport basé sur un dataset synthétique de
                      démonstration. Une anomalie détectée ne constitue
                      pas automatiquement une preuve d'erreur ou de fraude.
                    </div>
                  </div>
                </section>
              )}

              {/* ASSISTANT IA */}
              {active === "Assistant IA" && (
                <section className="page-view">
                  <PageIntro
                    eyebrow="NEXORA INTELLIGENCE"
                    title="Assistant IA"
                    description="Espace de discussion — mode démonstration."
                  />

                  <div className="chat-panel">
                    <div className="chat-header">
                      <div className="ai-avatar">✧</div>
                      <div>
                        <strong>NEXORA Assistant</strong>
                        <small>
                          Mode démonstration · API IA non connectée
                        </small>
                      </div>
                    </div>

                    <div className="chat-messages">
                      {messages.map((m, i) => (
                        <div
                          key={i}
                          className={`message ${m.from}`}
                        >
                          {m.text}
                        </div>
                      ))}
                    </div>

                    <form
                      className="chat-input"
                      onSubmit={(e) => {
                        e.preventDefault();
                        sendMessage();
                      }}
                    >
                      <input
                        value={question}
                        onChange={(e) =>
                          setQuestion(e.target.value)
                        }
                        placeholder="Écrivez votre question..."
                      />

                      <button type="submit">
                        Envoyer →
                      </button>
                    </form>

                    <p className="chat-disclaimer">
                      L'assistant est actuellement une maquette.
                      Il ne communique pas encore avec un modèle IA.
                    </p>
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

// FONCTIONS DE CALCUL DES GRAPHIQUES

function compterParCategorie(data, key) {
  const resultats = {};

  data.forEach((item) => {
    const valeur = item[key] || "Non précisé";
    resultats[valeur] = (resultats[valeur] || 0) + 1;
  });

  return Object.entries(resultats)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value);
}

function compterParTranches(data, key, tranches) {
  return tranches.map((tranche) => {
    const value = data.filter((item) => {
      const nombre = Number(item[key]);

      return (
        Number.isFinite(nombre) &&
        nombre >= tranche.min &&
        nombre < tranche.max
      );
    }).length;

    return {
      label: tranche.label,
      value,
    };
  });
}

// COMPOSANTS

function Stat({ title, value, detail, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <b>{icon}</b>
      </div>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function PanelTitle({ title, subtitle }) {
  return (
    <div className="panel-title">
      <div>
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </div>
      <span className="panel-decoration">✦</span>
    </div>
  );
}

function MetricBar({ name, value, width }) {
  return (
    <div className="metric-row">
      <div className="metric-label">
        <span>{name}</span>
        <strong>{value}</strong>
      </div>
      <div className="metric-track">
        <div style={{ width }} />
      </div>
    </div>
  );
}

function PageIntro({ eyebrow, title, description }) {
  return (
    <div className="page-intro">
      <span className="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  );
}

function ModelCard({
  name,
  score = 0,
  precision = 0,
  recall = 0,
  accuracy = 0,
  anomalies = 0,
  best,
}) {
  return (
    <div className="panel model-card">
      {best && <span className="best-tag">MEILLEUR F1</span>}

      <span className="eyebrow">MODÈLE DE DÉTECTION</span>
      <h2>{name}</h2>

      <div className="model-score">
        {Number(score).toFixed(4)}
        <small>F1-score</small>
      </div>

      <div className="model-details">
        <p>
          Anomalies détectées <strong>{anomalies ?? 0}</strong>
        </p>
        <p>
          Accuracy <strong>{Number(accuracy).toFixed(4)}</strong>
        </p>
        <p>
          Precision <strong>{Number(precision).toFixed(4)}</strong>
        </p>
        <p>
          Recall <strong>{Number(recall).toFixed(4)}</strong>
        </p>
      </div>
    </div>
  );
}

function DossierTable({ data }) {
  const [selected, setSelected] = useState(null);

  const getMethods = (d) => {
    const methods = [];

    if (Number(d.anomalie_regles) === 1) methods.push("Rules");
    if (Number(d.anomalie_IF) === 1) methods.push("Isolation Forest");
    if (Number(d.anomalie_LOF) === 1) methods.push("LOF");

    return methods;
  };

  return (
    <div>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID DOSSIER</th>
              <th>TYPE</th>
              <th>RÉGION</th>
              <th>ÂGE</th>
              <th>MONTANT</th>
              <th>STATUT</th>
            </tr>
          </thead>

          <tbody>
            {data.map((d) => (
              <tr
                key={d.id || d.id_dossier}
                onClick={() => setSelected(d)}
                style={{
                  cursor: "pointer",
                  background:
                    selected?.id === d.id ? "#eef2ff" : undefined,
                }}
              >
                <td>{d.id || d.id_dossier}</td>
                <td>{d.type || d.type_dossier || "N/A"}</td>
                <td>{d.region || "N/A"}</td>
                <td>{d.age ?? d.age_demandeur ?? "N/A"}</td>
                <td>
                  {Number(
                    d.montant ?? d.montant_demande ?? 0
                  ).toLocaleString("fr-FR")}{" "}
                  DT
                </td>
                <td>
                  <span
                    className={`status ${
                      d.statut === "Anomalie" ||
                      d.statut === "À vérifier"
                        ? "danger"
                        : "normal"
                    }`}
                  >
                    {d.statut || "Non défini"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="panel" style={{ marginTop: "20px", padding: "20px" }}>
          <h3>Détails du dossier : {selected.id || selected.id_dossier}</h3>

          <p>
            <strong>Méthodes de détection :</strong>{" "}
            {getMethods(selected).join(", ") || "Aucune"}
          </p>

          <p>
            <strong>Âge :</strong>{" "}
            {selected.age_demandeur ?? "N/A"}
          </p>

          <p>
            <strong>Montant demandé :</strong>{" "}
            {selected.montant_demande ?? "N/A"} DT
          </p>

          <p>
            <strong>Revenu mensuel :</strong>{" "}
            {selected.revenu_mensuel ?? "N/A"} DT
          </p>

          <p>
            <strong>Nombre de documents :</strong>{" "}
            {selected.nb_documents ?? "N/A"}
          </p>

          <p>
            <strong>Délai de traitement :</strong>{" "}
            {selected.delai_traitement_jours ?? "N/A"} jours
          </p>

          <p>
            <strong>Nombre d'erreurs :</strong>{" "}
            {selected.nb_erreurs ?? "N/A"}
          </p>

          <p>
            <strong>Raison des règles :</strong>{" "}
            {Number(selected.anomalie_regles) === 1
              ? selected.raisons_regles || "Non précisée"
              : "Aucune anomalie détectée par les règles"}
          </p>

          <p>
            <strong>Anomalie réelle :</strong>{" "}
            {Number(selected.anomalie_reelle) === 1 ? "Oui" : "Non"}
          </p>

          <button onClick={() => setSelected(null)}>
            Fermer les détails
          </button>
        </div>
      )}
    </div>
  );
}


// GRAPHIQUE CIRCULAIRE

function DonutChart({ normal, anomalie, total }) {
  const pourcentage =
    total > 0 ? (normal / total) * 100 : 0;

  return (
    <div className="donut-area">
      <div
        className="donut"
        style={{
          background: `conic-gradient(#b79ae8 0 ${pourcentage}%, #e8a4c7 ${pourcentage}% 100%)`,
        }}
      >
        <div>
          <strong>{total}</strong>
          <small>Total</small>
        </div>
      </div>

      <div className="legend">
        <p>
          <i className="legend-normal" />
          Dossiers normaux
          <strong>{normal}</strong>
        </p>
        <p>
          <i className="legend-anomaly" />
          Anomalies réelles
          <strong>{anomalie}</strong>
        </p>
      </div>
    </div>
  );
}

// GRAPHIQUE EN BARRES

function BarChart({ data, percent = false }) {
  const maximum = Math.max(
    ...data.map((item) => Number(item.value) || 0),
    1
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 17 }}>
      {data.map((item, index) => {
        const valeur = Number(item.value) || 0;
        const largeur = (valeur / maximum) * 100;

        return (
          <div key={`${item.label}-${index}`}>
            <div className="metric-label">
              <span>{item.label}</span>
              <strong>
                {percent
                  ? `${(valeur * 100).toFixed(2)}%`
                  : valeur}
              </strong>
            </div>

            <div className="metric-track">
              <div
                style={{
                  width: `${largeur}%`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// MATRICE DE CONFUSION

function ConfusionMatrix({ metrics }) {
  if (!metrics) {
    return <p>Données indisponibles.</p>;
  }

  const cells = [
    { label: "Vrais négatifs (TN)", value: metrics.TN },
    { label: "Faux positifs (FP)", value: metrics.FP },
    { label: "Faux négatifs (FN)", value: metrics.FN },
    { label: "Vrais positifs (TP)", value: metrics.TP },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: 12,
      }}
    >
      {cells.map((cell) => (
        <div
          key={cell.label}
          style={{
            padding: 18,
            borderRadius: 12,
            background: "#faf6ff",
            border: "1px solid #eee8f5",
          }}
        >
          <small style={{ color: "#93899f" }}>
            {cell.label}
          </small>
          <h2 style={{ color: "#7954b1", marginTop: 8 }}>
            {cell.value}
          </h2>
        </div>
      ))}
    </div>
  );
}

export default App;